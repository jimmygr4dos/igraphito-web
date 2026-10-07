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
IMAGES = ['Tarjetas-Personales.jpg','folders.png','membretadas.jpg','formatos.continuos.jpg','fotochecks.jpg','sellos.trodat.jpg','cuadernos.png','agendas.webp','calendarios.webp','flyers.jpg','dipticos.webp','tripticos.jpg','lapiceros.corporativos.jpg','tazas.corporativas.jpg','bolsas.papel.jpg','cajas.liner.jpg','adhesivos.webp','hangtags.png']

def wa(label='Solicitar cotización', product=None, path='/', classes='button', cta='content'):
    text = f'Hola, quisiera cotizar {product} para mi empresa.' if product else 'Hola, quisiera cotizar un pedido empresarial con Graphito.'
    text += ' Vi esta página: ' + BASE + path
    return f'<a class="{classes}" data-product="{E(product or "general")}" data-cta="{cta}" href="https://wa.me/51942722449?text={quote(text)}">{E(label)}</a>'

def asset(image):
    return '/assets/images/products/' + image

def card(title, path, image, description='Consulta las características de tu pedido a medida.'):
    return f'<article class="product-card"><a class="card-image" href="{path}"><img src="{asset(image)}" alt="{E(title)}" loading="lazy" width="600" height="450"></a><div class="card-body"><h3><a href="{path}">{E(title)}</a></h3><p>{E(description)}</p><a class="text-link" href="{path}">Conoce más <span aria-hidden="true">→</span></a></div></article>'

def section(title, body, extra=''):
    return f'<section class="section {extra}"><div class="container"><div class="section-heading"><h2>{E(title)}</h2></div>{body}</div></section>'

def category_cards():
    return '<div class="card-grid five">' + ''.join(card(n,'/'+s+'/',i) for s,n,i,_ in CATEGORIES) + '</div>'

def product_cards(products, indices):
    return '<div class="card-grid">' + ''.join(card(products[i]['name'],products[i]['path'],IMAGES[i]) for i in indices) + '</div>'

def carousel():
    logos = ''.join(f'<div class="client-logo"><img src="/assets/images/clients/item{i}.jpg" alt="Logotipo de cliente real de Graphito, {i} de 24" loading="lazy" width="210" height="110"></div>' for i in range(1,25))
    return '<div class="client-carousel" data-carousel role="region" aria-label="Empresas que confían en nosotros"><div class="carousel-track" tabindex="0" aria-label="Logotipos de clientes; desliza o usa las flechas para explorar">'+logos+'<'+ '/div><div class="carousel-controls"><button hidden data-carousel-prev aria-label="Clientes anteriores">←</button><button hidden data-carousel-toggle aria-pressed="false">Pausar</button><button hidden data-carousel-next aria-label="Clientes siguientes">→</button></div></div>'

def cta(path='/', product=None):
    return '<section class="cta-band"><div class="container"><div><h2>Hablemos de tu pedido empresarial</h2><p>Cuéntanos qué necesitas y cotizamos tu proyecto a medida.</p></div>'+wa('Conversemos por WhatsApp',product,path,cta='bottom')+'</div></section>'

def header(path):
    def link(p,n):
        current = ' aria-current="page"' if path == p else ''
        return f'<a href="{p}"{current}>{n}</a>'
    submenu = ''.join('<li>'+link('/'+s+'/',n)+'</li>' for s,n,_,_ in CATEGORIES)
    return '<a class="skip-link" href="#contenido">Saltar al contenido</a><header class="site-header"><div class="container"><a class="brand" href="/" aria-label="Impresiones Graphito, inicio"><img src="/assets/images/logo.png" alt="" width="70" height="70"><img src="/assets/images/wordmark.png" alt="Impresiones Graphito" width="188" height="29"></a><button class="nav-toggle" data-nav-toggle aria-controls="primary-nav" aria-expanded="false" aria-label="Abrir menú" hidden>☰</button><nav class="nav" id="primary-nav" aria-label="Navegación principal"><ul class="nav-links"><li>'+link('/','Inicio')+'</li><li><details class="nav-menu"><summary>Soluciones</summary><ul class="nav-submenu"><li>'+link('/productos/','Todos los productos')+'</li>'+submenu+'</ul></details></li><li>'+link('/impresion-offset-y-digital/','Impresión')+'</li><li>'+link('/nosotros/','Nosotros')+'</li><li>'+link('/contacto/','Contacto')+'</li></ul></nav><div class="header-contact"><a href="tel:+51942722449">942 722 449</a>'+wa(path=path,cta='header')+'</div></div></header>'

