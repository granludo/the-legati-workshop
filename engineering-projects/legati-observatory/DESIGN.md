# Observatorio de los legati: DISEÑO

## El cuadro en un párrafo

Tres capas, con un cortafuegos de portabilidad estricto entre ellas. Los **adaptadores de captura** (específicos de cada harness, intercambiables) traducen lo que emita un harness a **nuestro esquema de eventos** y lo añaden a un simple **registro de eventos**. El registro de eventos + dos diminutos directorios de estado (presencia, bloqueos) forman el **núcleo portable**: no saben nada de ningún harness concreto. Los **renderizadores estáticos** leen ese núcleo y generan artefactos listos para una captura de pantalla (un dashboard en markdown y un HTML interactivo en un solo fichero). Sin servidor, sin base de datos, sin nube. La coordinación entre agentes es **estigmérgica**: los agentes escriben rastros de presencia y de bloqueo y leen los de los demás, sin orquestador.

## Decisiones de diseño

1. **Estático, no un servidor.** Registro de eventos de solo anexado → artefactos estáticos renderizados a demanda. (Por qué no un servidor web: un proceso en marcha + un puerto + código no portable + una superficie de confianza en una base de datos en la nube. La vista en vivo, si algún día se quiere, será un front-end `--watch` opcional, nunca el núcleo.)
2. **Captura = adaptador de hooks del harness + autoinforme.** Un adaptador de hooks para el rastro automático; una pequeña CLI `obs` para lo que solo sabe el agente (la tarea actual, los bloqueos). `ADAPTERS.md` documenta el esquema + un adaptador de Claude Code resuelto, para que portarlo a otro harness sea mecánico.
3. **Alcance de agente a agente en la v0 = presencia + bloqueos consultivos.** Los traspasos estructurados quedan aplazados hasta que haya casos de uso concretos.
4. **Política de git:** **todo `.observatory/` está en el gitignore** (eventos, presencia, bloqueos), **y también** los dashboards renderizados. El estado depende de la máquina; versionar un `dashboard.md` compartido entre máquinas sería un generador de conflictos de merge. El renderizador escribe **un `dashboard-<hostname>.md` por máquina**. Si algún día se quiere una instantánea docente en git, fuerza el add de ese único fichero a propósito.

## El cortafuegos de portabilidad (el corazón del asunto)

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

La CLI del núcleo (`obs`) y los renderizadores no importan **nada** específico de un harness. Cambiar de harness = escribir un adaptador nuevo que emita el mismo esquema. Es el cortafuegos entre la capa duradera y el andamiaje: el andamiaje (la configuración de hooks de un harness) es desechable; la capa duradera (esquema + núcleo) nunca depende de él.

## Esquema de eventos (el contrato, v0)

Un objeto JSON por línea, solo de anexado. Mínimo a propósito; se ampliará más adelante.

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

`agent` + `parent_session_id` dan «quién hace qué» y «quién orquesta a quién». `project` + `cost_usd` dan el coste por proyecto.

## Disposición de ficheros

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

Tanto `.observatory/` como el `render/` visible están en el gitignore (dependen de la máquina). El dashboard vive FUERA del directorio oculto porque algunos editores (p. ej., Obsidian) no muestran los directorios que empiezan por punto.

## Presencia

Cada sesión activa escribe o actualiza `sessions/<session_id>.json`:
```json
{ "agent":"orchestrator","host":"your-host","cwd":"...","started":"...","last_seen":"...","current_task":"scaffolding the observatory" }
```
`last_seen` se actualiza con cada evento (hook) y con `obs heartbeat`. Una sesión cuyo `last_seen` tenga más de `STALE_MINUTES` (10 por defecto) se muestra como **inactiva/muerta**. `current_task` lo fija el agente con `obs task "..."`: el «qué estoy haciendo» legible por humanos que solo sabe el agente.

