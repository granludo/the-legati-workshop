# Observatori dels Legati: DESIGN

## La imatge en un paràgraf

Tres capes, amb un tallafoc de portabilitat estricte entre elles. Els **adaptadors de captura** (específics de cada harness, intercanviables) tradueixen el que emeti un harness al **nostre esquema d'esdeveniments** i ho afegeixen a un **registre d'esdeveniments** pla. El registre d'esdeveniments + dos directoris d'estat minúsculs (presència, bloquejos) són el **nucli portable**: no saben res de cap harness concret. Els **generadors estàtics** llegeixen aquest nucli i produeixen artefactes a punt per a una captura de pantalla (un dashboard en markdown i un HTML interactiu d'un sol fitxer). Sense servidor, sense base de dades, sense núvol. La coordinació entre agents és **estigmèrgica**: els agents escriuen rastres de presència i de bloqueig i llegeixen els dels altres, sense cap orquestrador.

## Decisions de disseny

1. **Estàtic, no un servidor.** Registre d'esdeveniments de només addició → generació d'artefactes estàtics a demanda. (Per què no un servidor web: un procés en marxa + un port + codi no portable + la superfície de confiança d'una base de dades al núvol. Si mai es vol el temps real, serà una interfície `--watch` opcional, mai el nucli.)
2. **Captura = adaptador de hooks del harness + autoinforme.** Un adaptador de hooks per al rastre automàtic; una CLI `obs` petita per a les coses que només sap l'agent (tasca actual, bloquejos). `ADAPTERS.md` documenta l'esquema + un adaptador de Claude Code d'exemple, perquè portar-lo a un altre harness sigui mecànic.
3. **Abast d'agent a agent v0 = presència + bloquejos consultius.** Els traspassos estructurats s'ajornen fins que hi hagi casos d'ús concrets.
4. **Política de git:** **git ignora tot `.observatory/`** (esdeveniments, presència, bloquejos), i també els dashboards generats. L'estat depèn de la màquina; versionar un `dashboard.md` compartit entre màquines seria una font de conflictes de merge. El generador escriu **un `dashboard-<hostname>.md` per màquina**. Si mai es vol una instantània docent a git, afegeix-la expressament forçant aquell únic fitxer.

## El tallafoc de portabilitat (el cor de tot)

```
 [ Claude Code ]        [ Codex / future ]         ← harnesses
        │                       │
   adapters/claude-code   adapters/<harness>        ← the ONLY harness-aware code
        │                       │
        └────────► our event schema ◄──────────┘    ← the contract (ADAPTERS.md)
                          │
              .observatory/  (event log + presence + locks)   ← PORTABLE CORE
                          │
                  obs render (static)                          ← renderers
                          │
              render/dashboard-<host>.md / .html               ← artifacts
```

La CLI del nucli (`obs`) i els generadors no importen **res** específic de cap harness. Canviar de harness = escriure un adaptador nou que emeti el mateix esquema. Aquest és el tallafoc entre la capa duradora i la bastida: la bastida (la configuració de hooks d'un harness) és d'un sol ús; la capa duradora (esquema + nucli) mai no en depèn.

## Esquema d'esdeveniments (el contracte, v0)

Un objecte JSON per línia, de només addició. Mínim a propòsit; ja s'ampliarà.

```json
{
  "ts": "2026-06-01T13:35:00+02:00",
  "session_id": "abc123",
  "agent": "orchestrator",              // legatus name (your persona name|unknown)
  "host": "your-host",
  "cwd": "/path/to/your-workspace",
  "project": "legati-observatory",      // derived from cwd, best-effort
  "type": "tool_use",                   // session_start|tool_use|file_touch|heartbeat|session_end
  "tool": "Edit",                       // when type=tool_use
  "target": "engineering-projects/.../DESIGN.md",  // file path when relevant
  "parent_session_id": null,            // set for subagents → orchestration tree
  "model": "claude-opus-4-8",
  "tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0  // best-effort, when the adapter has them
}
```

`agent` + `parent_session_id` donen «qui fa què» i «qui orquestra qui». `project` + `cost_usd` donen el cost per projecte.

## Organització dels fitxers

```
.observatory/                      # hidden, machine state — gitignored
  events/2026-06-01.jsonl          # append-only event log (per-day file)
  sessions/<session_id>.json       # presence/heartbeat
  sessions/<session_id>.agent      # active-legatus marker (set by `obs agent`)
  locks/<slug>.lock                # advisory claims

engineering-projects/legati-observatory/render/   # visible (Obsidian-friendly), gitignored
  dashboard-<host>.md              # the human-readable dashboard
  history/dashboard-<host>-<ts>.md # timestamped snapshot per render
  # (orchestration graph is an inline Mermaid block inside dashboard-<host>.md)
```

Tant `.observatory/` com el `render/` visible estan ignorats per git (depenen de la màquina). El dashboard viu FORA del directori ocult perquè alguns editors (per exemple, Obsidian) no mostren els directoris que comencen amb punt.

## Presència

Cada sessió activa escriu o actualitza `sessions/<session_id>.json`:
```json
{ "agent":"orchestrator","host":"your-host","cwd":"...","started":"...","last_seen":"...","current_task":"scaffolding the observatory" }
```
`last_seen` s'actualitza a cada esdeveniment (hook) i amb `obs heartbeat`. Una sessió amb un `last_seen` més antic que `STALE_MINUTES` (per defecte, 10) es mostra com a **inactiva o morta**. `current_task` el defineix l'agent amb `obs task "..."`: el «què estic fent» llegible per humans que només sap l'agent.

`obs who` → imprimeix les sessions actives (qui, on, fent què). **Aquesta és la primitiva de consciència** que un agent crida abans d'una operació arriscada.

## Bloquejos consultius (la part que acaba amb l'error de competència)

La fallada que això resol: dues instàncies regeneren alhora el mateix fitxer compartit (un dashboard, un índex) → «file modified since read» → escriptures parcials.

Protocol:
- `obs lock acquire <slug> --task "..." --ttl 15`
  → crea **atòmicament** `locks/<slug>.lock` (amb `O_CREAT|O_EXCL`: la creació exclusiva atòmica és el mateix mutex, no pas una comprovació seguida d'una escriptura). Contingut: sessió propietària, agent, ts, ttl, tasca.
  → si el fitxer ja existeix i és **viu** (dins el ttl), l'adquisició **falla** i torna el propietari actual.
- `obs lock check <slug>` → propietari viu o lliure.
- `obs lock release <slug>` → l'elimina (només l'hauria de fer el propietari).
- L'expiració del TTL allibera sol un bloqueig el propietari del qual ha caigut (no hi ha interbloqueig).

**Abast honest:** el bloqueig és consultiu: el sistema operatiu no atura un escriptor que no coopera; els agents el respecten per una disciplina escrita a la guia del teu agent. Però com que l'adquisició fa servir la creació exclusiva atòmica, **dos agents que cooperen no poden guanyar tots dos el mateix bloqueig**, i això tanca la competència real. La regla de disciplina que cal escriure: **abans de regenerar qualsevol fitxer compartit, fes-ne `obs lock acquire`; si l'adquisició falla, fes visible el propietari actiu i retira't.**

## Generadors: estàtics

`obs render` llegeix el nucli i escriu `render/dashboard-<host>.md`:
- **Taula de presència**: qui és actiu, màquina, cwd/projecte, tasca actual, temps des de l'última activitat.
- **Bloquejos actius**: slug, propietari, tasca, ttl restant.
- **Activitat recent**: els últims N esdeveniments, per sessió.
- **Cost per projecte**: taula.
- **Orquestració**: graf pare→fill de sessions i subagents com a **diagrama de flux Mermaid en línia** (amb estil de node viu o inactiu).

Es regenera a demanda (i, opcionalment, amb un hook de pre-commit de git o un observador de fitxers). Markdown o HTML estàtic = es veu en un editor, es pot posar en un screencast i fa commits nets.

Dues superfícies de sortida:
- **Markdown** (`render/dashboard-<host>.md`): la vista d'un cop d'ull: sessions actives, bloquejos, activitat i cost d'avui, graf d'orquestració en Mermaid.
- **HTML** (`render/dashboard-<host>.html`, amb `--html`): un fitxer únic autònom: dades dels esdeveniments incrustades com a JSON + JS pur → **zoom interactiu al navegador** (interval de temps ara/avui/7d/30d/tot, filtres per agent, projecte o cerca, detall per sessió, barres de cost). Continua sent estàtic: sense servidor, sense núvol, sense CDN.

Cada generació també escriu una còpia amb marca de temps a `render/history/`.

## Abast de la construcció

1. Organització de `.observatory/` + `.gitignore`.
2. CLI `obs` (Python, només biblioteca estàndard, 3.9+): `emit`, `task`, `heartbeat`, `who`, `agent`, `lock {acquire,check,release}`, `render`.
3. Gestor de hooks `adapters/claude-code/` + `ADAPTERS.md` (contracte d'esquema + configuració de CC d'exemple + com portar-lo).
4. Generadors estàtics → `render/dashboard-<host>.md` (+ `--html`).
5. Regla de disciplina a la guia del teu agent (bloquejar abans d'escriure un fitxer compartit).

Després de la v1: exportació del cost en SVG/PNG, una vista en temps real `--watch` opcional, traspassos estructurats d'agent a agent.
