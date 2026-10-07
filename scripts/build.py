#!/usr/bin/env python3
"""Build all approved pages using only Python's standard library."""
from pathlib import Path
import re, html, shutil, json, argparse
from urllib.parse import quote
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.igraphito.com'
E = html.escape
CATEGORIES = [
 ('papeleria-corporativa','Papelería corporativa','folders.png',range(0,6)),
 ('cuadernos-y-agendas-corporativas','Cuadernos y agendas corporativas','cuadernos.png',range(6,9)),
 ('publicidad-corporativa','Publicidad corporativa','tripticos.jpg',range(9,12)),
 ('merchandising-empresarial','Merchandising empresarial','lapiceros.corporativos.jpg',range(12,14)),
 ('packaging-corporativo','Packaging corporativo','bolsas.papel.jpg',range(14,18)),
]
IMAGES = ['tarjetas-de-presentacion-corporativas.webp','folders-corporativos.webp','hojas-membretadas.webp','formatos-continuos.webp','fotochecks-corporativos.webp','sellos-para-empresas.webp','cuadernos-corporativos.webp','agendas-corporativas.webp','calendarios-corporativos.webp','flyers-y-volantes.webp','dipticos.webp','tripticos.webp','lapiceros-corporativos.webp','tazas-corporativas.webp','bolsas-personalizadas-para-empresas.webp','cajas-personalizadas-para-empresas.webp','etiquetas-adhesivas.webp','hangtags.webp']
for i, representative in enumerate([1,6,11,12,14]):
    slug, name, _, indices = CATEGORIES[i]
    CATEGORIES[i] = (slug, name, IMAGES[representative], indices)
CONTACT_ICON = '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 11.5a9 9 0 0 1-13 8L3 21l1.5-5A9 9 0 1 1 21 11.5Z"/><path d="M8 7.5c-.8 4 3 7.7 7.1 8l1.3-2.4-2.8-1.3-1 1c-1.6-.7-2.6-1.8-3.2-3.2l1-1L9 6.7Z"/></svg>'
CLIENT_NAMES = ['Aranwa Hotels Resorts & Spas','Clasem','Esparq','Boyles Bros Diamantina','JRM','Terrazul','V&V Bravo Constructora','La Viga','Crepier','Controles Empresariales','Eureka Grupo Inmobiliario','iBR','ilko','Virutex','Koplast','Essentia','Montali S.A.','Movil Group','Movil Air','Synthec','Record','SoftwareOne','Colegio Lima Waldorf','Huayna Seguridad y Vigilancia']
STEP_PATHS = ['<path d="M9 5H5v16h14V5h-4M9 3h6v4H9ZM8 11h8M8 15h6"/>','<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="9" cy="6" r="2"/><circle cx="15" cy="12" r="2"/><circle cx="9" cy="18" r="2"/>','<path d="M5 3h10l4 4v14H5ZM14 3v5h5M8 12h8M8 16h5"/>','<path d="M6 9V3h12v6M6 17H3V9h18v8h-3M6 14h12v7H6Z"/>','<path d="M2 4h11v12H2ZM13 8h5l4 4v4h-9"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="18" r="2"/>']
def step_icon(index):
    return '<span class="step-icon"><svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">'+STEP_PATHS[index]+'</svg></span>'

def wa(label='Solicitar cotización', product=None, path='/', classes='button', cta='content'):
    text = f'Hola, quisiera cotizar {product} para mi empresa.' if product else 'Hola, quisiera cotizar un pedido empresarial con Graphito.'
    text += ' Vi esta página: ' + BASE + path
    return f'<a class="{classes}" aria-label="{E(label)}" data-product="{E(product or "general")}" data-cta="{cta}" href="https://wa.me/51942722449?text={quote(text)}">{CONTACT_ICON}<span>{E(label)}</span></a>'

def asset(image):
    return '/assets/images/final/' + image

def card(title, path, image, description='Consulta las características de tu pedido a medida.'):
    return f'<article class="product-card"><a class="card-image" href="{path}"><img src="{asset(image)}" alt="Imagen ilustrativa de {E(title.lower())}" loading="lazy" width="800" height="600"></a><div class="card-body"><h3><a href="{path}">{E(title)}</a></h3><p>{E(description)}</p><a class="text-link" aria-label="Conoce más sobre {E(title.lower())}" href="{path}">Conoce más <span aria-hidden="true">→</span></a></div></article>'

