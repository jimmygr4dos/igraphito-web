"""Check actual rendered metadata and structured navigation in each build."""
from pathlib import Path
from html.parser import HTMLParser
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]/'dist'
class Metadata(HTMLParser):
    def __init__(self):
        super().__init__();self.title='';self.meta={};self.canonical='';self.schema=[];self.reading=None;self.data=''
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='title':self.reading='title';self.data=''
        if tag=='script' and a.get('type')=='application/ld+json':self.reading='schema';self.data=''
        if tag=='meta':self.meta[a.get('name',a.get('property',''))]=a.get('content','')
        if tag=='link' and a.get('rel')=='canonical':self.canonical=a['href']
    def handle_data(self,data):
        if self.reading:self.data+=data
    def handle_endtag(self,tag):
        if tag=='title' and self.reading=='title':self.title=self.data;self.reading=None
        if tag=='script' and self.reading=='schema':self.schema.append(json.loads(self.data));self.reading=None
routes=json.loads((ROOT/'routes.json').read_text());base=json.loads((ROOT/'hosting.json').read_text())['site_url']
sitemap=[x.text for x in ET.parse(ROOT/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert set(sitemap)=={base+p for p in routes}
titles=set();descriptions=set();products=0
for route in routes:
    m=Metadata();m.feed((ROOT/route.lstrip('/')/'index.html').read_text())
    assert m.title and m.title not in titles, f'Duplicate title: {route}'
    assert m.meta['description'] and m.meta['description'] not in descriptions,f'Duplicate description: {route}'
    titles.add(m.title);descriptions.add(m.meta['description'])
    assert m.canonical==base+route,route
    assert 'noindex' in m.meta['robots'],route
    assert m.meta['og:url']==m.canonical,route
    assert m.schema[0]['url']==m.canonical,route
    if route.startswith('/productos/') and route!='/productos/':
        products+=1;schema=m.schema[0];crumbs=schema['breadcrumb']['itemListElement']
        assert [c['position'] for c in crumbs]==[1,2,3,4],route
        assert crumbs[-1]['item']==m.canonical,route
        assert schema['primaryImageOfPage']['contentUrl']==m.meta['og:image'],route
        assert m.meta['og:image'].endswith('.webp') and not m.meta['og:image'].endswith('/hero.webp'),route
assert products==20
assert 'Disallow: /' not in (ROOT/'robots.txt').read_text(), 'Crawler must reach noindex'
print('PASS SEO: 31 unique titles/descriptions, canonicals, sitemap, noindex; 20 product images and breadcrumb paths.')
