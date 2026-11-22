# tools/openai/

Script auxiliar para la API de OpenAI, paralelo a `tools/ollama/call.py`. La misma forma de CLI, otro backend.

Úsalo cuando una tarea necesite **razonamiento de nivel frontera** que el Ollama local no alcanza Y la llamada merezca dinero de verdad. Para el trabajo rutinario o voluminoso, quédate en Ollama. Para la voz del principal y el diálogo editorial, quédate en Claude (la conversación actual).

## Uso rápido

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

Cero dependencias: solo usa `urllib` de la biblioteca estándar. Funciona con `python3` sin más.

## Clave de API

El script auxiliar lee la clave de API de estos sitios, por este orden:
1. La variable de entorno `OPENAI_API_KEY` (la canónica, coincide con el SDK de OpenAI)
2. La variable de entorno `openai_api_key` (alternativa en minúsculas)
3. El fichero `.env` del repositorio (también sin distinguir mayúsculas: `OPENAI_API_KEY` o `openai_api_key`)

La clave **nunca se imprime ni se registra**, ni siquiera en los mensajes de error. El fichero `.env` está en el gitignore (verificado).

Si la clave falta o no es válida, el script auxiliar termina con código 2 y una pista clara. No se degrada en silencio.

## Cuándo mandar tareas aquí, a Ollama o a Claude

Este es el tercer nivel de las reglas de enrutado del cómputo. Los dos primeros están documentados en [memory/reference_ollama_server.md](../../memory/reference_ollama_server.md).

**Usa OpenAI (este script auxiliar) para:**
- **Segunda opinión o revisión de nivel frontera.** Coge el borrador de un capítulo, pásalo por GPT-5.4 u o3-pro con un prompt de sistema de editor crítico y obtén una crítica estructurada. Combínalo con el perfil de escritura + las reglas de densidad para calibrar.
- **Tareas de razonamiento profundo** en las que los modelos locales de Ollama tocan techo a la vista y acertar importa. Modelos de razonamiento (o3-pro, o4-mini-deep-research) para problemas con estructura verificable.
- **Matices multilingües complejos** en los que el Qwen 122B local se queda corto con expresiones concretas del catalán o del castellano o con el registro cultural.
- **Cualquier cosa para la que el principal haya dicho «usa el modelo de mayor rendimiento».**

**Quédate en Ollama (`tools/ollama/call.py`) para:**
- Borradores rutinarios de traducción
- Resúmenes masivos de material de fuentes largo
- Clasificación, etiquetado, limpieza de transcripciones
- Esquemas de primera pasada que el principal reescribirá
- Todo lo mecánico y voluminoso cuya salida es materia prima

**Quédate en Claude Opus (la conversación actual) para:**
- Todo lo que tenga que ESTAR en la voz del principal (versiones finales, reescrituras de capítulos)
- El diálogo editorial con el principal
- Decisiones estructurales y compromisos
- Todo lo crítico en lo que un error dañaría en silencio un documento en el que confía el principal

**Regla práctica:**
- mecánico y voluminoso → Ollama (gratis, local)
- interpretativo y crítico, en la voz del principal → Claude (la sesión actual)
- razonamiento de frontera, segunda opinión, crítica profunda → OpenAI (de pago)

## Coste

Las llamadas a OpenAI cuestan dinero de verdad. El uso de tokens se registra en stderr después de cada llamada:

```
[using gpt-5.4]
[tokens: prompt=12453 completion=2891 total=15344]
```

En los modelos de razonamiento, los tokens de razonamiento se informan por separado porque se facturan de otra manera:

```
[tokens: prompt=12453 completion=8421 (reasoning=5530) total=20874]
```

Hazlo a conciencia. Una revisión con `gpt-5.4-pro` de un capítulo de 30k tokens con esfuerzo de razonamiento alto no es barata. Si dudas, pruébalo antes con una muestra más pequeña.

## Selección de modelo

**Ejecuta siempre `list` primero.** La gama de modelos disponibles cambia de un mes a otro. No escribas nombres de modelo a fuego en los scripts; comprueba qué hay.

```bash
python3 tools/openai/call.py list --filter gpt-5
```

Como instantánea del momento en que se escribió este script auxiliar (2026-04-11):

| Nivel | Modelo | Uso |
|---|---|---|
| Insignia | `gpt-5.4` | Revisión general de alta calidad, crítica de capítulos |
| Insignia pro | `gpt-5.4-pro` | La revisión más exhaustiva: lenta, cara, la mejor |
| Insignia mini | `gpt-5.4-mini` | Iteración más rápida y barata sobre la misma tarea |
| Razonamiento | `o3-pro` | Análisis crítico profundo con traza de razonamiento |
| Razonamiento largo | `o3-deep-research` / `o4-mini-deep-research` | Tareas de investigación o síntesis de varios pasos |
| Codex | `gpt-5.4` (o `gpt-5.3-codex`) | Revisión de código |

Esta instantánea quedará desfasada en cuestión de semanas. Vuelve a ejecutar `list` en lugar de fiarte de ella.

## Modelos de razonamiento

Para los modelos de la serie o (o3, o3-pro, o4-mini, etc.), pasa `--reasoning-effort low|medium|high`.

Los modelos de razonamiento pueden rechazar `--temp` y comportarse de otra manera con `--max-tokens`. Si la API devuelve un error por un parámetro no admitido, quítalo y reintenta una vez.

## Generación de imágenes

El script auxiliar ofrece el subcomando `image` para la familia de modelos `gpt-image-*`. La misma clave, la misma resolución del `.env` y el mismo tratamiento de errores que la vía de chat. El subcomando `image` llama a `/v1/images/generations` y escribe el PNG resultante (que el script decodifica de base64) en `--out`.

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

Flags:
- `--size`: `1024x1024` (cuadrado) · `1536x1024` (horizontal, cabe en diapositivas 16:9) · `1024x1536` (vertical) · `auto`
- `--quality`: `low | medium | high (default) | auto`
- `--n`: número de variantes (por defecto 1; ficheros con sufijo `-1`, `-2`, …)
- `--output-format`: `png | jpeg | webp` (si se omite, el valor por defecto del modelo)
- `--background`: `transparent | opaque | auto` (el fondo transparente funciona con `png`/`webp`)

Coste a principios de 2026: una imagen 1024×1024 o 1536×1024 de calidad `high` sale aproximadamente a **$0.15–$0.20**. El uso se registra en stderr igual que el del chat.

La skill completa, con cuándo usarlo y patrones de prompt: [`../../skills/image-gen.md`](../../skills/image-gen.md).

## Modos de fallo

**Código de salida 1**: prompt vacío u otro error de uso.

**Código de salida 2**: fallo de la API o de la red. El script auxiliar imprime el mensaje de error de la API (truncado a 1000 caracteres) y termina. No reintentes en silencio. **Díselo al principal** cuando pase, igual que en el protocolo de respaldo del script auxiliar de Ollama.

Las causas más habituales:
- Clave de API ausente o no válida (`401 unauthorized`): revisa `.env`
- Errata en el nombre del modelo (`404 model not found`): ejecuta `list` para ver qué existe
- Límite de peticiones (`429`): reintenta una vez con espera progresiva y luego avisa al principal
- Contexto demasiado largo (`400`): divide la entrada o usa un modelo con más contexto

## Referencia en la memoria

Consulta [`../../memory/reference_openai_api.md`](../../memory/reference_openai_api.md) para la referencia canónica de infraestructura, que se mantiene al día con cualquier cambio en la gama de modelos que comunique el principal.
