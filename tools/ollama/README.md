# tools/ollama/

> [!note] Millor `llm`
> La feina nova crida els models a través de l'ordre `llm` ([tools/llm/README.md](../llm/README.md)), que també arriba a Ollama amb el connector `llm-ollama` i registra cada crida. Aquesta eina es manté per als scripts que ja la fan servir (`tools/wiki/`).

Eina auxiliar per a un o més servidors Ollama: un ordinador de sobretaula potent a la teva xarxa, o `localhost`. Edita la llista `SERVERS` a l'inici de `call.py` amb les teves adreces (els valors que s'hi inclouen són els de la LAN del taller original i a la teva no respondran).

L'eina sondeja els servidors per ordre i tria el primer accessible que tingui el model demanat. Millor els models grans: els models locals petits es degraden de pressa amb contextos llargs i amb llengües que no són l'anglès.

## Ús ràpid

```bash
# List models across the whole fleet (shows which server has what)
python3 tools/ollama/call.py list

# List models on a specific server
python3 tools/ollama/call.py --server http://localhost:11434 list

# Generate with whatever server has the model (fleet auto-discovery)
python3 tools/ollama/call.py generate --model gpt-oss:20b --prompt "Hola, com estàs?"

# Generate from a file, write to a file
python3 tools/ollama/call.py generate \
    --model qwen3.5:122b \
    --in sources/ia-i-educacio/el-moment-sputnik-2024/el_moment_sputnik_2024.txt \
    --out /tmp/summary.md \
    --temp 0.2

# Force a specific server (e.g. for benchmarking)
python3 tools/ollama/call.py --server http://localhost:11434 generate \
    --model qwen3.5:122b --prompt "test"

# Generate embeddings (only on .47 today)
python3 tools/ollama/call.py embed \
    --model nomic-embed-text:latest \
    --in some-text.txt
```

Cap dependència: només fa servir `urllib` de la biblioteca estàndard. S'executa amb un `python3` normal o amb `uv run`.

## Quan falla

Dos modes de fallada:

**Codi de sortida 2: cap servidor accessible.** Cap servidor de `SERVERS` no ha respost al sondeig. Normalment vol dir que aquesta màquina és fora de la xarxa on viu el servidor (un portàtil a la wifi d'un congrés), o que el servidor està apagat.

```
ERROR: no Ollama server reachable. Tried: <your SERVERS list>
HINT:  Fall back to the session model for this task and tell the principal you fell back.
```

**Codi de sortida 3: model no disponible.** Un servidor era accessible però no tenia el model demanat. L'eina imprimeix el que hi ha realment disponible perquè puguis triar una alternativa.

**Protocol d'alternativa:** quan un agent que fa la crida (Claude) veu el codi de sortida 2:
1. Diu al principal que ha recorregut al model de la sessió.
2. Fa la tasca directament a la conversa actual.
3. No degrada el resultat en silenci ni ho torna a provar en bucle.

Quan l'agent veu el codi de sortida 3: executa `list` per veure la flota actual, tria una alternativa raonable i ho torna a provar una vegada. Si continua sense estar disponible, ho diu al principal.

## Política de finestra de context

Segons l'experiència del taller original, els **models petits** (de menys de 70B paràmetres) es degraden quan el context passa de ~64k, i per això l'eina limita `num_ctx` a 65536 per a aquests models. Els models més grans (70B o més) fan servir el seu valor per defecte (que en aquest servidor és alt). Canvia-ho amb `--num-ctx N` si saps què fas.

## Temps d'espera

Per defecte, 900 segons (15 min). Els models locals són lents a la primera crida (escalfament) i en les generacions llargues. Si no n'hi ha prou, canvia `TIMEOUT_SECONDS` a `call.py` o passa-hi un prompt més curt.

## Descoberta dinàmica de models

Els models dels servidors canvien amb el temps. **Executa sempre `list` primer** per veure què hi ha disponible ara, en lloc de suposar que existeix un model concret. Els models d'avui poden ser diferents dels d'ahir, i quin servidor té quin model pot canviar d'una descàrrega a l'altra.

## Quan encaminar les tasques aquí o a Claude Opus

**Fes servir l'Ollama local (Qwen 3.5 122B o el model «ràpid» vigent) per a:**
- Esborranys rutinaris de traducció (CA ↔ ES ↔ EN, que el principal reescriurà)
- Resums de material font llarg
- Classificació i etiquetatge
- Neteja de transcripcions (corregir entitats amb nom, treure al·lucinacions)
- Esquemes inicials que el principal sobreescriurà
- Operacions massives sobre text (no n'hi ha prou amb una regex, però sí amb la semàntica)

**Fes servir Opus per a:**
- Qualsevol cosa que requereixi la veu del principal (necessita el perfil d'escriptura i la visió del món)
- Síntesi intel·lectual, raonament entre dominis
- El diàleg editorial amb el principal
- Versions finals de capítols i articles
- Decisions i compromisos estructurals

**Regla pràctica:** si una tasca és **mecànica i voluminosa**, Ollama. Si és **interpretativa i determinant**, Opus.

## Punter a la memòria

Vegeu [../../memory/reference_ollama_server.md](../../memory/reference_ollama_server.md) per a la referència d'infraestructura canònica, mantinguda al dia amb qualsevol canvi de models o de servidors.
