"""Prepare a minimal, reference-checked payload before any hosting connection."""
from collections import defaultdict
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for name in ('src', 'href', 'poster', 'xlink:href'):
            if attrs.get(name):
                self.urls.append(attrs[name])
        if tag == 'meta' and attrs.get('property') in ('og:image', 'og:url'):
            self.urls.append(attrs.get('content', ''))
        if attrs.get('style'):
            self.urls.extend(css_urls(attrs['style']))
        if attrs.get('srcset'):
            self.urls.extend(part.strip().split()[0] for part in attrs['srcset'].split(',') if part.strip())


def css_urls(text):
    return re.findall(r'url\(\s*[\"\']?([^\s\)\"\']+)', text) + re.findall(
        r'@import\s+[\"\']([^\"\']+)', text)


def prepare_release():
    source = ROOT / 'dist'
    output = ROOT / 'release'
    hosting = json.loads((source / 'hosting.json').read_text())
    if hosting['base_path'] or hosting['site_url'] != 'https://www.igraphito.com':
        raise RuntimeError('Production payload must use https://www.igraphito.com without a preview base path')
    routes = json.loads((source / 'routes.json').read_text())
    selected = {route.lstrip('/') + 'index.html' for route in routes}
    selected.update({'404.html', '.htaccess', 'robots.txt', 'sitemap.xml',
                     'googled4596d5466e1d60a.html', 'BingSiteAuth.xml'})
    queue = list(selected)
    checked = set()
    origin = hosting['site_url']
    while queue:
        name = queue.pop()
        if name in checked:
            continue
        checked.add(name)
        file = source / name
        if not file.is_file() or not file.resolve().is_relative_to(source.resolve()):
            raise RuntimeError('Missing or unsafe release reference: ' + name)
        urls = []
        if file.suffix in {'.html', '.svg'}:
            text = file.read_text()
            parser = References()
            parser.feed(text)
            urls += parser.urls
            urls += css_urls(text)
            urls += re.findall(r'"contentUrl"\s*:\s*"([^\"]+)"', text)
        elif file.suffix == '.css':
            urls += css_urls(file.read_text())
        elif file.suffix == '.xml':
            urls += re.findall(r'<loc>([^<]+)</loc>', file.read_text())
        elif file.suffix == '.js':
            # Keep explicit local asset dependencies if scripts introduce them.
            urls += re.findall(r'[\"\'](/assets/[^\"\']+)[\"\']', file.read_text())
        for value in urls:
            url = urlsplit(urljoin(origin + '/' + name, value))
            if url.scheme not in {'http', 'https'} or url.netloc != urlsplit(origin).netloc:
                continue
            target = unquote(url.path).lstrip('/')
            if not target or target.endswith('/'):
                target += 'index.html'
            path = source / target
            if not path.is_file():
                raise RuntimeError(f'Broken release reference from {name}: {value}')
            if target not in selected:
                selected.add(target)
                queue.append(target)

    hashes = defaultdict(list)
    manifest = []
    for name in sorted(selected):
        data = (source / name).read_bytes()
        digest = sha256(data).hexdigest()
        hashes[digest].append(name)
        manifest.append({'path': name, 'bytes': len(data), 'sha256': digest})
    duplicates = [names for names in hashes.values() if len(names) > 1]
    if duplicates:
        raise RuntimeError('Identical files in release payload: ' + json.dumps(duplicates))
    folded = [name.casefold() for name in selected]
    if len(set(folded)) != len(folded):
        raise RuntimeError('Case-insensitive path collision in release payload')
    if output.exists():
        shutil.rmtree(output)
    for name in sorted(selected):
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    all_files = [p for p in source.rglob('*') if p.is_file()]
    excluded = sorted(p.relative_to(source).as_posix() for p in all_files
                      if p.relative_to(source).as_posix() not in selected)
    report = {'files': manifest, 'excluded': excluded, 'duplicate_groups': duplicates,
              'total_bytes': sum(item['bytes'] for item in manifest)}
    (ROOT / 'release-manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS release: {len(selected)} files, {report["total_bytes"]} bytes; '
          f'{len(excluded)} excluded; no identical duplicates or broken local references.')
    return output


if __name__ == '__main__':
    prepare_release()
