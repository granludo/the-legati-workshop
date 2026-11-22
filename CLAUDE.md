# The Legati Workshop: punt d'entrada de Claude Code

@AGENTS.md

## Apèndix de Claude Code (només el que és específic d'aquest harness)

- **Si la importació de dalt no s'ha carregat, llegeix ara [AGENTS.md](AGENTS.md).** És el nucli; el seu §1 (converteix-te en un legatus) va primer.
- **Arrenca com a legatus en una pestanya amb nom:** `./claude_<name>.sh` des de l'arrel del repositori. És un embolcall de `legati/bin/legatus <name> claude-code`, que defineix `LEGATUS_AGENT`, afegeix `characters/<name>/boot.md` al prompt de sistema i posa nom a la pestanya. A mà: `LEGATUS_AGENT=writer claude -n writer --append-system-prompt "$(cat characters/writer/boot.md)"`.
- **Els hooks** són al `.claude/settings.json` versionat, amb camins `$CLAUDE_PROJECT_DIR`, de manera que un clon nou ja funciona: el resum d'inici de sessió, la comprovació de la safata a cada torn i la captura de l'Observatori. Claude Code et demana que confiïs en la carpeta la primera vegada. Els afegits propis de cada màquina van a `.claude/settings.local.json` (ignorat per git).
- **Permisos:** el `.claude/settings.json` versionat conté les regles `allow` / `deny`; les regles de denegació valen en tots els modes de permisos. El `git push` directe està denegat a propòsit: els push es fan dins de `tools/git/sync.sh`, després del rebase.
- **Memòria:** la carpeta `memory/` del repositori és la memòria del taller, indexada a `memory/MEMORY.md`. L'auto-memòria pròpia de Claude Code (`~/.claude/projects/<repo-slug>/memory/`) és de cada màquina i invisible per a Codex i per a les teves altres màquines: qualsevol cosa que valgui la pena conservar i que hi vagi a parar es trasllada a `memory/`, amb una línia a l'índex, en la mateixa sessió.
- **Commits:** posa els trailers d'atribució del harness al missatge de `-m` / `-F`; `tools/git/sync.sh` hi afegeix `Legatus:` / `Harness:` / `Host:`.
- **Ordres de barra:** `skills/<name>.md` és l'única còpia d'una skill. Un fitxer a `~/.claude/commands/` o a `.claude/commands/` només existeix per comoditat a l'hora de teclejar i és un punter d'una línia a la skill del repositori, mai una còpia: una còpia se'n va desviant, i Codex no la veu mai.
