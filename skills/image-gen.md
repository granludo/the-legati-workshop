Genera una imagen con la familia `gpt-image-*` de OpenAI mediante `tools/openai/call.py image` y guárdala en disco. Úsala cuando un proyecto de escritura o una presentación necesite un elemento gráfico diseñado (una captura de pantalla simulada, un diagrama estilizado con el texto incrustado, una portadilla, una ilustración) que sería tedioso componer con formas nativas y que sea lo bastante pequeño para que merezca una sola llamada de pago a la API.

## Cuándo usar esta skill

- Una diapositiva necesita un visual diseñado que mezcle texto y forma (una respuesta simulada de un LLM con una cita inventada de un artículo, una ilustración anotada, un diagrama conceptual estilizado).
- Un documento necesita una imagen de cabecera o una ilustración puntual.
- Una figura que costaría más tiempo componer en PowerPoint / python-pptx / Excalidraw que especificar en un prompt.

## Cuándo NO usar esta skill

- **Tablas, cuadrículas 2×2, listas de viñetas, formas simples**: constrúyelas como elementos nativos de PowerPoint (python-pptx, Keynote, Excalidraw). Así siguen siendo editables. La presentación del Día 4 de unex (`writting-projects/BSC-AGENTS-COURSE/sources-unex-2026/build_slides_2026-05-13.py`) es el precedente dentro del repositorio: diagramas simples nativos, diagramas conceptuales como PNG prerrenderizados.
- **Cualquier cosa que el principal tenga que retocar después**: una imagen generada es un binario; una errata no se arregla sin regenerarla. Las formas nativas sobreviven a la edición; las imágenes quedan congeladas.
- **Fotografías de personas, lugares o productos reales**: usa una foto real, no una imagen generada.
- **Cualquier caso en que los ~$0.16 por imagen de alta calidad no compren bastante más calidad que una composición nativa de 5 minutos.**

## Instrucciones

### 1. Confirma que el modelo está disponible

La gama de modelos de imagen de OpenAI cambia. Lista siempre primero: `list` es gratis, solo consulta `/v1/models`.

```bash
python3 tools/openai/call.py list --filter image
```

Por defecto, `gpt-image-2`. Si se ha retirado, usa el que esté vigente.

### 2. Elige el tamaño

| Tamaño | Proporción | Uso |
|---|---|---|
| `1536x1024` | 3:2 horizontal | Imagen del cuerpo de una diapositiva (cabe en 16:9 con margen) |
| `1024x1024` | 1:1 | Ilustración cuadrada, estilo icono |
| `1024x1536` | 2:3 vertical | Figura de página de libro, ilustración de media página |
| `auto` | variable | Cuando dudes; elige el modelo |

### 3. Elige la calidad

`high` es el valor por defecto, adecuado para diapositivas y figuras de documentos. Baja a `medium` solo para iteraciones exploratorias. `low` es para pruebas desechables.

### 4. Escribe el prompt como un único párrafo autocontenido

El modelo recibe una sola cadena. Empieza por el medio («Clean academic slide. Title '…' in dark navy Palatino serif…»). Especifica las fuentes, los colores en hexadecimal o por nombre, la proporción y lo que NO debe aparecer. En `writting-projects/BSC-AGENTS-COURSE/week-01/session-1-slides.md` tienes una biblioteca de prompts dentro del repositorio.

### 5. Lanza la generación

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

`--n 4` genera cuatro variantes de una vez (sale más barato por imagen que cuatro llamadas separadas: los tokens del prompt se amortizan). Cuando `--n > 1`, los ficheros llevan los sufijos `-1.png`, `-2.png`, …

### 6. Revisa el resultado

- ¿El texto ha salido legible? Los modelos gpt-image todavía estropean a veces el texto pequeño: si pasa, vuelve a lanzarlo con un prompt más preciso o con un tamaño mayor.
- ¿La estética encaja con el resto de la presentación o del documento?
- Si no está bien: afina el prompt y regenera. No aceptes una imagen mala porque la llamada ya esté pagada.

### 7. Haz visible el coste

El uso de tokens se registra en stderr después de cada llamada:

```
[using gpt-image-2, size=1536x1024, quality=high]
[tokens: input=42 (text=42 image=0) output=4160 total=4202]
[wrote 1834 KB to /path/to/image.png]
```

Dile al principal el coste en tu resumen (una imagen 1536×1024 de alta calidad cuesta aproximadamente **$0.15–$0.20** a principios de 2026).

## Patrones de prompt que funcionan

- **Empieza por el medio.** «Clean academic slide. Title '…' in dark navy Palatino serif. Below, …»
- **Especifica la familia tipográfica aunque el modelo no pueda respetarla con exactitud.** Nombres como «Palatino serif», «Helvetica sans-serif», «Consolas monospace» anclan la estética.
- **Indica el color en hexadecimal o por nombre.** «navy #1F2454 on white background».
- **Especifica de forma explícita la proporción y la decoración.** «16:9. No decoration. Thin navy lines only.»
- **Di explícitamente lo que NO debe aparecer.** «No drop shadows. No gradients. No emoji.»

## Modos de fallo

- **`404 model not found`**: `gpt-image-2` ha cambiado de nombre o se ha retirado. Vuelve a ejecutar `list --filter image` y elige el id vigente.
- **Texto estropeado en la salida**: habitual con fuentes pequeñas o títulos largos. Aumenta el tamaño, acorta la parte de texto incrustado o divide: deja el texto editable como elemento nativo y pon en la imagen solo la parte que de verdad es ilustración.
- **`429` límite de peticiones**: reintenta una vez con espera progresiva y, si sigue fallando, avisa al principal.

## Referencias cruzadas

- Script auxiliar (el subcomando `image`): [`tools/openai/call.py`](../tools/openai/call.py)
- README del script auxiliar: [`tools/openai/README.md`](../tools/openai/README.md)
- Referencia de infraestructura: [`memory/reference_openai_api.md`](../memory/reference_openai_api.md)
- Enrutado del cómputo en [`AGENTS.md`](../AGENTS.md) §6 y en [`tools/llm/README.md`](../tools/llm/README.md)
