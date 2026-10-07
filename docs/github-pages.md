# Revisión navegable en GitHub Pages

La rama gh-pages contiene el sitio completo generado: 29 páginas y 20 imágenes finales. Las rutas se adaptaron a /igraphito-web/ y la versión conserva noindex. No modifica igraphito.com, Publiperú, DNS ni correo.

Generar: python3 scripts/build.py --base-path igraphito-web --site-url https://jimmygr4dos.github.io
Validar: python3 scripts/check.py

La rama gh-pages contiene únicamente el resultado generado y los assets; nunca publicar el repositorio entero, respaldos o credenciales.

Configuración necesaria: Settings → Pages → Deploy from a branch → gh-pages → / (root) → Save.

El 07/10/2026 se confirmó en Settings → Pages la fuente gh-pages / (root) y HTTPS obligatorio. GitHub mostró HTTP 500 después de guardar, pero una comprobación posterior confirmó que el ajuste quedó aplicado. Ejecución de publicación: https://github.com/jimmygr4dos/igraphito-web/actions/runs/37655615798. Verificar la URL antes de dar por completado el despliegue.

URL prevista: https://jimmygr4dos.github.io/igraphito-web/

Una modificación en main requiere regenerar y actualizar gh-pages. No se configura publicación automática a igraphito.com.
