"""Verify rendered routes, internal links, images and SEO metadata."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json

ROOT = Path(__file__).resolve().parents[1] / 'dist'
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.h1=0; self.links=[]; self.sources=[]; self.title=False; self.description=False; self.canonical=False; self.form=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1':self.h1+=1
        if tag=='title':self.title=True
        if tag=='form':self.form=True
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag in ['img','script'] and 'src' in a:self.sources.append(a['src'])
        if tag=='meta' and a.get('name')=='description':self.description=bool(a.get('content'))
        if tag=='link' and a.get('rel')=='canonical':self.canonical=True

errors=[]
routes=json.loads((ROOT/'routes.json').read_text())
assert len(routes)==29
for route in routes:
    target=ROOT/route.lstrip('/')/'index.html'
    p=Page();p.feed(target.read_text())
    if p.h1!=1:errors.append(f'{route}: expected one H1, got {p.h1}')
    if not(p.title and p.description and p.canonical):errors.append(f'{route}: missing metadata')
    if p.form:errors.append(f'{route}: commercial form is not authorized')
    for url in p.links+p.sources:
        if url.startswith('/'):
            path=unquote(urlsplit(url).path); local=ROOT/path.lstrip('/')
            if path.endswith('/'):local/= 'index.html'
            if not local.is_file():errors.append(f'{route}: broken target {url}')
        if url.startswith('https://wa.me/') and not url.startswith('https://wa.me/51942722449?text='):
            errors.append(f'{route}: incorrect WhatsApp contact')
if errors:raise SystemExit('\n'.join(errors))
print('PASS: 29 routes, internal links, assets, H1, metadata and WhatsApp contact; no forms.')
