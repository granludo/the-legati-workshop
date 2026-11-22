---
type: project-folder
project: Legati Observatory
status: en funcionamiento (núcleo portable + adaptadores para Claude Code y Codex)
---

# Observatorio de los legati

Una capa de observabilidad + coordinación ligera, **portable, estática y estigmérgica**, para las sesiones de IA en paralelo de un taller (los *legati*, tus agentes con nombre). Cuando varias instancias de agente trabajan a la vez sobre el mismo repositorio, te dice **quién está activo, qué está haciendo, quién orquesta a quién y cuánto ha costado**, y les da una manera de **no pisarse** al escribir ficheros compartidos.

**Por qué construir uno propio** en vez de instalar un dashboard de terceros: sigue siendo portable entre harnesses (no está atado a una sola herramienta), estático (sin servidor web, sin superficie de confianza en una base de datos en la nube), ajustado al problema de coordinación que de verdad muerde (instancias en paralelo compitiendo por el mismo fichero) y lo bastante legible para servir también como material docente. Es un ejemplo resuelto de **estigmergia frente a orquestación**: los agentes se coordinan **sin orquestador central**, dejando rastros en ficheros compartidos (ficheros de presencia y de bloqueo consultivo a modo de rastros de feromonas) y leyendo el estado del entorno. El repositorio es el termitero.

## Cómo funciona (tres capas, un cortafuegos)

```
 harness hooks  ──►  adapters/<harness>/  ──►  event schema  ──►  .observatory/  ──►  obs render  ──►  dashboard
 (Claude Code,        (the only harness-       (the contract,      (portable core:      (static)         (.md / .html)
  Codex, …)            aware code)              ADAPTERS.md)        events+presence+locks)
```

El núcleo (`obs.py` + los renderizadores) no sabe nada de ningún harness. Para dar soporte a un harness nuevo escribes **un** adaptador que emita el mismo esquema de eventos; no cambia nada más. Consulta [`DESIGN.md`](DESIGN.md) y [`ADAPTERS.md`](ADAPTERS.md).

## Ficheros

| Fichero | Qué es |
|---|---|
| [`obs.py`](obs.py) | La CLI del núcleo portable: `emit` · `task` · `heartbeat` · `who` · `agent` · `lock {acquire,check,release}` · `say` · `chat` · `render`. Solo biblioteca estándar, Python 3.9+. |
| [`DESIGN.md`](DESIGN.md) | El diseño: el cortafuegos de portabilidad, el esquema de eventos, la disposición de ficheros, el protocolo de bloqueos, los renderizadores. |
| [`ADAPTERS.md`](ADAPTERS.md) | El contrato de portabilidad: esquema de eventos + una configuración de hooks de Claude Code resuelta como ejemplo + cómo portarlo a otro harness. |
| [`adapters/claude-code/hook-handler.py`](adapters/claude-code/hook-handler.py) | Adaptador de captura de Claude Code (el código que conoce el harness vive solo en los adaptadores; falla en silencio y sale con 0, así que nunca puede bloquear una sesión). |
| [`adapters/codex/hook-handler.py`](adapters/codex/hook-handler.py) | Adaptador de captura de Codex CLI (el mismo contrato). Se instala en cada máquina con `bash tools/legati/install-hooks.sh codex`. |

El [`.claude/settings.json`](../../.claude/settings.json) versionado ya conecta los cinco eventos de hook de Claude Code con el adaptador usando `$CLAUDE_PROJECT_DIR`, así que un clon recién hecho empieza a capturar en la siguiente sesión. Codex necesita un paso por máquina: `bash tools/legati/install-hooks.sh codex` y, después, aprobar los hooks una vez dentro de Codex con `/hooks`.

## Uso

```bash
OBS=engineering-projects/legati-observatory/obs.py
python3 $OBS agent writer                                       # on persona switch — attribute events to this legatus
python3 $OBS task "what I'm doing"                              # set current task
python3 $OBS who                                               # who's live
python3 $OBS lock acquire dashboards --task "refresh" --ttl 20  # claim before a risky shared write
python3 $OBS lock release dashboards
python3 $OBS render                                            # markdown dashboard -> render/dashboard-<host>.md
python3 $OBS render --html                                     # interactive HTML  -> render/dashboard-<host>.html
python3 $OBS render --html --since 7d                          # HTML embed window: today|7d|30d|all (default 30d)
```

**Dos superficies, las dos estáticas + en el gitignore + por máquina:**
- **Markdown** (`render/dashboard-<host>.md`): la vista rápida, con las sesiones activas, los bloqueos, la actividad y el coste del día y el grafo de orquestación en Mermaid.
- **HTML** (`render/dashboard-<host>.html`): se abre en un navegador (`file://`, sin servidor). Los datos de eventos van incrustados como JSON con JS sin frameworks, así que los **niveles de zoom son interactivos dentro de la página**: rango temporal (ahora / hoy / 7d / 30d / todo), filtro por agente o proyecto, búsqueda de texto libre, clic en una sesión para ver toda su cronología. Las barras de coste + los recuentos se recalculan con cada cambio en los controles.

Todo el estado de la máquina vive en `<repo>/.observatory/` (oculto) y los dashboards renderizados en `render/`, **los dos en el gitignore**, porque dependen de la máquina.

> El grafo de orquestación del HTML usa Mermaid. Para renderizar el grafo sin conexión, deja un `mermaid.min.js` en `engineering-projects/legati-observatory/vendor/` (está en el gitignore). Sin él, el HTML se renderiza igual: el grafo solo aparece como texto, y `obs render --html` imprime la pista.

## Licencia

Consulta el [`LICENSE`](../../LICENSE) del repositorio.
