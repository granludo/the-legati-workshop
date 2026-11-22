# tools/openai/

Eina auxiliar per a l'API d'OpenAI, paral·lela a `tools/ollama/call.py`. La mateixa forma de línia d'ordres, un backend diferent.

Fes-la servir quan una tasca necessiti un **raonament de qualitat frontera** que l'Ollama local no assoleix I la crida valgui diners de debò. Per a la feina rutinària o voluminosa, queda't a Ollama. Per a la veu del principal i el diàleg editorial, queda't a Claude (la conversa actual).

## Ús ràpid

```bash
# List currently available models (free — uses /v1/models)
python3 tools/openai/call.py list

# Filter the model list (substring, case-insensitive)
python3 tools/openai/call.py list --filter gpt-5
python3 tools/openai/call.py list --filter o3

# Generate from an inline prompt
python3 tools/openai/call.py generate --model gpt-5.4 --prompt "..."

# Generate from a file → file
python3 tools/openai/call.py generate \
    --model gpt-5.4 \
    --in /path/to/chapter.md \
    --out /tmp/review.md \
    --system "You are a critical editor of long-form essays. Identify weak passages and propose specific cuts."

# System prompt from a file (recommended for long review prompts)
python3 tools/openai/call.py generate \
    --model gpt-5.4-pro \
    --in /path/to/chapter.md \
    --out /tmp/review.md \
    --system /path/to/review-system-prompt.md

# Reasoning model (o-series)
python3 tools/openai/call.py generate \
    --model o3-pro \
    --in /path/to/chapter.md \
    --out /tmp/review.md \
    --reasoning-effort high
```

Cap dependència: només fa servir `urllib` de la biblioteca estàndard. S'executa amb un `python3` normal.

## Clau d'API

L'eina llegeix la clau d'API d'aquests llocs, per ordre:
1. Variable d'entorn `OPENAI_API_KEY` (la canònica, coincideix amb l'SDK d'OpenAI)
2. Variable d'entorn `openai_api_key` (alternativa en minúscules)
3. El fitxer `.env` del repositori (també sense distingir majúscules: `OPENAI_API_KEY` o `openai_api_key`)

La clau **no s'imprimeix ni es registra mai**, ni tan sols als missatges d'error. El fitxer `.env` està ignorat per git (comprovat).

Si la clau falta o no és vàlida, l'eina surt amb el codi 2 i una indicació clara. No degrada el resultat en silenci.

## Quan encaminar les tasques aquí, a Ollama o a Claude

Aquest és el tercer nivell de les regles d'encaminament de còmput. Els dos primers estan documentats a [memory/reference_ollama_server.md](../../memory/reference_ollama_server.md).

**Fes servir OpenAI (aquesta eina) per a:**
- **Segona opinió o revisió de qualitat frontera.** Agafa l'esborrany d'un capítol, passa'l per GPT-5.4 o o3-pro amb un prompt de sistema d'editor crític i obtén una crítica estructurada. Combina-ho amb el perfil d'escriptura i les regles de densitat per calibrar-ho.
- **Tasques de raonament profund** en què els models locals d'Ollama toquen sostre de manera visible i encertar la resposta és important. Models de raonament (o3-pro, o4-mini-deep-research) per a problemes amb una estructura verificable.
- **Matisos multilingües complexos** en què el Qwen local de 122B no arriba amb expressions concretes del català o del castellà o amb el registre cultural.
- **Qualsevol cosa per a la qual el principal hagi dit «fes servir el model de més rendiment».**

**Queda't a Ollama (`tools/ollama/call.py`) per a:**
- Esborranys rutinaris de traducció
- Resums massius de material font llarg
- Classificació, etiquetatge, neteja de transcripcions
- Esquemes de primera passada que el principal reescriurà
- Qualsevol cosa mecànica i voluminosa en què la sortida sigui matèria primera

**Queda't a Claude Opus (la conversa actual) per a:**
- Qualsevol cosa que hagi de SER en la veu del principal (versions finals, reescriptures de capítols)
- El diàleg editorial amb el principal
- Decisions estructurals i compromisos
- Qualsevol cosa determinant en què un error podria malmetre en silenci un document en què el principal confia

**Regla pràctica:**
- **mecànic i voluminós** → Ollama (gratuït, local)
- **interpretatiu i determinant, en la veu del principal** → Claude (la sessió actual)
- **raonament frontera, segona opinió, crítica profunda** → OpenAI (de pagament)

## Cost

Les crides a OpenAI costen diners de debò. L'ús de tokens es registra a stderr després de cada crida:

```
[using gpt-5.4]
[tokens: prompt=12453 completion=2891 total=15344]
```

Per als models de raonament, els tokens de raonament s'informen a part perquè es facturen de manera diferent:

