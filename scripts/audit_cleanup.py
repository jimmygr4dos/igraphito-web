"""Read-only hosting audit; never rename, delete, or upload remote files."""
import ftplib
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import ssl
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
from prepare_release import prepare_release, ROOT


def main():
    prepare_release()
    manifest = json.loads((ROOT / 'release-manifest.json').read_text())
    candidates = [p for p in manifest['excluded'] if p.startswith('assets/')]
    expected_hashes = {}
    for item in manifest['files']:
        expected_hashes.setdefault(item['sha256'], []).append(item['path'])
    host = 'nemesis.sipanserver.com'
    assert set(socket.gethostbyname_ex(host)[2]) & set(socket.gethostbyname_ex('igraphito.com')[2])
    ftp = ftplib.FTP_TLS(context=ssl.create_default_context(), timeout=90)
    try:
        ftp.connect('igraphito.com', 21)
        ftp.host = host
        ftp.login('igraphito@igraphito.com', os.environ['FTP_PASSWORD'])
        ftp.prot_p()
        ftp.cwd('public_html')
        base = ftp.pwd().rstrip('/')
        files = {}

        def scan(remote, prefix=''):
            for name, facts in ftp.mlsd(remote):
                kind = facts.get('type')
                if kind in {'cdir', 'pdir'}:
                    continue
                assert name not in {'.', '..'} and '/' not in name and '\\' not in name
                relative = prefix + name
                if kind == 'dir':
                    scan(remote + '/' + name, relative + '/')
                elif kind == 'file':
                    files[relative] = int(facts.get('size', 0))
                else:
                    raise RuntimeError('Unsupported remote entry; audit incomplete')

        def read(path):
            output = io.BytesIO()
            ftp.retrbinary('RETR ' + base + '/' + path, output.write)
            data = output.getvalue()
            if len(data) != files[path]:
                raise RuntimeError('File changed or incomplete download: ' + path)
            return data

        scan(base)
        present = [p for p in candidates if p in files]
        hits = {p: [] for p in present}
        text_count = 0
        server_sources = []
        for path in files:
            suffix = Path(path).suffix.lower()
            if suffix in {'.php', '.cgi', '.asp', '.aspx'}:
                server_sources.append(path)
            if suffix not in {'.html', '.htm', '.css', '.js', '.json', '.xml', '.txt', '.svg', '.php', '.cgi', '.asp', '.aspx'} and Path(path).name != '.htaccess':
                continue
            # Content remains in memory; reports contain paths and counts only.
            text = unquote(read(path).decode('utf-8', errors='replace'))
            text_count += 1
            for candidate in present:
                if candidate in text or Path(candidate).name in text:
                    hits[candidate].append(path)

        results = []
        for candidate in present:
            digest = hashlib.sha256(read(candidate)).hexdigest()
            identical_to = []
            for retained in expected_hashes.get(digest, []):
                if retained in files and hashlib.sha256(read(retained)).hexdigest() == digest:
                    identical_to.append(retained)
            results.append({'path': candidate, 'bytes': files[candidate], 'sha256': digest,
                            'references': hits[candidate], 'identical_to_retained_remote': identical_to})
        sitemap = ET.fromstring(read('sitemap.xml'))
        routes = [urlsplit(e.text).path for e in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        assert routes and '/' in routes
        report = {'read_only': True, 'files_scanned': len(files), 'text_files_scanned': text_count,
                  'server_sources': server_sources, 'routes': routes, 'candidates': results,
                  'not_present': sorted(set(candidates) - set(present))}
        folder = ROOT / 'qa'
        folder.mkdir(exist_ok=True)
        (folder / 'cleanup-audit.json').write_text(json.dumps(report, indent=2))
        print(json.dumps({'read_only': True, 'text_files_scanned': text_count,
                          'candidates_present': len(results),
                          'referenced_candidates': sum(bool(x['references']) for x in results),
                          'exact_duplicates': sum(bool(x['identical_to_retained_remote']) for x in results),
                          'server_source_count': len(server_sources)}, indent=2))
    finally:
        ftp.close()


if __name__ == '__main__':
    main()
