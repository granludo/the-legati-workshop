# The Legati Workshop: punto de entrada para Claude Code

@AGENTS.md

## Apéndice de Claude Code (solo lo específico de este harness)

- **Si la importación de arriba no se ha cargado, lee ahora [AGENTS.md](AGENTS.md).** Es el núcleo; su §1 (conviértete en un legatus) va primero.
- **Lanza un legatus con una pestaña con nombre:** `./claude_<name>.sh` desde la raíz del repositorio. Envuelve `legati/bin/legatus <name> claude-code`, que define `LEGATUS_AGENT`, añade `characters/<name>/boot.md` al prompt de sistema y pone nombre a la pestaña. A mano: `LEGATUS_AGENT=writer claude -n writer --append-system-prompt "$(cat characters/writer/boot.md)"`.
- **Los hooks** están en el `.claude/settings.json` versionado, con rutas `$CLAUDE_PROJECT_DIR`, así que un clon recién hecho funciona: el resumen de inicio de sesión, la comprobación de la bandeja en cada turno y la captura del Observatorio. Claude Code te pide que confíes en la carpeta la primera vez. Los añadidos propios de cada máquina van en `.claude/settings.local.json` (en el gitignore).
- **Permisos:** el `.claude/settings.json` versionado contiene las reglas `allow` / `deny`; las reglas deny valen en cualquier modo de permisos. El `git push` directo está denegado a propósito: los push se hacen dentro de `tools/git/sync.sh`, después del rebase.
- **Memoria:** el `memory/` del repositorio es la memoria del taller, indexada en `memory/MEMORY.md`. La automemoria propia de Claude Code (`~/.claude/projects/<repo-slug>/memory/`) es de cada máquina e invisible para Codex y para tus otras máquinas: lo que valga la pena conservar y acabe allí se traslada a `memory/`, con su línea de índice, en la misma sesión.
- **Commits:** pon los trailers de atribución del harness en el mensaje `-m` / `-F`; `tools/git/sync.sh` añade `Legatus:` / `Harness:` / `Host:`.
- **Comandos de barra:** `skills/<name>.md` es la única copia de una skill. Un fichero en `~/.claude/commands/` o `.claude/commands/` existe solo por comodidad al teclear y es un puntero de una línea a la skill del repositorio, nunca una copia: una copia se desvía con el tiempo, y Codex nunca la ve.