def footer(path):
    return '<footer class="site-footer"><div class="container"><div class="footer-grid"><div><h2>Impresiones Graphito</h2><p>Tu marca, en cada impresión.<br>Soluciones gráficas para empresas en Lima.</p></div><div><h3>Soluciones</h3>'+''.join(f'<p><a href="/{s}/">{n}</a></p>' for s,n,_,_ in CATEGORIES)+'</div><div><h3>Conversemos</h3><p><a href="tel:+51942722449">942 722 449</a></p><p><a href="mailto:ventas@igraphito.com">ventas@igraphito.com</a></p>'+wa('Escríbenos por WhatsApp',path=path,cta='footer')+'</div><div><h3>Graphito</h3><p><a href="/nosotros/">Nosotros</a></p><p><a href="/contacto/">Contacto</a></p><p><a href="/privacidad/">Privacidad</a></p></div></div><div class="footer-bottom"><p>© Impresiones Graphito</p><a href="/productos/">Productos corporativos a demanda</a></div></div></footer>'+wa('WhatsApp',path=path,classes='whatsapp-float',cta='floating')

def hero(title, paragraph, path, image, compact=False):
    return f'<section class="hero {"compact" if compact else ""}"><img class="hero-photo" src="{asset(image)}" alt="" width="1440" height="700" fetchpriority="high"><div class="hero-inner"><div class="hero-copy"><p class="eyebrow">SOLUCIONES GRÁFICAS PARA EMPRESAS EN LIMA</p><h1>{E(title)}</h1><p>{E(paragraph)}</p><div class="hero-actions">{wa(path=path)}<a class="button button-outline" href="/productos/">Ver soluciones</a></div></div></div></section>'

def inline(text):
    result = E(text)
    result = re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',result)
    result = result.replace('942 722 449', '<a href="tel:+51942722449">942 722 449</a>')
    result = result.replace('ventas@igraphito.com','<a href="mailto:ventas@igraphito.com">ventas@igraphito.com</a>')
    return result

