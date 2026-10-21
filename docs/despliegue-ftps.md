# Publicación por FTPS

La publicación inicial se completó el 21/10/2026. La verificación pública confirmó 31 páginas y 37 recursos accesibles.

## Publicaciones posteriores

En Actions, abrir «Publicar Graphito por FTPS», pulsar Run workflow, elegir main y mode=publish. mode=check solo comprueba conexión y destino. No se publica automáticamente al cambiar la web.

El proceso genera y valida el sitio, habilita indexación de producción y usa FTP_PASSWORD de los secretos del repositorio. Conecta a igraphito.com:21 con FTPS explícito, usuario igraphito@igraphito.com. El certificado presentado por el hosting pertenece a nemesis.sipanserver.com; se verifica la cadena y ese nombre y se comprueba que ambos nombres resuelvan a una IP común.

## Respaldos

Antes de subir archivos, descarga íntegramente public_html, genera un ZIP y lo guarda en igraphito-private-backups, fuera de public_html. Si no puede completar el respaldo, detiene la publicación. No se suben respaldos a GitHub.

Respaldo de la web anterior a la primera publicación: public_html-20261021T155712Z.zip. Conservarlo para recuperar la versión anterior. Los respaldos posteriores pueden contener ya el nuevo diseño.

Para restaurar, acceder al hosting y extraer la carpeta public_html del ZIP seleccionado. Revisar diferencias antes de reemplazar archivos; el despliegue conserva los archivos ajenos al nuevo build. No modificar DNS ni correo.

Tras cada publicación correcta, «Verificar web publicada» comprueba las 31 rutas, el contacto, la indexación y los recursos públicos.
