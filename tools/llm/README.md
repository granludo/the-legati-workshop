# tools/llm: `llm`, la porta d'entrada única

Totes les crides a models que **no** són el model de la sessió (un model local per a feina massiva, un segon model frontera per a una opinió independent, embeddings) passen per [l'ordre `llm` de Simon Willison](https://llm.datasette.io). Una sola superfície d'ordres per a tots els proveïdors, i cada prompt i cada resposta **es registren a SQLite** automàticament, de manera que sempre pots veure què s'ha demanat a quin model i què n'ha tornat. Funciona igual des de Claude Code, des de Codex i des del teu propi terminal.

## Configuració (una vegada per màquina)

```bash
uv tool install llm                # or: pipx install llm · brew install llm
llm install llm-ollama             # local models through Ollama (optional)
llm keys set openai                # paste your key; stored in llm's keys.json, outside the repo (optional)
llm models                         # what you can call now
```

Els altres proveïdors també són connectors (`llm install llm-anthropic`, `llm install llm-gemini`, `llm install llm-mistral` …). Per a un servidor Ollama remot a la teva xarxa: `OLLAMA_HOST=http://desk-machine.local:11434` al perfil del shell. Anota què té aquesta màquina a la seva secció de `memory/reference_hosts.md`.

Els àlies fan els prompts més curts i l'encaminament explícit:

```bash
llm aliases set local qwen3.5:122b # whatever big model your Ollama server runs
llm aliases set second gpt-5       # a frontier model from another family
```

## Ús

```bash
llm -m local 'Summarise this transcript in five bullet points' < transcript.txt
cat draft.md | llm -m second -s 'Review this argument. List the three weakest claims.'
llm embed -m nomic-embed-text -c 'text to embed'
```

Opcions habituals: `-s 'system prompt'` · `-o temperature 0.2` · `-o max_tokens 4000` · `-a image.png` (models de visió) · `-t <template>`.

## Regles d'encaminament

- **La feina interpretativa, sensible a la veu i determinant es queda al model de la sessió.** Això inclou tot el que hagi de sonar com el principal.
- **La feina mecànica massiva** (classificació, extracció, resums per a ús propi, esborranys de traducció de primera passada en llengües que el model maneja bé) pot anar a un model local gran. Millor els models grans: els petits es degraden de pressa amb contextos llargs i fora de l'anglès.
- **No enviïs mai la generació en una llengua a un model que l'escriu malament.** Per a molts models locals, això vol dir el català, el basc, el gallec i altres llengües petites: es queden al model de la sessió o a un model frontera.
- **Les crides de pagament costen diners de debò:** fes-ho amb intenció, i abans d'un lot digues quantes crides farà.
- **Les crides llargues segueixen la regla de progrés** (`memory/feedback_progress_updates.md`).
- **Passa sempre `-m`**, perquè la ruta sigui visible a l'ordre i al registre.

## El registre

```bash
llm logs path            # where the SQLite database lives (per machine, outside the repo)
llm logs -n 5            # last five responses
llm logs -q "search"     # full-text search over prompts and responses
llm logs -m local -n 10  # filter by model
```

La base de dades conté el text dels prompts: tracta-la com el `.env`, estat de treball local que mai no entra a git. Explora-la amb `uvx datasette "$(llm logs path)"`.

## Què substitueix

`tools/ollama/call.py` i `tools/openai/call.py` es mantenen només per als scripts que ja els criden (`tools/wiki/`, `skills/image-gen.md` per a les imatges). Els scripts nous criden l'ordre `llm` o la seva API de Python (`import llm`), perquè les seves crides també quedin al registre. Les claus mai no entren a git: viuen a `llm keys` o al `.env` (ignorat per git).
