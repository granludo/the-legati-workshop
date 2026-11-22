# legati/: trabajar juntos entre sesiones, máquinas y harness

Varias sesiones de legati pueden trabajar a la vez en este repositorio: dos pestañas de terminal en una máquina, un portátil y un ordenador de sobremesa, Claude Code junto a Codex. Nada de lo que hay aquí presupone un único harness. El contexto y las lecciones aprendidas están en [good-practices/08-many-legati-many-harnesses.md](../good-practices/08-many-legati-many-harnesses.md); este fichero es el manual de operaciones.

## La idea en un párrafo

**Git es el bus.** Cada commit es un evento fechado y con autoría que cualquier sesión lee después de un pull; los traspasos son ficheros que viajan en commits; reservar un carril es hacer un commit en el backlog del proyecto. Máquinas distintas tienen árboles de trabajo separados; los terminales de una misma máquina pueden compartir un mismo checkout. Las sesiones de una misma máquina tienen además la presencia en vivo, los bloqueos y el chat del Observatorio de los legati (`engineering-projects/legati-observatory/`); todo eso nunca sale de la máquina y nada de lo que hay aquí depende de ello.

## Las cuatro reglas

1. **Toda escritura en git pasa por `tools/git/sync.sh`.** Solo staging limitado a rutas (nunca `-A`, nunca `.`), trailers `Legatus:` / `Harness:` / `Host:` añadidos automáticamente, rebase sobre origin y push en el acto. Un commit sin push no existe para los demás. En macOS, el rebase quita el indicador de inmutabilidad (`uchg`) de los ficheros que tiene que reescribir y lo restaura después.
   ```bash
   bash tools/git/sync.sh commit -m "Subject line" -- path/one.md path/two.md
   bash tools/git/sync.sh status | pull | push | log | whoami
   ```
2. **Reserva el carril antes de trabajar en un proyecto.** `python3 tools/legati/lane.py claim <project-dir> "<task>"` pone un callout `> [!lane]` al principio del `BACKLOG.md` de ese proyecto y hace push. `lane.py list` muestra todos los carriles activos; una reserva de otro con menos de 24 horas significa retirarse o coordinarse. `lane.py release <project-dir>` al terminar.
3. **Los mensajes son ficheros, uno por mensaje.** `python3 tools/legati/handoff.py send --to writer --subject "…" --body "…"` escribe `legati/handoffs/<timestamp>_<from>_to_<to>_<slug>.md` y hace push. Los destinatarios lo ven con `handoff.py inbox` y lo archivan con `handoff.py ack <file>` (se mueve a `legati/handoffs/archive/YYYY-MM/` y se hace commit). `--to all` lo difunde a todos; los lectores avanzan una marca local en lugar de archivarlo. Un fichero por mensaje es lo que impide que dos remitentes choquen nunca en la misma línea.
4. **Inicio de sesión = mira antes de tocar.** `bash tools/legati/host-section.sh` imprime la sección de esta máquina en `memory/reference_hosts.md`. `tools/legati/session-start.sh` hace fetch, hace pull solo cuando el árbol está limpio y no hay ningún commit local, y lista los commits desde la última vez que esta máquina y este harness miraron, los carriles activos y los traspasos sin leer. `tools/legati/turn-start.sh` muestra los traspasos nuevos antes de cada prompt. Los dos tienen hook en Claude Code (`.claude/settings.json` versionado) y en Codex (`install-hooks.sh codex`).

## Lanzar un legatus

| | Claude Code | Codex |
|---|---|---|
| Un legatus en esta pestaña | `./claude_<name>.sh` | `./codex_<name>.sh` |
| Qué ejecuta | `legati/bin/legatus <name> claude-code` | `legati/bin/legatus <name> codex` |
| Cómo llega el fichero de arranque | se añade al prompt de sistema | Codex lee `AGENTS.md` de forma nativa; el prompt inicial nombra el fichero de arranque |
| Configuración única por máquina | confiar en la carpeta cuando lo pida | `codex login`, `bash tools/legati/install-hooks.sh codex`, aprobar `/hooks` una vez |