def blocks(page):
    """Editorial labels become semantic headings; internal instructions are excluded."""
    lines = page['body'].split('\n\n')
    out=[]; faq=[]; question=None; first=True
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
            if 'WhatsApp' in label or target == 'WhatsApp':
                out.append(wa(label,page['name'],page['path']))
            elif target and target.startswith('/'):
                out.append(f'<p><a class="text-link" href="{E(target)}">{E(label)}</a></p>')
            elif first:
                first=False
            elif label not in ['Sigue explorando','Empresas que confían en nosotros']:
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
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='dist');args=parser.parse_args()
    out=ROOT/args.output
    if out.resolve()==ROOT.resolve() or ROOT not in out.resolve().parents: raise ValueError('Output must be a subdirectory of the project')
    if out.exists(): shutil.rmtree(out)
    out.mkdir();shutil.copytree(ROOT/'assets',out/'assets')
    shutil.copyfile(ROOT/'src/site.css',out/'assets/site.css');shutil.copyfile(ROOT/'src/site.js',out/'assets/site.js')
    pages=parse();products=pages[8:26]
    for p in pages:
        n,path=p['number'],p['path']
        if n==1:
            body=hero('Tu marca, en cada impresión','Papelería corporativa, cuadernos, publicidad, merchandising y packaging para tu empresa. Cuéntanos qué necesitas y cotizamos tu pedido a medida.',path,'folders.png')
            body+=section('Todo lo que tu empresa necesita para comunicar su marca',category_cards())
            body+='<section class="printing-banner"><div class="container"><div><p class="eyebrow">IMPRESIÓN OFFSET Y DIGITAL</p><h2>El proyecto empieza con lo que necesitas imprimir</h2><p>La cantidad, el formato, el uso y la presentación ayudan a evaluar cada pedido.</p><a class="button" href="/impresion-offset-y-digital/">Conoce más</a></div></div></section>'
            body+=section('Productos para tu empresa',product_cards(products,[0,1,6,7,11]))
            steps=[('Cuéntanos tu proyecto','Comparte el producto y el uso que tienes en mente.'),('Revisamos tu requerimiento','Conversamos sobre las características de tu pedido.'),('Cotizamos a medida','La propuesta corresponde a tu proyecto.'),('Confirmamos los detalles','Las condiciones se acuerdan contigo.'),('Coordinamos tu pedido','Conforme a lo confirmado en la cotización.')]
            body+=section('Tu pedido, a medida','<div class="steps">'+''.join(f'<div class="step"><h3>{h}</h3><p>{v}</p></div>' for h,v in steps)+'</div>')
            body+=cta()+section('Empresas que confían en nosotros',carousel())
        elif n==2:
            body=hero('Productos corporativos a demanda','Soluciones para el trabajo, la comunicación y la presentación de tu marca.',path,'cuadernos.png',True)+section('Nuestras soluciones',category_cards())+section('Explora nuestros productos',product_cards(products,range(18)))+cta(path)
        elif 3<=n<=7:
            cat=CATEGORIES[n-3]
            body=hero(p['name'],'Cada pedido parte de lo que tu empresa necesita. Conversemos sobre tu proyecto.',path,cat[2],True)+section('Encuentra la pieza para tu proyecto',product_cards(products,cat[3]))+'<div class="container article">'+blocks(p)+'</div>'+cta(path,p['name'])
        elif 9<=n<=26:
            i=n-9;cat=next(c for c in CATEGORIES if i in c[3]);intro=re.search(r'\*\*'+re.escape(p['name'])+r'\*\*\s+([^\n]+)',p['body'])
            body=f'<div class="container"><nav class="breadcrumbs" aria-label="Ruta de navegación"><a href="/">Inicio</a> / <a href="/productos/">Productos</a> / <a href="/{cat[0]}/">{cat[1]}</a></nav><section class="product-layout"><div class="product-gallery"><img src="{asset(IMAGES[i])}" alt="{E(p["name"])}" width="800" height="650" fetchpriority="high"></div><div class="product-summary"><p class="eyebrow">{E(cat[1])}</p><h1>{E(p["name"])}</h1><p>{E(intro[1] if intro else "Consulta tu pedido a medida para tu empresa.")}</p>{wa("Cotizar por WhatsApp",p["name"],path)}<p>Cantidades, características y condiciones se revisan en la cotización.</p></div></section></div>'
            body+='<div class="container article">'+blocks(p)+'</div>'+section('También te puede interesar',product_cards(products,[j for j in cat[3] if j!=i][:2]))+cta(path,p['name'])
        elif n==29:
            body='<article class="container legal"><h1>Privacidad</h1><div class="notice"><p>Documento pendiente de validación. Esta versión de desarrollo no está habilitada para publicación.</p></div><h2>Contacto voluntario</h2><p>Los enlaces de contacto abren WhatsApp. Tú decides si envías el mensaje y qué información compartes para consultar tu pedido.</p><h2>Validaciones pendientes</h2><p>Antes de publicar se deben confirmar el responsable legal, las finalidades y el tratamiento operativo, proveedores, conservación y atención de derechos. No se ha activado analítica en esta versión.</p><p>Contacto comercial: <a href="mailto:ventas@igraphito.com">ventas@igraphito.com</a>.</p></article>'
        else:
            body='<article class="container article"><h1>'+E('Impresiones Graphito' if n==27 else p['name'])+'</h1>'+blocks(p)+'</article>'
            if n==8: body+=section('Productos relacionados',product_cards(products,[0,1,2,6,7,8,9,10,11]))
            if n==27: body+=section('Empresas que confían en nosotros',carousel())
            body+=cta(path)
        schema={'@context':'https://schema.org','@type':'WebPage','name':p['title'],'url':BASE+path,'description':p['description'],'inLanguage':'es-PE'}
        document='<!doctype html><html lang="es-PE"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(p['title'])+'</title><meta name="description" content="'+E(p['description'])+'"><meta name="robots" content="noindex,nofollow"><link rel="canonical" href="'+BASE+path+'"><meta property="og:title" content="'+E(p['title'])+'"><meta property="og:description" content="'+E(p['description'])+'"><meta property="og:url" content="'+BASE+path+'"><meta property="og:type" content="website"><link rel="icon" href="/assets/images/favicon.ico"><link rel="stylesheet" href="/assets/site.css"><script defer src="/assets/site.js"></script><script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script></head><body>'+header(path)+'<main id="contenido">'+body+'</main>'+footer(path)+'</body></html>'
        target=out/path.lstrip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(document)
    (out/'404.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8"><meta name="robots" content="noindex"><title>Página no encontrada | Graphito</title><h1>Página no encontrada</h1><p><a href="/">Volver al inicio</a></p></html>')
    (out/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+escape(BASE+p['path'])+'</loc></url>' for p in pages)+'</urlset>')
    (out/'.htaccess').write_text('Options -Indexes\nDirectoryIndex index.html\nErrorDocument 404 /404.html\n<IfModule mod_headers.c>\nHeader always set X-Robots-Tag "noindex, nofollow"\nHeader always set X-Content-Type-Options "nosniff"\nHeader always set Referrer-Policy "strict-origin-when-cross-origin"\n</IfModule>\n')
    (out/'routes.json').write_text(json.dumps([p['path'] for p in pages],indent=2))
    print(f'Built {len(pages)} pages; preview protected from indexing. Publication remains disabled.')

if __name__=='__main__':main()