```
[tokens: prompt=12453 completion=8421 (reasoning=5530) total=20874]
```

Fes-ho amb intenció. Una revisió amb `gpt-5.4-pro` d'un capítol de 30k tokens amb un esforç de raonament alt no és barata. Si dubtes, prova-ho primer amb una mostra més petita.

## Selecció de model

**Executa sempre `list` primer.** La gamma de models disponibles canvia d'un mes per l'altre. No escriguis noms de model fixos als scripts; comprova què hi ha.

```bash
python3 tools/openai/call.py list --filter gpt-5
```

Com a instantània del moment en què es va escriure aquesta eina (2026-04-11):

| Nivell | Model | Per a |
|---|---|---|
| Insígnia | `gpt-5.4` | Revisió general d'alta qualitat, crítica de capítols |
| Insígnia pro | `gpt-5.4-pro` | La revisió més exhaustiva: lenta, cara, la millor |
| Insígnia mini | `gpt-5.4-mini` | Iteració més ràpida i barata sobre la mateixa tasca |
| Raonament | `o3-pro` | Anàlisi crítica profunda amb traça de raonament |
| Raonament llarg | `o3-deep-research` / `o4-mini-deep-research` | Tasques de recerca i síntesi de diversos passos |
| Codex | `gpt-5.4` (o `gpt-5.3-codex`) | Revisió de codi |

Aquesta instantània quedarà desfasada en poques setmanes. Torna a executar `list` en lloc de refiar-te'n.

## Models de raonament

Per als models de la sèrie o (o3, o3-pro, o4-mini, etc.), passa `--reasoning-effort low|medium|high`.

Els models de raonament poden rebutjar `--temp` i comportar-se de manera diferent amb `--max-tokens`. Si l'API torna un error sobre un paràmetre no admès, treu-lo i torna-ho a provar una vegada.

## Generació d'imatges

L'eina ofereix la subordre `image` per a la família de models `gpt-image-*`. La mateixa clau, la mateixa resolució del `.env` i la mateixa gestió d'errors que el camí del xat. La subordre `image` crida `/v1/images/generations` i escriu el PNG resultant (descodificat de base64 per l'eina) a `--out`.

```bash
# List image models
python3 tools/openai/call.py list --filter image

# Generate one image
python3 tools/openai/call.py image \
    --model gpt-image-2 \
    --prompt "Clean academic slide. Title '...' in dark navy Palatino serif. ..." \
    --out /tmp/slide.png \
    --size 1536x1024 \
    --quality high

# Multiple variants on one prompt (cheaper per image — shared prompt tokens)
python3 tools/openai/call.py image \
    --model gpt-image-2 \
    --in prompt.txt \
    --out /tmp/slide.png \
    --n 4
# → /tmp/slide-1.png, /tmp/slide-2.png, /tmp/slide-3.png, /tmp/slide-4.png
```

Opcions:
- `--size`: `1024x1024` (quadrat) · `1536x1024` (horitzontal, cap en diapositives 16:9) · `1024x1536` (vertical) · `auto`
- `--quality`: `low | medium | high (default) | auto`
- `--n`: nombre de variants (per defecte 1; fitxers amb sufix `-1`, `-2`, …)
- `--output-format`: `png | jpeg | webp` (el valor per defecte del model si s'omet)
- `--background`: `transparent | opaque | auto` (transparent funciona amb `png`/`webp`)

Cost a principis del 2026: una imatge de qualitat `high` de 1024×1024 o 1536×1024 surt aproximadament per **0,15–0,20 $**. L'ús es registra a stderr igual que l'ús del xat.

La skill completa, amb quan fer-la servir i patrons de prompt: [`../../skills/image-gen.md`](../../skills/image-gen.md).

## Modes de fallada

**Codi de sortida 1**: prompt buit o un altre error d'ús.

**Codi de sortida 2**: fallada de l'API o de la xarxa. L'eina imprimeix el missatge d'error de l'API (tallat a 1000 caràcters) i surt. No ho tornis a provar en silenci. **Digues-ho al principal** quan passi, de la mateixa manera que funciona el protocol d'alternativa de l'eina d'Ollama.

Les causes més habituals:
- Clau d'API que falta o no és vàlida (`401 unauthorized`): comprova el `.env`
- Errada en el nom del model (`404 model not found`): executa `list` per veure què existeix
- Límit de freqüència (`429`): torna-ho a provar una vegada amb espera progressiva, i després digues-ho al principal
- Context massa llarg (`400`): divideix l'entrada o fes servir un model amb un context més gran

## Punter a la memòria

Vegeu [`../../memory/reference_openai_api.md`](../../memory/reference_openai_api.md) per a la referència d'infraestructura canònica, mantinguda al dia amb qualsevol canvi en la gamma de models que informi el principal.
