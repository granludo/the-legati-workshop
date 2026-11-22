# tools/llm: `llm`, la puerta de entrada única

Toda llamada a un modelo que **no** sea el de la sesión (un modelo local para trabajo masivo, un segundo modelo frontera para una opinión independiente, embeddings) pasa por [el comando `llm` de Simon Willison](https://llm.datasette.io). Una sola interfaz de comandos para todos los proveedores, y cada prompt y cada respuesta **quedan registrados en SQLite** automáticamente, así que siempre puedes ver qué se le pidió a qué modelo y qué devolvió. Funciona igual desde Claude Code, desde Codex y desde tu propio terminal.

## Configuración (una vez por máquina)

```bash
uv tool install llm                # or: pipx install llm · brew install llm
llm install llm-ollama             # local models through Ollama (optional)
llm keys set openai                # paste your key; stored in llm's keys.json, outside the repo (optional)
llm models                         # what you can call now
```

Los demás proveedores también son plugins (`llm install llm-anthropic`, `llm install llm-gemini`, `llm install llm-mistral` …). Para un servidor Ollama remoto en tu red: `OLLAMA_HOST=http://desk-machine.local:11434` en el perfil de tu shell. Anota lo que tiene esta máquina en su sección de `memory/reference_hosts.md`.

Los alias mantienen cortos los prompts y hacen explícito el enrutado:

```bash
llm aliases set local qwen3.5:122b # whatever big model your Ollama server runs
llm aliases set second gpt-5       # a frontier model from another family
```

## Uso

```bash
llm -m local 'Summarise this transcript in five bullet points' < transcript.txt
cat draft.md | llm -m second -s 'Review this argument. List the three weakest claims.'
llm embed -m nomic-embed-text -c 'text to embed'
```

Flags habituales: `-s 'system prompt'` · `-o temperature 0.2` · `-o max_tokens 4000` · `-a image.png` (modelos de visión) · `-t <template>`.

## Reglas de enrutado

- **El trabajo interpretativo, sensible a la voz y crítico se queda en el modelo de la sesión.** Eso incluye todo lo que tenga que sonar como el principal.
- **El trabajo mecánico masivo** (clasificación, extracción, resúmenes para uso propio, borradores de traducción de primera pasada en idiomas que el modelo maneja bien) puede ir a un modelo local grande. Prefiere modelos grandes: los pequeños se degradan enseguida con contextos largos y fuera del inglés.
- **Nunca mandes la generación en un idioma a un modelo que lo escribe mal.** Para muchos modelos locales eso significa el catalán, el euskera, el gallego y otras lenguas con menos hablantes: esas se quedan en el modelo de la sesión o en un modelo frontera.
- **Las llamadas de pago cuestan dinero de verdad:** hazlas a conciencia y di, antes de un lote, cuántas llamadas va a hacer.
- **Las llamadas largas siguen la regla de progreso** (`memory/feedback_progress_updates.md`).
- **Pasa siempre `-m`** para que la ruta se vea en el comando y en el registro.

## El registro

```bash
llm logs path            # where the SQLite database lives (per machine, outside the repo)
llm logs -n 5            # last five responses
llm logs -q "search"     # full-text search over prompts and responses
llm logs -m local -n 10  # filter by model
```

La base de datos contiene el texto de los prompts: trátala como `.env`, estado de trabajo local que nunca entra en git. Explórala con `uvx datasette "$(llm logs path)"`.

## Qué sustituye

`tools/ollama/call.py` y `tools/openai/call.py` se quedan solo para los scripts que ya los llaman (`tools/wiki/`, `skills/image-gen.md` para las imágenes). Los scripts nuevos llaman al comando `llm` o a su API de Python (`import llm`), así que sus llamadas también acaban en el registro. Las claves nunca entran en git: viven en `llm keys` o en `.env` (en el gitignore).