`obs who` → imprime las sesiones activas (quién, dónde, haciendo qué). **Es la primitiva de conciencia del entorno** a la que llama un agente antes de una operación arriesgada.

## Bloqueos consultivos (la parte que acaba con el fallo de carrera)

El fallo que esto resuelve: dos instancias regeneran a la vez el mismo fichero compartido (un dashboard, un índice) → «file modified since read» → escrituras parciales.

Protocolo:
- `obs lock acquire <slug> --task "..." --ttl 15`
  → crea `locks/<slug>.lock` de forma **atómica** (con `O_CREAT|O_EXCL`: la creación exclusiva atómica **es** el mutex; no es un comprobar y luego escribir). Contenido: sesión propietaria, agent, ts, ttl, task.
  → si el fichero ya existe y está **vivo** (dentro del ttl), la adquisición **falla** y devuelve el propietario actual.
- `obs lock check <slug>` → propietario vivo o libre.
- `obs lock release <slug>` → lo elimina (solo debería hacerlo el propietario).
- Al vencer el TTL, un bloqueo cuyo propietario se ha caído se libera solo (sin interbloqueo).

**Alcance honesto:** el bloqueo es **consultivo**: el sistema operativo no detiene a quien escribe sin cooperar; los agentes lo respetan por una disciplina escrita en tu guía de agentes. Pero como la adquisición usa creación exclusiva atómica, **dos agentes que cooperan no pueden ganar los dos el mismo bloqueo**, y eso cierra la carrera real. La regla de disciplina que hay que escribir: «antes de regenerar cualquier fichero compartido, haz `obs lock acquire` sobre él; si la adquisición falla, informa del propietario vivo y retírate».

## Renderizadores: estáticos

`obs render` lee el núcleo y escribe `render/dashboard-<host>.md`:
- **Tabla de presencia**: quién está activo, máquina, cwd/proyecto, tarea actual, tiempo desde la última señal.
- **Bloqueos activos**: slug, propietario, tarea, ttl restante.
- **Actividad reciente**: los últimos N eventos, por sesión.
- **Coste por proyecto**: tabla.
- **Orquestación**: grafo padre→hijo de sesiones y subagentes como **diagrama de flujo Mermaid en línea** (estilo de nodo según esté vivo o inactivo).

Se regenera a demanda (y, opcionalmente, con un hook pre-commit de git o un vigilante de ficheros). Markdown/HTML estático = se ve en un editor, se mete en un screencast, se hace commit sin problemas.

Dos superficies de renderizado:
- **Markdown** (`render/dashboard-<host>.md`): la vista rápida, con las sesiones activas, los bloqueos, la actividad y el coste del día y el grafo de orquestación en Mermaid.
- **HTML** (`render/dashboard-<host>.html`, con `--html`): un único fichero autocontenido, con los datos de eventos incrustados como JSON + JS sin frameworks → **zoom interactivo en el navegador** (rango temporal ahora/hoy/7d/30d/todo, filtros de agente/proyecto/búsqueda, detalle por sesión, barras de coste). Sigue siendo estático: sin servidor, sin nube, sin CDN.

Cada renderizado escribe además una copia con marca de tiempo en `render/history/`.

## Alcance de la construcción

1. Disposición de `.observatory/` + `.gitignore`.
2. CLI `obs` (Python, solo biblioteca estándar, 3.9+): `emit`, `task`, `heartbeat`, `who`, `agent`, `lock {acquire,check,release}`, `render`.
3. Hook handler de `adapters/claude-code/` + `ADAPTERS.md` (contrato del esquema + configuración de CC resuelta + cómo portarlo).
4. Renderizadores estáticos → `render/dashboard-<host>.md` (+ `--html`).
5. Regla de disciplina en tu guía de agentes (bloquear antes de una escritura compartida).

Después de la v1: exportación del coste a SVG/PNG, una vista en vivo `--watch` opcional, traspasos estructurados de agente a agente.
