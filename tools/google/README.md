# tools/google: configuración de Google Workspace

Esta carpeta sirve para configurar `gws` (la CLI de Google Workspace) para el agente comms. `gws` da acceso de solo lectura a Gmail, Google Calendar y Google Drive mediante OAuth.

## Qué hace gws

`gws` es una herramienta de línea de comandos del mismo equipo que el taller. El agente comms la usa para:
- Listar y leer mensajes de Gmail
- Leer eventos de Google Calendar
- Listar y leer ficheros de Google Drive

**No puede** enviar correos, crear eventos de calendario ni modificar ningún dato de Google. El techo de alcance de OAuth lo impone a nivel de credenciales.

## Instalación

```bash
npm install -g @googleworkspace/cli
# or via npx (no global install):
npx @googleworkspace/cli@latest
```

Comprueba la versión instalada:
```bash
gws --version
```

## Configuración de OAuth (una sola vez)

1. Ve a [Google Cloud Console](https://console.cloud.google.com/).
2. Crea un proyecto nuevo (o usa uno existente).
3. Activa para el proyecto la Gmail API, la Google Calendar API y la Google Drive API.
4. Crea un ID de cliente OAuth 2.0 (tipo de aplicación: aplicación de escritorio).
5. Descarga el fichero `client_secret.json` y guárdalo en `~/.config/gws/client_secret.json` (crea el directorio si no existe y ponle el modo 0600).
6. Ejecuta el flujo de autenticación:
   ```bash
   gws auth login
   ```
7. Sigue las indicaciones del navegador para autorizar. El alcance que quieres: `gmail.readonly`, `calendar.readonly`, `drive.readonly`.
8. Las credenciales se guardan en `~/.config/gws/credentials.enc` (cifradas con una clave guardada en el llavero del sistema operativo).

## Prueba

```bash
gws gmail users messages list --maxResults 5
gws calendar calendarList list
gws drive files list --pageSize 5
```

Si devuelven datos, está todo bien configurado.

## Configuración en varias máquinas

Las credenciales de OAuth son de cada máquina (el fichero cifrado usa el llavero del sistema operativo). Para configurar una segunda máquina, vuelve a ejecutar `gws auth login` en ella con el mismo `client_secret.json`. El `client_secret.json` se puede compartir por iCloud o con un gestor de contraseñas; `credentials.enc`, no.

## El mandato del agente comms

Una vez configurado, el agente comms usa `gws` mediante llamadas al shell dentro de la sesión. Lee, resume y pone la información a la vista. Nunca llama a comandos de `gws` que escriban datos. La salida de `--help` lista todos los comandos disponibles; antes de añadir un comando nuevo al conjunto de herramientas del agente comms, comprueba que es de solo lectura.