def section(title, body, extra=''):
    return f'<section class="section {extra}"><div class="container"><div class="section-heading"><h2>{E(title)}</h2></div>{body}</div></section>'

def category_cards():
    descriptions=['Tarjetas, folders y documentos para tu empresa.','Cuadernos, agendas y calendarios para trabajo y planificación.','Flyers, dípticos y trípticos para tus campañas.','Lapiceros y tazas con la identidad de tu marca.','Bolsas, cajas, adhesivos y hangtags para tus productos.']
    return '<div class="card-grid five">' + ''.join(card(n,'/'+s+'/',i,descriptions[j]) for j,(s,n,i,_) in enumerate(CATEGORIES)) + '</div>'

def product_cards(products, indices, variant=''):
    return f'<div class="card-grid {variant}">' + ''.join(card(products[i]['name'],products[i]['path'],IMAGES[i]) for i in indices) + '</div>'

def carousel():
    logos = ''.join(f'<div class="client-logo"><img src="/assets/images/clients/item{i}.jpg" alt="{E(CLIENT_NAMES[i-1])}" loading="lazy" width="563" height="396"></div>' for i in range(1,25))
    return '<div class="client-carousel" data-carousel role="region" aria-label="Empresas que confían en nosotros"><div class="carousel-track" role="group" tabindex="0" aria-label="Logotipos de clientes; desliza o usa las flechas para explorar">'+logos+'<'+ '/div><div class="carousel-controls"><button hidden data-carousel-prev aria-label="Clientes anteriores">←</button><button hidden data-carousel-toggle aria-pressed="false">Pausar</button><button hidden data-carousel-next aria-label="Clientes siguientes">→</button></div></div>'

def cta(path='/', product=None):
    return '<section class="cta-band"><div class="container"><div><h2>Hablemos de tu pedido empresarial</h2><p>Cuéntanos qué necesitas y cotizamos tu proyecto a medida.</p></div>'+wa('Conversemos por WhatsApp',product,path,cta='bottom')+'</div></section>'

def header(path):
    def link(p,n):
        current = ' aria-current="page"' if path == p else ''
        return f'<a href="{p}"{current}>{n}</a>'
    submenu = ''.join('<li>'+link('/'+s+'/',n)+'</li>' for s,n,_,_ in CATEGORIES)
    return '<a class="skip-link" href="#contenido">Saltar al contenido</a><header class="site-header"><div class="container"><a class="brand" href="/" aria-label="Impresiones Graphito, inicio"><img src="/assets/images/logo.png" alt="" width="70" height="70"><img src="/assets/images/wordmark.png" alt="Impresiones Graphito" width="188" height="29"></a><button class="nav-toggle" data-nav-toggle aria-controls="primary-nav" aria-expanded="false" aria-label="Abrir menú" hidden>☰</button><nav class="nav" id="primary-nav" aria-label="Navegación principal"><ul class="nav-links"><li>'+link('/','Inicio')+'</li><li><details class="nav-menu"><summary>Soluciones</summary><ul class="nav-submenu"><li>'+link('/productos/','Todos los productos')+'</li>'+submenu+'</ul></details></li><li>'+link('/impresion-offset-y-digital/','Impresión')+'</li><li>'+link('/nosotros/','Nosotros')+'</li><li>'+link('/contacto/','Contacto')+'</li></ul></nav><div class="header-contact"><a href="tel:+51942722449">942 722 449</a>'+wa(path=path,cta='header')+'</div></div></header>'

def footer(path):
    return '<footer class="site-footer"><div class="container"><div class="footer-grid"><div><a class="brand" href="/" aria-label="Impresiones Graphito, inicio"><img src="/assets/images/logo.png" alt="" width="54" height="54"><img src="/assets/images/wordmark.png" alt="Impresiones Graphito" width="156" height="24"></a><p>Tu marca, en cada impresión.<br>Soluciones gráficas para empresas en Lima.</p></div><div><h3>Soluciones</h3>'+''.join(f'<p><a href="/{s}/">{n}</a></p>' for s,n,_,_ in CATEGORIES)+'</div><div><h3>Conversemos</h3><p><a href="tel:+51942722449">942 722 449</a></p><p><a href="mailto:ventas@igraphito.com">ventas@igraphito.com</a></p>'+wa('Escríbenos por WhatsApp',path=path,cta='footer')+'</div><div><h3>Graphito</h3><p><a href="/nosotros/">Nosotros</a></p><p><a href="/contacto/">Contacto</a></p><p><a href="/privacidad/">Privacidad</a></p></div></div><div class="footer-bottom"><p>© Impresiones Graphito</p><a href="/productos/">Productos corporativos a demanda</a></div></div></footer>'+wa('WhatsApp',path=path,classes='whatsapp-float',cta='floating')

