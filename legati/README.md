# legati/: treballar junts entre sessions, màquines i harness

Diverses sessions de legati poden treballar en aquest repositori alhora: dues pestanyes de terminal en una màquina, un portàtil i un ordinador de taula, Claude Code al costat de Codex. Res d'aquí dona per fet un sol harness. El context i les lliçons són a [good-practices/08-many-legati-many-harnesses.md](../good-practices/08-many-legati-many-harnesses.md); aquest fitxer és el manual d'operacions.

## La idea en un paràgraf

**Git és el bus.** Cada commit és un esdeveniment amb data, hora i autoria que qualsevol sessió llegeix després d'un pull; els traspassos són fitxers que viatgen dins dels commits; reservar un carril és fer un commit al backlog del projecte. Les diferents màquines tenen arbres de treball separats; els terminals d'una mateixa màquina poden compartir un sol checkout. Les sessions de la mateixa màquina tenen, a més, la presència en directe, els bloquejos i el xat de l'Observatori dels legati (`engineering-projects/legati-observatory/`); això no travessa mai d'una màquina a una altra i res d'aquí no en depèn.

## Les quatre regles

1. **Totes les escriptures a git passen per `tools/git/sync.sh`.** Només staging limitat als camins indicats (mai `-A`, mai `.`), trailers `Legatus:` / `Harness:` / `Host:` afegits automàticament, rebase sobre origin i push immediat. Un commit sense push no existeix per als altres. A macOS, el rebase treu el flag immutable (`uchg`) dels fitxers que ha de reescriure i el torna a posar després.
   ```bash
   bash tools/git/sync.sh commit -m "Subject line" -- path/one.md path/two.md
   bash tools/git/sync.sh status | pull | push | log | whoami
   ```
2. **Reserva el carril abans de treballar en un projecte.** `python3 tools/legati/lane.py claim <project-dir> "<task>"` posa un callout `> [!lane]` a dalt de tot del `BACKLOG.md` d'aquell projecte i en fa push. `lane.py list` mostra tots els carrils actius; una reserva d'algú altre de menys de 24 hores vol dir fer-se enrere o coordinar-se. `lane.py release <project-dir>` quan acabis.
3. **Els missatges són fitxers, un per missatge.** `python3 tools/legati/handoff.py send --to writer --subject "…" --body "…"` escriu `legati/handoffs/<timestamp>_<from>_to_<to>_<slug>.md` i en fa push. Els destinataris el veuen amb `handoff.py inbox` i l'arxiven amb `handoff.py ack <file>` (es mou a `legati/handoffs/archive/YYYY-MM/`, amb commit). `--to all` l'envia a tothom; els lectors avancen un marcador local en lloc d'arxivar-lo. Un fitxer per missatge és el que evita que dos remitents entrin mai en conflicte a la mateixa línia.
4. **Inici de sessió = mira abans de tocar.** `bash tools/legati/host-section.sh` imprimeix la secció d'aquesta màquina de `memory/reference_hosts.md`. `tools/legati/session-start.sh` fa fetch, fa pull només quan l'arbre és net i no hi ha cap commit local, i llista els commits des de l'última vegada que aquesta màquina i aquest harness hi van mirar, els carrils actius i els traspassos no llegits. `tools/legati/turn-start.sh` fa aflorar els traspassos nous abans de cada prompt. Tots dos tenen hook a Claude Code (`.claude/settings.json` versionat) i a Codex (`install-hooks.sh codex`).

## Arrencar un legatus

| | Claude Code | Codex |
|---|---|---|
| Un legatus en aquesta pestanya | `./claude_<name>.sh` | `./codex_<name>.sh` |
| Què executa | `legati/bin/legatus <name> claude-code` | `legati/bin/legatus <name> codex` |
| Com arriba el fitxer d'arrencada | s'afegeix al prompt de sistema | Codex llegeix `AGENTS.md` de manera nativa; el prompt inicial anomena el fitxer d'arrencada |
| Configuració inicial, una vegada per màquina | confia en la carpeta quan t'ho demani | `codex login`, `bash tools/legati/install-hooks.sh codex`, aprova `/hooks` una vegada |

