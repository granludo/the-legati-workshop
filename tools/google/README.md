# tools/google: configuració de Google Workspace

Aquesta carpeta serveix per configurar `gws` (la CLI de Google Workspace) per a l'agent comms. `gws` dona accés de només lectura a Gmail, Google Calendar i Google Drive a través d'OAuth.

## Què fa gws

`gws` és una eina de línia d'ordres del mateix equip que el taller. L'agent comms la fa servir per:
- Llistar i llegir missatges de Gmail
- Llegir esdeveniments de Google Calendar
- Llistar i llegir fitxers de Google Drive

**No pot** enviar correus, crear esdeveniments de calendari ni modificar cap dada de Google. El límit d'àmbits d'OAuth ho imposa a la mateixa credencial.

## Instal·lació

```bash
npm install -g @googleworkspace/cli
# or via npx (no global install):
npx @googleworkspace/cli@latest
```

Comprova la versió instal·lada:
```bash
gws --version
```

## Configuració d'OAuth (una sola vegada)

1. Ves a [Google Cloud Console](https://console.cloud.google.com/).
2. Crea un projecte nou (o fes-ne servir un d'existent).
3. Activa la Gmail API, la Google Calendar API i la Google Drive API per al projecte.
4. Crea un ID de client OAuth 2.0 (tipus d'aplicació: aplicació d'escriptori).
5. Descarrega el fitxer `client_secret.json` i desa'l a `~/.config/gws/client_secret.json` (crea el directori si no existeix i posa-hi el mode 0600).
6. Executa el flux d'autenticació:
   ```bash
   gws auth login
   ```
7. Segueix les indicacions del navegador per autoritzar-lo. Els àmbits que vols: `gmail.readonly`, `calendar.readonly`, `drive.readonly`.
8. Les credencials es desen a `~/.config/gws/credentials.enc` (xifrades amb una clau guardada al clauer del sistema operatiu).

## Proves

```bash
gws gmail users messages list --maxResults 5
gws calendar calendarList list
gws drive files list --pageSize 5
```

Si aquestes ordres tornen dades, la configuració és correcta.

## Configuració en diverses màquines

Les credencials d'OAuth són per màquina (el fitxer xifrat fa servir el clauer del sistema operatiu). Per configurar una segona màquina, torna a executar `gws auth login` en aquella màquina amb el mateix `client_secret.json`. El `client_secret.json` es pot compartir per iCloud o amb un gestor de contrasenyes; `credentials.enc`, no.

## El mandat de l'agent comms

Un cop configurat, l'agent comms fa servir `gws` amb crides al shell dins la sessió. Llegeix, resumeix i fa aflorar informació. Mai no crida ordres de `gws` que escriguin dades. La sortida de `--help` llista totes les ordres disponibles; comprova que qualsevol ordre nova que es faci servir sigui de només lectura abans d'afegir-la al conjunt d'eines de l'agent comms.