def hero(title, paragraph, path, image, compact=False):
    heading = 'Tu marca,<br><span>en cada impresión</span>' if path=='/' else E(title)
    return f'<section class="hero {"compact" if compact else ""}"><img class="hero-photo" src="{asset(image)}" alt="" width="1672" height="941" fetchpriority="high"><div class="hero-inner"><div class="hero-copy"><p class="eyebrow">SOLUCIONES GRÁFICAS PARA EMPRESAS EN LIMA</p><h1>{heading}</h1><p>{E(paragraph)}</p><div class="hero-actions">{wa(path=path)}<a class="button button-outline" href="/productos/">Ver soluciones</a></div></div></div></section>'

def inline(text):
    result = E(text)
    result = re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',result)
    result = result.replace('942 722 449', '<a href="tel:+51942722449">942 722 449</a>')
    result = result.replace('ventas@igraphito.com','<a href="mailto:ventas@igraphito.com">ventas@igraphito.com</a>')
    return result

def blocks(page, omit_intro=False, omit_heading=None):
    """Editorial labels become semantic headings; internal instructions are excluded."""
    body = re.sub(r'\n(?=\*\*[^*\n]+\*\*)', '\n\n', page['body'])
    lines = re.split(r'\n\s*\n', body)
    out=[]; faq=[]; question=None; first=True; skip_paragraph=False
    for raw in lines:
        raw = raw.strip()
        if not raw or raw.startswith('Nota interna:'): continue
        raw = raw.split(' Nota interna:')[0]
        if raw.startswith('**Title:') or raw.startswith('**Descripción SEO:'): continue
        m=re.fullmatch(r'\*\*(.*?)\*\*(?: — (.*))?',raw)
        if m:
            label, target = m.groups()
            if label.startswith('¿'):
                question = label
                continue
            if label == 'Conversemos por WhatsApp' and not target:
                out.append(f'<h2>{E(label)}</h2>')
            elif 'WhatsApp' in label or target == 'WhatsApp':
                product = page['name'] if 3 <= page['number'] <= 7 or 9 <= page['number'] <= 26 else None
                out.append(wa(label,product,page['path']))
            elif target and target.startswith('/'):
                out.append(f'<p><a class="text-link" href="{E(target)}">{E(label)}</a></p>')
            elif first:
                first=False;skip_paragraph=omit_intro
            elif label not in ['Sigue explorando','Empresas que confían en nosotros',omit_heading]:
                out.append(f'<h2>{E(label)}</h2>')
        elif raw.startswith('### '):
            out.append(f'<h2>{E(raw[4:])}</h2>')
        elif question:
            faq.append(f'<details><summary>{E(question)}</summary><p>{inline(raw)}</p></details>');question=None
        elif raw.startswith('- '):
            out.append('<ul>'+''.join('<li>'+inline(x[2:])+'</li>' for x in raw.splitlines() if x.startswith('- '))+'</ul>')
        elif raw.startswith('Volver a '):
            continue
        else:
            if skip_paragraph:
                skip_paragraph=False
                continue
            out.append('<p>'+inline(raw).replace('\n','<br>')+'</p>')
    return '<div class="content-block">'+''.join(out)+'</div>'+ ('<section class="faq"><h2>Preguntas frecuentes</h2>'+''.join(faq)+'</section>' if faq else '')