- El llançador defineix `LEGATUS_AGENT` i `LEGATUS_HARNESS`, posa nom a la pestanya del terminal i engega el harness a l'arrel del repositori. Per a Codex també defineix un `LEGATUS_SESSION` únic, perquè dues pestanyes de Codex simultànies no comparteixin mai identitat.
- **Dos legati en una pestanya:** `legati/bin/legatus comms --with reviewer` (o `comms+reviewer`). S'exporta `LEGATUS_COMPANIONS`, la pestanya es titula `COMMS+REVIEWER` i els dos fitxers d'arrencada es carreguen darrere d'una nota d'aparellament: el titular respon per defecte; el company, dins el seu carril; cadascun amb el seu prefix.
- **Harness i model per defecte de cada legatus:** `legati/roster.toml`. Els embolcalls de l'arrel indiquen el harness explícitament; `legati/bin/legatus <name>` sol fa servir el roster.
- **Legatus nou o reanomenat:** `bash tools/legati/make-launchers.sh` regenera els embolcalls a partir de `characters/*/boot.md`.
- **Prova en sec:** `LEGATUS_DRY_RUN=1 ./codex_writer.sh` imprimeix l'ordre sense llançar-la.
- Els arguments addicionals van al harness: `./codex_reviewer.sh -m <model>`, `./claude_writer.sh --model <model>`.

## Identitat

`Legatus` surt del marcador per sessió de l'Observatori (`obs.py agent <name>` l'escriu en un canvi de personatge); si no n'hi ha, de `LEGATUS_AGENT` (el valor per defecte del llançador); si no, `unknown`. `Harness` es detecta a partir de l'entorn (`LEGATUS_HARNESS` té preferència). `Host` és el nom curt de la màquina.

Els identificadors de sessió es resolen en aquest ordre: `LEGATUS_SESSION`, `CLAUDE_CODE_SESSION_ID`, `CLAUDE_SESSION_ID`, `CODEX_THREAD_ID`. L'Observatori, els trailers de git i els traspassos fan servir el mateix marcador per a aquest identificador, de manera que un canvi de personatge dins d'una sessió s'atribueix correctament a tot arreu. Un inici simple de `codex` o `claude` (sense llançador) pregunta quin legatus; després de la resposta, `obs.py agent <name>` el fixa.

Comprovacions fora de línia (sense harness, sense model, sense xarxa, sense escriptures a git): `python3 -B tools/legati/test_identity.py` i `python3 -B tools/legati/test_state.py`.

## Què viu on

| | a git (travessa màquines) | per màquina (mai amb commit) |
|---|---|---|
| Commits amb trailers | ✓ | |
| `legati/handoffs/*.md` i `archive/` | ✓ | |
| Callouts de carril als fitxers `BACKLOG.md` | ✓ | |
| Marcadors de lectura («des de l'última mirada», safata, xat) | | `.legati-state/` |
| Esdeveniments, presència, bloquejos i xat de l'Observatori | | `.observatory/` |
| Connexió dels hooks de Codex i configuració del projecte | | `.codex/` |
| Afegits per màquina de Claude Code | | `.claude/settings.local.json` |

## Quan un pull entra en conflicte

Passarà, de tant en tant, als fitxers d'índex compartits (`MEMORY.md`, `INDEX.md`, un `BACKLOG.md`). Regla de resolució: **conserva les línies de tots dos costats**, i després `git add <file> && git rebase --continue && bash tools/git/sync.sh push`. Els carrils fan que passi poc. Si dubtes, `git rebase --abort` i pregunta al principal.

## El teu remot

El taller necessita un remot **privat** propi perquè res d'això travessi màquines. Un clon acabat de fer de la bastida pública encara hi apunta: aleshores l'inici de sessió se salta el pull i `sync.sh push` s'hi nega, fins que facis apuntar `origin` al teu propi repositori (`skills/start-here.md`, pas 6).

## Codex dins del seu sandbox

Codex executa les ordres de shell en un sandbox que potser no pot escriure `.git` des d'un hook. Aleshores el hook d'inici imprimeix un resum local i diu «Git refresh deferred»; el legatus el completa amb `bash tools/legati/session-start.sh --refresh` a través del flux d'aprovació de Codex (l'apèndix de Codex d'`AGENTS.md` explica com). `--local` força el resum local en qualsevol harness. El `.codex/config.toml` generat manté `workspace-write` amb xarxa i aprovacions `on-request`; no l'eixamplis.
