# tools/google — Google Workspace setup

This folder is for setting up `gws` (Google Workspace CLI) for the comms agent. `gws` provides read-only access to Gmail, Google Calendar, and Google Drive via OAuth.

## What gws does

`gws` is a CLI tool by the same team as the workshop. The comms agent uses it to:
- List and read Gmail messages
- Read Google Calendar events
- List and read Google Drive files

It **cannot** send emails, create calendar events, or modify any Google data. The OAuth scope ceiling enforces this at the credential level.

## Install

```bash
npm install -g @googleworkspace/cli
# or via npx (no global install):
npx @googleworkspace/cli@latest
```

Check the installed version:
```bash
gws --version
```

## One-time OAuth setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or use an existing one).
3. Enable the Gmail API, Google Calendar API, and Google Drive API for the project.
4. Create an OAuth 2.0 Client ID (Application type: Desktop app).
5. Download the `client_secret.json` file and save it to `~/.config/gws/client_secret.json` (create the directory if it doesn't exist, set mode 0600).
6. Run the auth flow:
   ```bash
   gws auth login
   ```
7. Follow the browser prompts to authorize. The scope you want: `gmail.readonly`, `calendar.readonly`, `drive.readonly`.
8. Credentials are saved to `~/.config/gws/credentials.enc` (encrypted with a key stored in your OS keychain).

## Testing

```bash
gws gmail users messages list --maxResults 5
gws calendar calendarList list
gws drive files list --pageSize 5
```

If these return data, you're set up correctly.

## Cross-machine setup

OAuth credentials are per-machine (the encrypted file uses your OS keychain). To set up a second machine, run `gws auth login` again on that machine with the same `client_secret.json`. The `client_secret.json` can be shared via iCloud or a password manager; `credentials.enc` cannot.

## The comms agent's mandate

Once set up, the comms agent uses `gws` via shell calls in the session. It reads, summarizes, and surfaces information. It never calls `gws` commands that write data. The `--help` output lists all available commands; verify that any new commands used are read-only before adding them to the comms agent's toolset.
