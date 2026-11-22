# ADAPTERS: el contrato de portabilidad

El Observatorio de los legati sigue siendo portable porque **el núcleo (`obs.py` + los renderizadores) no sabe nada de ningún harness.** Todo el conocimiento específico de un harness vive en `adapters/<harness>/`, y su único trabajo es traducir los eventos de ese harness a **un solo esquema**. Cambias de harness → escribes un adaptador → listo.

## El esquema de eventos (el contrato)

Un objeto JSON por línea, añadido al final de `.observatory/events/<YYYY-MM-DD>.jsonl`. Obligatorios: `ts`, `session_id`, `agent`, `host`, `cwd`, `project`, `type`. Opcionales, cuando se conocen: `tool`, `target`, `parent_session_id`, `model`, `tokens_in`, `tokens_out`, `cost_usd`, `harness` (`claude-code` | `codex` | …, para que los dashboards distingan los cuerpos; el legatus sigue siendo `agent`).

```json
{"ts":"2026-06-01T18:07:30+02:00","session_id":"abc123","agent":"orchestrator",
 "host":"your-host","cwd":"/path/to/your-workspace","project":"legati-observatory",
 "type":"tool_use","tool":"Edit","target":"obs.py","parent_session_id":null,
 "model":"claude-opus-4-8","tokens_in":0,"tokens_out":0,"cost_usd":0.0}
```

Vocabulario de `type`: `session_start` · `prompt` · `tool_use` · `tool_result` · `subagent_stop` · `session_end` · `task` · `notification` · `say` (una línea de chat en la misma máquina; el texto vive en `.observatory/chat/`). Un adaptador puede emitir de dos maneras: importando `obs` y llamando a `obs.append_event(record)` (lo que se hace aquí) o lanzando `obs.py emit …` desde el shell.

**La identidad** la resuelve el núcleo a partir del entorno (así no depende del harness):
- `LEGATUS_AGENT`: qué legatus (el nombre de tu persona); por defecto, `unknown`.
- `LEGATUS_SESSION`: id de sesión estable; si falta, se usa `CLAUDE_CODE_SESSION_ID`, `CLAUDE_SESSION_ID`, `CODEX_THREAD_ID` y, por último, `host-ppid`.

**Atribución por persona.** Si tu taller cambia de persona **dentro** de una misma sesión, un `LEGATUS_AGENT` estático lo etiquetaría todo mal. La solución usa el id de sesión que el harness expone **tanto** a la herramienta Bash **como** a los hooks (en Claude Code, `CLAUDE_CODE_SESSION_ID`), de modo que un `obs agent <name>` ejecutado como herramienta Bash y el hook-handler resuelven la **misma** sesión. Precedencia para `agent`: un marcador por sesión (`.observatory/sessions/<sid>.agent`, escrito por `obs agent <name>`) **prevalece sobre** el valor por defecto del entorno. Así que: define `env.LEGATUS_AGENT` como valor por defecto de la sesión y haz que cada persona ejecute `obs agent <name>` al cambiar; a partir de ahí, los eventos de herramientas capturados se atribuyen al legatus activo hasta el siguiente cambio. `session_id()` resuelve `LEGATUS_SESSION` → `CLAUDE_CODE_SESSION_ID` → `CLAUDE_SESSION_ID` → `CODEX_THREAD_ID` → `host-ppid`. Codex expone `CODEX_THREAD_ID` a las herramientas de shell, y coincide con el id de sesión del payload del hook. El marcador se escribe con cada id por el que se conoce la sesión, así que el nombre sobrevive cuando desaparece el entorno del lanzador. Los trailers de git y los traspasos usan la misma precedencia.

## Adaptador de Claude Code (el ejemplo resuelto)

`adapters/claude-code/hook-handler.py` lee por stdin el JSON del hook de CC, traduce `hook_event_name` → nuestro `type`, saca `tool_name` / `tool_input.file_path` → `tool` / `target` y lo registra a través del núcleo. **Sale con 0 en todos los caminos: nunca puede bloquear una sesión.**

Se instala en una máquina añadiendo hooks al **`~/.claude/settings.json`** de esa máquina (o al `.claude/settings.json` del proyecto). El `.claude/settings.json` versionado de este repositorio ya los conecta usando `$CLAUDE_PROJECT_DIR`, así que un clon recién hecho captura eventos desde el primer momento. La forma manual:

```jsonc
{
  "hooks": {
    "SessionStart":     [{ "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/engineering-projects/legati-observatory/adapters/claude-code/hook-handler.py\"" }] }],
    "PreToolUse":       [{ "matcher": "*", "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/engineering-projects/legati-observatory/adapters/claude-code/hook-handler.py\"" }] }],
    "PostToolUse":      [{ "matcher": "*", "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/engineering-projects/legati-observatory/adapters/claude-code/hook-handler.py\"" }] }],
    "SubagentStop":     [{ "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/engineering-projects/legati-observatory/adapters/claude-code/hook-handler.py\"" }] }],
    "Stop":             [{ "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/engineering-projects/legati-observatory/adapters/claude-code/hook-handler.py\"" }] }]
  }
}
```

Compruébalo con `python3 …/obs.py render` y abre `engineering-projects/legati-observatory/render/dashboard-<host>.md`.

## Adaptador de Codex

`adapters/codex/hook-handler.py`: los hooks de Codex envían por stdin un JSON con la misma forma que los de Claude Code, así que portarlo se reduce al mapa de eventos (Codex añade `SessionEnd`, `PermissionRequest`, `Interrupt`, `PreCompact`/`PostCompact`, `SubagentStart`) más la extracción del target a partir de los parches de `apply_patch`. Se instala en cada máquina con `bash tools/legati/install-hooks.sh codex`, en `<repo>/.codex/hooks.json` (en el gitignore, con rutas absolutas); Codex solo ejecuta los hooks del proyecto cuando el repositorio es de confianza en `~/.codex/config.toml` y cada hook se ha aprobado una vez por su hash (`/hooks`). El lanzador fija un `LEGATUS_SESSION` estable en las ejecuciones de Codex para que el `obs agent` de la herramienta de shell y el hook handler resuelvan la misma sesión.

## Cómo portarlo a otro harness (pi, Cursor, …)

1. Copia `adapters/claude-code/` → `adapters/<harness>/`.
2. Reescribe **solo** la correspondencia de campos en `hook-handler.py`: traduce los nombres de eventos de ese harness → el vocabulario de `type` de arriba, y sus campos de herramienta y de fichero → `tool`/`target`. Mantén la disciplina de fallar en silencio y salir con 0.
3. Conéctalo al mecanismo de hooks o de eventos de ese harness (su equivalente de `settings.json`).
4. No cambia nada en `obs.py` ni en el renderizador. Si el harness nuevo no puede emitir algunos campos (coste, tokens), omítelos: todos son opcionales.

Ese es todo el cortafuegos: los harnesses van y vienen; el esquema y el núcleo se quedan.
