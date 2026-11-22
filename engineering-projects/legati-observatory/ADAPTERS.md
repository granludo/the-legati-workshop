# ADAPTERS: el contracte de portabilitat

L'Observatori dels Legati es manté portable perquè **el nucli (`obs.py` + els generadors) no sap res de cap harness.** Tot el coneixement específic de cada harness viu a `adapters/<harness>/`, i la seva única feina és traduir els esdeveniments d'aquell harness a **un sol esquema**. Canvies de harness → escrius un adaptador → fet.

## L'esquema d'esdeveniments (el contracte)

Un objecte JSON per línia, afegit a `.observatory/events/<YYYY-MM-DD>.jsonl`. Obligatoris: `ts`, `session_id`, `agent`, `host`, `cwd`, `project`, `type`. Opcionals, quan se saben: `tool`, `target`, `parent_session_id`, `model`, `tokens_in`, `tokens_out`, `cost_usd`, `harness` (`claude-code` | `codex` | …, perquè els dashboards puguin distingir els cossos; el legatus continua sent `agent`).

```json
{"ts":"2026-06-01T18:07:30+02:00","session_id":"abc123","agent":"orchestrator",
 "host":"your-host","cwd":"/path/to/your-workspace","project":"legati-observatory",
 "type":"tool_use","tool":"Edit","target":"obs.py","parent_session_id":null,
 "model":"claude-opus-4-8","tokens_in":0,"tokens_out":0,"cost_usd":0.0}
```

Vocabulari de `type`: `session_start` · `prompt` · `tool_use` · `tool_result` · `subagent_stop` · `session_end` · `task` · `notification` · `say` (una línia de xat dins la mateixa màquina; el text viu a `.observatory/chat/`). Un adaptador pot emetre esdeveniments important `obs` i cridant `obs.append_event(record)` (el que es fa aquí) o executant `obs.py emit …` al shell.

La **identitat** la resol el nucli a partir de l'entorn (així no depèn del harness):
- `LEGATUS_AGENT`: quin legatus (el nom de la teva persona); per defecte, `unknown`.
- `LEGATUS_SESSION`: identificador de sessió estable; si no hi és, recorre a `CLAUDE_CODE_SESSION_ID`, `CLAUDE_SESSION_ID`, `CODEX_THREAD_ID` i, finalment, `host-ppid`.

**Atribució per persona.** Si el teu taller canvia de persona dins una mateixa sessió, un `LEGATUS_AGENT` estàtic ho etiquetaria tot malament. La solució fa servir l'identificador de sessió que el harness exposa **tant** a l'eina Bash **com** als hooks (per a Claude Code, `CLAUDE_CODE_SESSION_ID`), de manera que un `obs agent <name>` executat com a eina Bash i el gestor de hooks resolen la **mateixa** sessió. Precedència per a `agent`: un marcador per sessió (`.observatory/sessions/<sid>.agent`, escrit per `obs agent <name>`) **preval sobre** el valor per defecte de l'entorn. Així doncs: defineix `env.LEGATUS_AGENT` com a valor per defecte de la sessió, i fes que cada persona executi `obs agent <name>` quan hi canviïs; a partir d'aleshores, els esdeveniments d'eina capturats s'atribueixen al legatus actiu fins al canvi següent. `session_id()` resol `LEGATUS_SESSION` → `CLAUDE_CODE_SESSION_ID` → `CLAUDE_SESSION_ID` → `CODEX_THREAD_ID` → `host-ppid`. Codex exposa `CODEX_THREAD_ID` a les eines de shell, i coincideix amb l'identificador de sessió del contingut del hook. El marcador s'escriu sota cada identificador amb què es coneix la sessió, de manera que el nom sobreviu quan l'entorn del llançador ja no hi és. Els trailers de git i els traspassos fan servir la mateixa precedència.

## Adaptador de Claude Code (l'exemple resolt)

`adapters/claude-code/hook-handler.py` llegeix el JSON del hook de CC des de stdin, associa `hook_event_name` → el nostre `type`, extreu `tool_name` / `tool_input.file_path` → `tool` / `target`, i ho registra a través del nucli. **Surt amb 0 en tots els camins: mai no pot bloquejar una sessió.**

Per instal·lar-lo en una màquina, afegeix els hooks al **`~/.claude/settings.json`** d'aquella màquina (o al `.claude/settings.json` del projecte). El `.claude/settings.json` del repositori ja els connecta fent servir `$CLAUDE_PROJECT_DIR`, de manera que un clon nou captura esdeveniments des del primer moment. La forma manual:

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

Comprova-ho amb `python3 …/obs.py render` i obre `engineering-projects/legati-observatory/render/dashboard-<host>.md`.

## Adaptador de Codex

`adapters/codex/hook-handler.py`: els hooks de Codex envien per stdin un JSON amb la mateixa forma que els de Claude Code, de manera que la portabilitat es redueix al mapa d'esdeveniments (Codex hi afegeix `SessionEnd`, `PermissionRequest`, `Interrupt`, `PreCompact`/`PostCompact`, `SubagentStart`) més l'extracció del destí a partir dels pegats d'`apply_patch`. S'instal·la a cada màquina amb `bash tools/legati/install-hooks.sh codex` a `<repo>/.codex/hooks.json` (ignorat per git, amb camins absoluts); Codex només executa els hooks del projecte quan el repositori és de confiança a `~/.codex/config.toml` i cada hook s'ha aprovat una vegada pel seu hash (`/hooks`). El llançador defineix un `LEGATUS_SESSION` estable per a les execucions de Codex, perquè l'`obs agent` de l'eina de shell i el gestor de hooks resolguin la mateixa sessió.

## Com portar-lo a un altre harness (pi, Cursor, …)

1. Copia `adapters/claude-code/` → `adapters/<harness>/`.
2. Reescriu **només** l'associació de camps a `hook-handler.py`: associa els noms d'esdeveniment d'aquell harness → el vocabulari de `type` d'abans, i els seus camps d'eina i de fitxer → `tool`/`target`. Mantén la disciplina de fallar en silenci i sortir amb 0.
3. Connecta'l al mecanisme de hooks o d'esdeveniments d'aquell harness (el seu equivalent de `settings.json`).
4. No canvia res a `obs.py` ni al generador. Si el harness nou no pot emetre alguns camps (cost, tokens), omet-los: tots són opcionals.

Aquest és tot el tallafoc: els harness van i vénen; l'esquema i el nucli es queden.