- El lanzador define `LEGATUS_AGENT` y `LEGATUS_HARNESS`, pone nombre a la pestaña del terminal y arranca el harness en la raíz del repositorio. Para Codex define además un `LEGATUS_SESSION` único, de modo que dos pestañas de Codex simultáneas nunca comparten identidad.
- **Dos legati en una pestaña:** `legati/bin/legatus comms --with reviewer` (o `comms+reviewer`). Se exporta `LEGATUS_COMPANIONS`, la pestaña se titula `COMMS+REVIEWER` y se cargan los dos ficheros de arranque tras una nota de emparejamiento: el que lidera responde por defecto, el acompañante en su carril, cada uno con su propio prefijo.
- **Harness y modelo por defecto de cada legatus:** `legati/roster.toml`. Los envoltorios de la raíz nombran el harness de forma explícita; `legati/bin/legatus <name>` a secas usa el roster.
- **Legatus nuevo o renombrado:** `bash tools/legati/make-launchers.sh` regenera los envoltorios a partir de `characters/*/boot.md`.
- **Ensayo en seco:** `LEGATUS_DRY_RUN=1 ./codex_writer.sh` imprime el comando sin lanzarlo.
- Los argumentos adicionales pasan al harness: `./codex_reviewer.sh -m <model>`, `./claude_writer.sh --model <model>`.

## Identidad

`Legatus` sale de la marca por sesión del Observatorio (`obs.py agent <name>` la escribe en un cambio de personaje); si no la hay, de `LEGATUS_AGENT` (el valor por defecto del lanzador); y si tampoco, `unknown`. `Harness` se detecta a partir del entorno (`LEGATUS_HARNESS` tiene prioridad). `Host` es el nombre corto de la máquina.

Los ids de sesión se resuelven en este orden: `LEGATUS_SESSION`, `CLAUDE_CODE_SESSION_ID`, `CLAUDE_SESSION_ID`, `CODEX_THREAD_ID`. El Observatorio, los trailers de git y los traspasos usan la misma marca para ese id, así que un cambio de personaje dentro de una sesión se atribuye bien en todas partes. Un arranque simple con `codex` o `claude` (sin lanzador) pregunta qué legatus; tras la respuesta, `obs.py agent <name>` lo fija.

Comprobaciones sin conexión (sin harness, sin modelo, sin red, sin escrituras en git): `python3 -B tools/legati/test_identity.py` y `python3 -B tools/legati/test_state.py`.

## Qué vive dónde

| | en git (viaja entre máquinas) | por máquina (nunca va en un commit) |
|---|---|---|
| Commits con trailers | ✓ | |
| `legati/handoffs/*.md` y `archive/` | ✓ | |
| Callouts de carril en los ficheros `BACKLOG.md` | ✓ | |
| Marcas de lectura de «desde la última vez», de la bandeja y del chat | | `.legati-state/` |
| Eventos, presencia, bloqueos y chat del Observatorio | | `.observatory/` |
| Conexión de los hooks de Codex y configuración de proyecto | | `.codex/` |
| Añadidos por máquina de Claude Code | | `.claude/settings.local.json` |

## Cuando un pull da conflicto

Pasará de vez en cuando con los ficheros de índice compartidos (`MEMORY.md`, `INDEX.md`, un `BACKLOG.md`). Regla de resolución: **conserva las líneas de los dos lados** y después `git add <file> && git rebase --continue && bash tools/git/sync.sh push`. Los carriles hacen que esto sea raro. En caso de duda, `git rebase --abort` y pregunta al principal.

## Tu remoto

Para que algo de esto viaje entre máquinas, el taller necesita un remoto **privado** propio. Un clon recién hecho del andamiaje público sigue apuntando a él: el inicio de sesión se salta entonces el pull y `sync.sh push` se niega, hasta que apuntes `origin` a tu propio repositorio (`skills/start-here.md`, paso 6).

## Codex dentro de su sandbox

Codex ejecuta los comandos de shell en un sandbox que quizá no pueda escribir en `.git` desde un hook. El hook de inicio imprime entonces un resumen local y dice «Git refresh deferred»; el legatus lo completa con `bash tools/legati/session-start.sh --refresh` mediante el flujo de aprobación de Codex (el apéndice de Codex de `AGENTS.md` explica cómo). `--local` fuerza el resumen local en cualquier harness. El `.codex/config.toml` generado mantiene `workspace-write` con red y aprobaciones `on-request`; no lo amplíes.
