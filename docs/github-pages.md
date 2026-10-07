# Revisión navegable en GitHub Pages

La rama gh-pages contiene el sitio completo generado: 29 páginas y 20 imágenes finales. Las rutas se adaptaron a /igraphito-web/ y la versión conserva noindex. No modifica igraphito.com, Publiperú, DNS ni correo.

Generar: python3 scripts/build.py --base-path igraphito-web --site-url https://jimmygr4dos.github.io
Validar: python3 scripts/check.py

La rama gh-pages contiene únicamente el resultado generado y los assets; nunca publicar el repositorio entero, respaldos o credenciales.

Configuración necesaria: Settings → Pages → Deploy from a branch → gh-pages → / (root) → Save.

Al 07/10/2026, el navegador devolvió HTTP 500 al guardar tanto la fuente GitHub Actions como la fuente desde rama. La activación no está confirmada. No presentar la URL prevista como publicada hasta verificar que sirve el sitio completo.

URL prevista: https://jimmygr4dos.github.io/igraphito-web/

Una modificación en main requiere regenerar y actualizar gh-pages. No se configura publicación automática a igraphito.com.
