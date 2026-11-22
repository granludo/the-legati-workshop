Genera una imatge amb la família `gpt-image-*` d'OpenAI fent servir `tools/openai/call.py image` i desa-la al disc. Fes-la servir quan un projecte d'escriptura o una presentació necessiti un element d'imatge dissenyat (una captura de pantalla simulada, un diagrama estilitzat amb text incrustat, una portadeta, una il·lustració) que costaria compondre amb formes natives i que és prou petit perquè valgui la pena una sola crida de pagament a l'API.

## Quan fer servir aquesta skill

- Una diapositiva necessita un element visual dissenyat que barregi text i forma (una resposta simulada d'un LLM amb una cita d'article inventada, una il·lustració anotada, un diagrama conceptual estilitzat).
- Un document necessita una imatge de capçalera o una il·lustració puntual.
- Una figura que costaria més de compondre en PowerPoint / python-pptx / Excalidraw que d'especificar en un prompt.

## Quan NO fer servir aquesta skill

- **Taules, graelles 2×2, llistes de vinyetes, formes simples**: construeix-les com a elements natius de PowerPoint (python-pptx, Keynote, Excalidraw). Així continuen sent editables. La presentació del Día 4 de la unex (`writting-projects/BSC-AGENTS-COURSE/sources-unex-2026/build_slides_2026-05-13.py`) és el precedent dins el repositori: diagrames simples natius, diagrames conceptuals com a PNG generats prèviament.
- **Qualsevol cosa que el principal hagi de retocar després**: una imatge generada és un binari; una errada tipogràfica no es pot corregir sense tornar-la a generar. Les formes natives sobreviuen a l'edició; les imatges queden congelades.
- **Fotografies de persones, llocs o productes reals**: fes servir una foto real, no una generació.
- **Qualsevol cas en què els ~0,16 $ per imatge d'alta qualitat no comprin prou qualitat respecte d'una composició nativa de 5 minuts.**

## Instruccions

### 1. Confirma que el model està disponible

La gamma de models d'imatge d'OpenAI canvia. Fes sempre primer un llistat: `list` és gratuït, només consulta `/v1/models`.

```bash
python3 tools/openai/call.py list --filter image
```

Per defecte, `gpt-image-2`. Si ha quedat obsolet, recorre al que sigui vigent.

### 2. Tria la mida

| Mida | Proporció | Per a |
|---|---|---|
| `1536x1024` | 3:2 horitzontal | Imatge del cos d'una diapositiva (cap en 16:9 amb marge) |
| `1024x1024` | 1:1 | Il·lustració quadrada, estil icona |
| `1024x1536` | 2:3 vertical | Figura de pàgina de llibre, il·lustració de mitja pàgina |
| `auto` | (cap) | Quan dubtis; tria el model |

### 3. Tria la qualitat

`high` és l'opció per defecte, adequada per a diapositives i figures de documents. Baixa a `medium` només per a iteracions exploratòries. `low` és per a proves d'un sol ús.

### 4. Escriu el prompt en un sol paràgraf autònom

El model rep una sola cadena. Comença pel mitjà («Clean academic slide. Title '…' in dark navy Palatino serif…»). Especifica les fonts, els colors en hexadecimal o pel nom, la proporció i què NO s'ha d'incloure. Vegeu `writting-projects/BSC-AGENTS-COURSE/week-01/session-1-slides.md` per a una biblioteca de prompts dins el repositori.

### 5. Executa la generació

```bash
# Inline prompt
python3 tools/openai/call.py image \
    --model gpt-image-2 \
    --prompt "<your prompt>" \
    --out /path/to/image.png \
    --size 1536x1024 \
    --quality high

# Or read the prompt from a file (cleaner for long prompts)
python3 tools/openai/call.py image \
    --model gpt-image-2 \
    --in prompt.txt \
    --out /path/to/image.png \
    --size 1536x1024
```

`--n 4` genera quatre variants alhora (més barat per imatge que quatre crides separades: els tokens del prompt s'amortitzen). Els fitxers reben els sufixos `-1.png`, `-2.png`, … quan `--n > 1`.

### 6. Revisa el resultat

- El text s'ha generat llegible? Els models gpt-image encara de tant en tant desfiguren el text petit; si passa, torna-ho a executar amb un prompt més precís o una mida més gran.
- L'estètica encaixa amb la resta de la presentació o del document?
- Si no és bona: afina el prompt i torna-la a generar. No acceptis una imatge dolenta perquè la crida ja està pagada.

### 7. Fes visible el cost

L'ús de tokens es registra a stderr després de cada crida:

```
[using gpt-image-2, size=1536x1024, quality=high]
[tokens: input=42 (text=42 image=0) output=4160 total=4202]
[wrote 1834 KB to /path/to/image.png]
```

Digues-ne el cost al principal al teu resum (una imatge d'alta qualitat de 1536×1024 costa aproximadament **0,15–0,20 $** a principis del 2026).

## Patrons de prompt que funcionen

- **Comença pel mitjà.** «Clean academic slide. Title '…' in dark navy Palatino serif. Below, …»
- **Especifica la família tipogràfica encara que el model no la pugui respectar exactament.** Noms com «Palatino serif», «Helvetica sans-serif», «Consolas monospace» fixen l'estètica.
- **Indica el color en hexadecimal o pel nom.** «navy #1F2454 on white background».
- **Especifica explícitament la proporció i la decoració.** «16:9. No decoration. Thin navy lines only.»
- **Digues explícitament què NO s'ha d'incloure.** «No drop shadows. No gradients. No emoji.»

## Modes de fallada

- **`404 model not found`**: `gpt-image-2` ha canviat de nom o ha quedat obsolet. Torna a executar `list --filter image` i tria l'identificador vigent.
- **Text desfigurat a la sortida**: habitual amb fonts petites o títols llargs. Augmenta la mida, escurça la part de text incrustat, o separa-ho: deixa el text editable com a element natiu i posa a la imatge només la part realment il·lustrativa.
- **Límit de freqüència `429`**: torna-ho a provar una vegada amb espera progressiva, i després digues-ho al principal.

## Referències creuades

- Eina auxiliar (la subordre `image`): [`tools/openai/call.py`](../tools/openai/call.py)
- README de l'eina auxiliar: [`tools/openai/README.md`](../tools/openai/README.md)
- Referència d'infraestructura: [`memory/reference_openai_api.md`](../memory/reference_openai_api.md)
- Encaminament de còmput a [`AGENTS.md`](../AGENTS.md) §6 i [`tools/llm/README.md`](../tools/llm/README.md)
