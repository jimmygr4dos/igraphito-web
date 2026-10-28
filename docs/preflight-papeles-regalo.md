# Validación previa del paquete de producción

Fecha: 28 de octubre de 2026. Rama: `feature/papeles-regalo-empresariales`.

El generador copiaba el directorio completo `assets` a `dist`, incluyendo
recursos antiguos que ninguna página usa. El despliegue subía todos esos archivos.

| Comprobación | Resultado |
| --- | --- |
| Salida completa `dist` | 131 archivos; 6.922.185 bytes |
| Paquete depurado `release` | 82 archivos; 3.693.223 bytes |
| Excluidos del envío | 49 archivos; 3.228.962 bytes |
| Recursos sin uso excluidos | 46, incluido el SVG reemplazado y las copias de verificaciones |
| Metadatos de pruebas excluidos | `routes.json`, `hosting.json`, `.nojekyll` |
| Duplicados por SHA-256 en el paquete final | 0 |
| Referencias locales rotas en el paquete final | 0 |
| Colisiones de ruta al ignorar mayúsculas | 0 |
| Páginas conservadas | 32 y la página de error 404 |

`python scripts/prepare_release.py` construye `release` desde las rutas publicables
y sigue sus dependencias. Conserva imágenes, estilos, scripts, favicon, sitemap,
robots, `.htaccess` y verificaciones necesarias. Genera un inventario local con
ruta, tamaño y SHA-256 en `release-manifest.json`; el inventario no se sube al hosting.

`deploy_ftps.py` ejecuta esa validación antes de conectar y solo envía `release`.
Los checks automáticos también la ejecutan. Se probaron tres rechazos: duplicado
referenciado, imagen inexistente y configuración de GitHub Pages. Todos abortaron
antes de crear el paquete o conectar al hosting.

Esta revisión controla los archivos del próximo envío. No realiza un inventario
actual ni elimina archivos históricos del hosting. El despliegue sigue preservando
los archivos remotos ajenos al paquete y creando su respaldo previo. No se realizó
publicación en producción. La protección debe llegar a `main` junto al producto
antes de ejecutar el despliegue manual.
