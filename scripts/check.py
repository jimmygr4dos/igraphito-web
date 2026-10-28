"""Verify rendered routes, internal links, images and SEO metadata."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, parse_qs
import json

ROOT = Path(__file__).resolve().parents[1] / 'dist'
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.h1=0; self.links=[]; self.sources=[]; self.title=False; self.description=False; self.canonical=False; self.form=False; self.whatsapp=[]; self.in_h1=False; self.heading=''
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1':self.h1+=1;self.in_h1=True
        if tag=='title':self.title=True
        if tag=='form':self.form=True
        if tag=='a' and 'href' in a:
            self.links.append(a['href'])
            if a['href'].startswith('https://wa.me/'):self.whatsapp.append(a)
        if tag in ['img','script'] and 'src' in a:self.sources.append(a['src'])
        if tag=='meta' and a.get('name')=='description':self.description=bool(a.get('content'))
        if tag=='link' and a.get('rel')=='canonical':self.canonical=True

    def handle_data(self,data):
        if self.in_h1:self.heading+=data
    def handle_endtag(self,tag):
        if tag=='h1':self.in_h1=False

errors=[]
personalized=0

routes=json.loads((ROOT/'routes.json').read_text())
base_path=json.loads((ROOT/'hosting.json').read_text())['base_path']
assert len(routes)==32
for route in routes:
    target=ROOT/route.lstrip('/')/'index.html'
    p=Page();p.feed(target.read_text())
    if route.startswith('/productos/') and route!='/productos/':
        if len(p.whatsapp)!=6:errors.append(f'{route}: expected six product WhatsApp links')
        for a in p.whatsapp:
            message=parse_qs(urlsplit(a['href']).query).get('text',[''])[0]
            expected=f'Hola, quisiera cotizar {p.heading.lower()} para mi empresa.'
            if message!=expected:errors.append(f'{route}: generic or wrong product message ({a.get("data-cta")})')
            if a.get('data-product')!=p.heading:errors.append(f'{route}: wrong product tracking context')
            personalized+=1
    if p.h1!=1:errors.append(f'{route}: expected one H1, got {p.h1}')
    if not(p.title and p.description and p.canonical):errors.append(f'{route}: missing metadata')
    if p.form:errors.append(f'{route}: commercial form is not authorized')
    for a in p.whatsapp:
        message=parse_qs(urlsplit(a['href']).query).get('text',[''])[0]
        if 'http' in message or 'Vi esta página:' in message:errors.append(f'{route}: URL exposed in WhatsApp message')
    for url in p.links+p.sources:
        if url.startswith('/'):
            path=unquote(urlsplit(url).path)
            if base_path:
                if not path.startswith(base_path+'/'):
                    errors.append(f'{route}: target outside hosting path {url}')
                    continue
                path=path[len(base_path):]
            local=ROOT/path.lstrip('/')
            if path.endswith('/'):local/= 'index.html'
            if not local.is_file():errors.append(f'{route}: broken target {url}')
        if url.startswith('https://wa.me/') and not url.startswith('https://wa.me/51942722449?text='):
            errors.append(f'{route}: incorrect WhatsApp contact')
    if 'Nota interna:' in target.read_text():errors.append(f'{route}: editorial note exposed')
for verification in ['googled4596d5466e1d60a.html','BingSiteAuth.xml']:
    if (ROOT/verification).read_bytes() != (ROOT.parent/'assets'/verification).read_bytes():
        errors.append(f'Verification file altered: {verification}')
final_images=list((ROOT/'assets/images/final').glob('*.webp'))
if len(final_images)!=22:errors.append(f'Expected 22 final image assets, got {len(final_images)}')
if errors:raise SystemExit('\n'.join(errors))
assert personalized==126, personalized
print('PASS: 126 WhatsApp links personalized across all 21 products.')
print('PASS: 32 routes, 22 final images, internal links, assets, H1, metadata, original verification files and WhatsApp contact; no forms or editorial notes.')
