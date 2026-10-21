"""Manual FTPS deployment. Backups remain on hosting, outside the web root."""
import ftplib
import os
from pathlib import Path
import ssl
import socket
import tempfile
from datetime import datetime, timezone
import zipfile


def main():
    password = os.environ.get('FTP_PASSWORD')
    if not password:
        raise SystemExit('Missing FTP_PASSWORD repository secret')
    ftp = ftplib.FTP_TLS(context=ssl.create_default_context(), timeout=90)
    try:
        host = 'nemesis.sipanserver.com'
        if not (set(socket.gethostbyname_ex(host)[2]) & set(socket.gethostbyname_ex('ftp.igraphito.com')[2])):
            raise RuntimeError('Hosting hostname does not match the supplied FTP server')
        ftp.connect(host, 21)
        ftp.login('igraphito', password)
        ftp.prot_p()
        root = ftp.pwd()
        ftp.cwd('public_html')
        webroot = ftp.pwd()
        if root == webroot:
            raise RuntimeError('Cannot establish a separate backup location')
        entries = list(ftp.mlsd())
        if not any(n in {'index.php', 'index.html', 'index.htm'} for n, _ in entries):
            raise RuntimeError('public_html does not contain a recognized existing homepage')
        print('FTPS connection and public_html verified.')
        if os.environ.get('DEPLOY_MODE') != 'publish':
            print('Connection check complete; no hosting files changed.')
            return

        def download_tree(remote, local):
            local.mkdir(parents=True, exist_ok=True)
            for name, facts in ftp.mlsd(remote):
                if facts.get('type') in {'cdir', 'pdir'}:
                    continue
                if name in {'.', '..'} or '/' in name or '\\' in name:
                    raise RuntimeError('Unsafe entry in remote listing')
                target = local / name
                source = remote.rstrip('/') + '/' + name
                if facts.get('type') == 'dir':
                    download_tree(source, target)
                elif facts.get('type') == 'file':
                    with target.open('wb') as output:
                        ftp.retrbinary('RETR ' + source, output.write)
                    if 'size' in facts and target.stat().st_size != int(facts['size']):
                        raise RuntimeError('Incomplete backup download')
                else:
                    raise RuntimeError('Unsupported remote entry; backup must be complete')

        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            download_tree(webroot, temp / 'public_html')
            archive = temp / ('public_html-' + stamp + '.zip')
            with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as backup:
                for file in (temp / 'public_html').rglob('*'):
                    if file.is_file():
                        backup.write(file, file.relative_to(temp))
            ftp.cwd(root)
            backup_dir = 'igraphito-private-backups'
            try:
                ftp.mkd(backup_dir)
            except ftplib.error_perm:
                ftp.cwd(backup_dir)
                ftp.cwd(root)
            ftp.cwd(backup_dir)
            with archive.open('rb') as source:
                ftp.storbinary('STOR ' + archive.name, source)
            ftp.voidcmd('TYPE I')
            if ftp.size(archive.name) != archive.stat().st_size:
                raise RuntimeError('Remote backup size mismatch; deployment aborted')
            print('Backup saved outside public_html: ' + archive.name)
        ftp.cwd(webroot)
        dist = Path('dist')
        files = sorted(p for p in dist.rglob('*') if p.is_file())
        # Upload assets and inner pages first; activate the homepage last.
        files.sort(key=lambda p: (p.relative_to(dist).as_posix() in {'index.html', '.htaccess'}, p.relative_to(dist).as_posix() == '.htaccess'))
        for file in files:
            relative = file.relative_to(dist)
            ftp.cwd(webroot)
            for part in relative.parts[:-1]:
                try:
                    ftp.mkd(part)
                except ftplib.error_perm:
                    pass
                ftp.cwd(part)
            temporary = file.name + '.igraphito-upload'
            with file.open('rb') as source:
                ftp.storbinary('STOR ' + temporary, source)
            ftp.rename(temporary, file.name)
        print('Published successfully. Existing unrelated files were preserved.')
    finally:
        ftp.close()


if __name__ == '__main__':
    main()
