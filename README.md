# igraphito-web

Rediseño completo de igraphito.com para clientes empresariales, con enfoque SEO y contacto por WhatsApp.

## Alcance aprobado

29 páginas: inicio, catálogo, cinco categorías, impresión offset y digital, 18 productos, nosotros, contacto y privacidad.

- Diseño aprobado: «Tu marca, en cada impresión», verde bosque, logotipo original.
- Productos corporativos a demanda: sin cantidades mínimas, precios, tamaños ni plazos publicados.
- WhatsApp: +51 942 722 449. Correo: ventas@igraphito.com.
- Carrusel accesible con los 24 logotipos de clientes reales.
- Sin formularios comerciales, carrito ni checkout.
- No modificar hosting, DNS ni correo productivos. La publicación requiere aprobación independiente.

## Estado

Las 29 rutas se generan desde `src/content.md` mediante `scripts/build.py`. Incluye CSS responsive, navegación, carrusel accesible, enlaces de WhatsApp y assets originales recuperados del sitio actual. El arte final de las 20 imágenes está completo e integrado. Privacidad requiere validación antes de publicación.

## Desarrollo

Requiere Python 3. No necesita dependencias externas para generar el sitio.

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8080 --directory dist
```

El resultado se genera en `dist/`. El build de revisión bloquea la indexación. No hay despliegue automático a producción.

## Verificación

Comprobación estática aprobada: 29 rutas, 20 imágenes finales, H1 únicos, metadatos, enlaces internos, assets, verificaciones Google/Bing originales, contacto de WhatsApp y ausencia de formularios o notas editoriales. La comprobación visual en navegador está pendiente.

Consulta `docs/publicacion.md` para condiciones de publicación.