def parse():
    text=(ROOT/'src/content.md').read_text()
    matches=list(re.finditer(r'^## (\d+)\. (.*?) — (/\S*)',text,re.M))
    pages=[]
    for i,m in enumerate(matches):
        body=text[m.end():matches[i+1].start() if i+1<len(matches) else text.index('## Enlaces y mensajes')]
        title=re.search(r'\*\*Title:\*\* (.+)',body)
        desc=re.search(r'\*\*Descripción SEO:\*\* (.+)',body)
        pages.append(dict(number=int(m[1]),name=m[2],path=m[3],body=body,title=title[1] if title else 'Privacidad | Impresiones Graphito',description=desc[1] if desc else 'Información de privacidad y contacto de Impresiones Graphito.'))
    assert len(pages)==29
    return pages

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='dist',choices=['dist']);args=parser.parse_args()
    out=ROOT/args.output
    if out.resolve()==ROOT.resolve() or ROOT not in out.resolve().parents: raise ValueError('Output must be a subdirectory of the project')
    if out.exists(): shutil.rmtree(out)
    out.mkdir();shutil.copytree(ROOT/'assets',out/'assets')
    for verification in ['googled4596d5466e1d60a.html','BingSiteAuth.xml']:
        shutil.copyfile(ROOT/'assets'/verification,out/verification)
    shutil.copyfile(ROOT/'src/site.css',out/'assets/site.css');shutil.copyfile(ROOT/'src/site.js',out/'assets/site.js')
    pages=parse();products=pages[8:26]
    for p in pages:
        n,path=p['number'],p['path']
        if n==1:
            body=hero('Tu marca, en cada impresión','Papelería corporativa, cuadernos, publicidad, merchandising y packaging para tu empresa. Cuéntanos qué necesitas y cotizamos tu pedido a medida.',path,'hero.webp')
            body+='<div class="benefits-band"><div class="container"><span>Pedidos a demanda</span><span>Personalización</span><span>Enfoque empresarial</span><span>Contacto por WhatsApp</span></div></div>'
            body+=section('Todo lo que tu empresa necesita para comunicar su marca',category_cards())
            body+='<section class="printing-banner" style="background-image:url(/assets/images/final/printing.webp)"><div class="container"><div><p class="eyebrow">TU PROYECTO, A MEDIDA</p><h2>Impresión<br>offset y digital</h2><p>Conversemos sobre tu proyecto y sus opciones de impresión.</p><a class="button" href="/impresion-offset-y-digital/">Conoce más</a></div></div></section>'
            body+=section('Productos para tu empresa',product_cards(products,[0,1,6,7,11],'five'))
            steps=[('Cuéntanos tu proyecto','Comparte el producto y el uso que tienes en mente.'),('Revisamos tu requerimiento','Conversamos sobre las características de tu pedido.'),('Cotizamos a medida','La propuesta corresponde a tu proyecto.'),('Confirmamos los detalles','Las condiciones se acuerdan contigo.'),('Coordinamos tu pedido','Conforme a lo confirmado en la cotización.')]
            body+=section('Tu pedido, a medida','<div class="steps">'+''.join(f'<div class="step">{step_icon(i)}<h3>{h}</h3><p>{v}</p></div>' for i,(h,v) in enumerate(steps))+'</div>')
            gallery='<p>Ideas visuales para explorar tu proyecto. Las imágenes muestran diseños ilustrativos de productos.</p><div class="illustrative-gallery">'+''.join(f'<a href="{products[i]["path"]}"><img src="{asset(IMAGES[i])}" alt="Imagen ilustrativa de {E(products[i]["name"].lower())}" loading="lazy" width="800" height="600"></a>' for i in [0,6,13,14])+'</div>'
            body+=section('Imágenes ilustrativas de productos',gallery)+cta()+section('Empresas que confían en nosotros',carousel())
        elif n==2:
            body=hero('Productos corporativos a demanda','Soluciones para el trabajo, la comunicación y la presentación de tu marca.',path,'hero.webp',True)+section('Nuestras soluciones',category_cards())+section('Explora nuestros productos',product_cards(products,range(18)))+cta(path)
        elif 3<=n<=7:
            cat=CATEGORIES[n-3]
            body=hero(p['name'],'Cada pedido parte de lo que tu empresa necesita. Conversemos sobre tu proyecto.',path,cat[2],True)+section('Encuentra la pieza para tu proyecto',product_cards(products,cat[3]))+'<div class="container article">'+blocks(p,omit_heading='Encuentra la pieza para tu proyecto')+'</div>'+cta(path,p['name'])
        elif 9<=n<=26:
            i=n-9;cat=next(c for c in CATEGORIES if i in c[3]);intro=re.search(r'\*\*'+re.escape(p['name'])+r'\*\*\s+([^\n]+)',p['body'])
            body=f'<div class="container"><nav class="breadcrumbs" aria-label="Ruta de navegación"><a href="/">Inicio</a> / <a href="/productos/">Productos</a> / <a href="/{cat[0]}/">{cat[1]}</a></nav><section class="product-layout"><div class="product-gallery"><img src="{asset(IMAGES[i])}" alt="Imagen ilustrativa de {E(p["name"].lower())}" width="800" height="650" fetchpriority="high"></div><div class="product-summary"><p class="eyebrow">{E(cat[1])}</p><h1>{E(p["name"])}</h1><p>{E(intro[1] if intro else "Consulta tu pedido a medida para tu empresa.")}</p>{wa("Cotizar por WhatsApp",p["name"],path)}<p>Cantidades, características y condiciones se revisan en la cotización.</p></div></section></div>'
            features=[('Personalización','Comparte tu marca, diseño o referencia.'),('Pedido a demanda','Las cantidades y características se acuerdan contigo.'),('Uso empresarial','Cuéntanos cómo se utilizará el producto.')]
            body+='<section class="section soft"><div class="container"><div class="feature-grid">'+''.join(f'<div class="feature"><h2>{h}</h2><p>{v}</p></div>' for h,v in features)+'</div></div></section>'
            body+='<div class="container article">'+blocks(p,omit_intro=True)+'</div>'+section('También te puede interesar',product_cards(products,[j for j in cat[3] if j!=i][:2]))+cta(path,p['name'])
        elif n==29:
            body='<article class="container legal"><h1>Privacidad</h1><div class="notice"><p>Documento pendiente de validación. Esta versión de desarrollo no está habilitada para publicación.</p></div><h2>Contacto voluntario</h2><p>Los enlaces de contacto abren WhatsApp. Tú decides si envías el mensaje y qué información compartes para consultar tu pedido.</p><h2>Validaciones pendientes</h2><p>Antes de publicar se deben confirmar el responsable legal, las finalidades y el tratamiento operativo, proveedores, conservación y atención de derechos. No se ha activado analítica en esta versión.</p><p>Contacto comercial: <a href="mailto:ventas@igraphito.com">ventas@igraphito.com</a>.</p></article>'
        else:
            body='<article class="container article"><h1>'+E('Impresiones Graphito' if n==27 else p['name'])+'</h1>'+blocks(p)+'</article>'
            if n==8: body+=section('Productos relacionados',product_cards(products,[0,1,2,6,7,8,9,10,11]))
            if n==27: body+=section('Empresas que confían en nosotros',carousel())
            body+=cta(path)
        schema={'@context':'https://schema.org','@type':'WebPage','name':p['title'],'url':BASE+path,'description':p['description'],'inLanguage':'es-PE'}
        document='<!doctype html><html lang="es-PE"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(p['title'])+'</title><meta name="description" content="'+E(p['description'])+'"><meta name="robots" content="noindex,nofollow"><link rel="canonical" href="'+BASE+path+'"><meta property="og:title" content="'+E(p['title'])+'"><meta property="og:description" content="'+E(p['description'])+'"><meta property="og:url" content="'+BASE+path+'"><meta property="og:type" content="website"><meta property="og:image" content="'+BASE+'/assets/images/final/hero.webp"><meta property="og:image:alt" content="Imagen ilustrativa de productos corporativos"><link rel="icon" href="/assets/images/favicon.ico"><link rel="stylesheet" href="/assets/site.css"><script defer src="/assets/site.js"></script><script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script></head><body>'+header(path)+'<main id="contenido">'+body+'</main>'+footer(path)+'</body></html>'
        target=out/path.lstrip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(document)
    (out/'404.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8"><meta name="robots" content="noindex"><title>Página no encontrada | Graphito</title><h1>Página no encontrada</h1><p><a href="/">Volver al inicio</a></p></html>')
    (out/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+escape(BASE+p['path'])+'</loc></url>' for p in pages)+'</urlset>')
    (out/'.htaccess').write_text('Options -Indexes\nDirectoryIndex index.html\nErrorDocument 404 /404.html\n<IfModule mod_headers.c>\nHeader always set X-Robots-Tag "noindex, nofollow"\nHeader always set X-Content-Type-Options "nosniff"\nHeader always set Referrer-Policy "strict-origin-when-cross-origin"\n</IfModule>\n')
    (out/'routes.json').write_text(json.dumps([p['path'] for p in pages],indent=2))
    print(f'Built {len(pages)} pages; preview protected from indexing. Publication remains disabled.')

if __name__=='__main__':main()
