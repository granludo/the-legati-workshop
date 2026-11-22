---
name: add-source
description: Incorpora una fuente nueva (vídeo de YouTube, PDF, fichero de audio, artículo web, texto) al árbol sources/ del taller, para un proyecto de escritura concreto o para uso compartido. Se encarga de la descarga, la extracción de audio, la transcripción, la ubicación, el README y el registro en INDEX.md.
---

# /add-source

Usa esta skill cuando el principal quiera traer material de fuentes nuevo al repositorio. La skill cubre todo el proceso de incorporación: adquirir → derivar → ubicar → documentar → registrar. Es **conservadora por diseño**: deja la fuente en su sitio y ofrece enlazarla desde los documentos del proyecto, pero no edita por su cuenta las wikis ni la memoria de los proyectos. La integración es un paso aparte que aprueba el principal.

## Cuándo invocarla

El principal dice cosas como:
- «añade esta fuente: <URL>»
- «/add-source <URL o ruta>»
- «he encontrado este artículo, ¿puedes ponerlo en su sitio?»
- «aquí tienes una grabación nueva de una conferencia para el libro ia-i-educacio»

## Entradas

Acepta cualquiera de las siguientes y detecta el tipo automáticamente:
- **URL de YouTube** → usa `yt-dlp` (ya instalado en este entorno).
- **URL de un artículo web o académico** (PDF o HTML) → usa `curl` o `WebFetch`. Si la página ofrece el PDF, descárgalo siempre antes que otra cosa.
- **PDF local u otro binario** → muévelo o cópialo al destino.
- **Fichero local de audio o vídeo** → lo mismo, con los pasos derivados de audio y transcripción.
- **Texto o markdown pegado** → escríbelo directamente en un fichero `.md` dentro de la carpeta adecuada.

Si la entrada es ambigua (p. ej., un nombre de fichero suelto), pregunta al principal antes de seguir.

## Flujo (síguelo en orden)

### 1. Identifica el ámbito

Pregunta al principal (o dedúcelo del contexto) a qué ámbito pertenece la fuente:
- **`sources/shared/<type>/`** si alimenta varios proyectos o es de interés general.
- **`sources/<project>/`** si solo tiene sentido para un proyecto de escritura concreto. Slugs de proyecto válidos hoy: `ia-i-educacio`, `palantir-paper`, `aprenentatge-personalitzat`, `aac-book`.

Si dudas, **por defecto, `shared/`**. Es más fácil encerrarla en un proyecto más adelante que sacarla de él ahora.

### 2. Elige un slug de carpeta

Crea una carpeta dentro del ámbito elegido con un nombre en minúsculas y en kebab-case. Convenciones:
- **Charlas / conferencias:** `{year}-{venue}-{topic}`, p. ej. `2024-udl-sputnik/`.
- **Libros / artículos:** `{firstauthor}-{year}-{shortname}`, p. ej. `weller-2022-metaphors/`.
- **Cursos / masterclasses:** `{name}-{subtitle}`, p. ej. `lamb-101-rag-masterclass/`.
- **Entradas de blog / fuentes de un solo fichero:** sin carpeta; pon el fichero directamente en el ámbito, con un nombre descriptivo.

Para una fuente de varios ficheros (vídeo + audio + transcripción + metadatos), usa siempre una carpeta. Un PDF único y autocontenido va directamente en el ámbito.

### 3. Consigue los bytes

**URL de YouTube:**
```bash
cd <scope-folder>
yt-dlp --write-info-json --write-subs --write-auto-subs \
       --sub-langs "ca,es,en,ca.*,es.*,en.*" \
       -f "bv*+ba/b" \
       -o "%(title)s.%(ext)s" "<URL>"
```
Si ffmpeg no está instalado en el sistema, yt-dlp dejará las pistas de vídeo y de audio por separado, y no pasa nada. El audio que hay que transcribir estará en el fichero `.webm` (Opus) o `.m4a`.

**URL web (PDF):**
```bash
curl -sSL -o <filename>.pdf "<URL>"
```

**URL web (artículo HTML):** usa `WebFetch` con un prompt que pida el texto del artículo en markdown y guarda el resultado.

**Fichero local:** `mv` o `cp` a su sitio.

### 4. Deriva formatos útiles

**Vídeo → audio (MP3 para transcribir o escuchar):**
```bash
uv run --with imageio-ffmpeg python -c "
import imageio_ffmpeg, subprocess
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ffmpeg, '-y', '-i', 'input.webm', '-vn',
                '-codec:a', 'libmp3lame', '-b:a', '128k', '-ar', '44100',
                'output.mp3'])
"
```

**Audio → transcripción:** usa la herramienta que ya tiene el repositorio.
```bash
uv run --project tools/transcribe tools/transcribe/transcribe.py --lang ca <audio.mp3>
```
(Cámbialo por `--lang es` o `--lang en` según corresponda.) Esto escribe un `.srt` y un `.txt` junto a la entrada. El idioma se deduce del contexto: si el principal no lo indica, pregunta.

**Pasada obligatoria de revisión de la transcripción con un LLM.** Whisper comete errores garrafales (nombres propios, siglas, cambios de idioma, vocabulario de grupo) con tanta frecuencia que el `.txt` en bruto no puede tratarse como listo para citar. Conserva el fichero en bruto como rastro de auditoría y genera un `<slug>.reviewed.txt` con una pasada de LLM. El nivel de modelo sigue las reglas de cómputo (`AGENTS.md` §6): el modelo de la sesión, o un modelo frontera a través de `llm`, para cualquier idioma que un modelo local escriba mal; un modelo local grande a través de `llm` sirve para corregir nombres propios de forma mecánica en los idiomas que maneja bien; revisión con un modelo frontera cuando el contenido es crítico. El fichero revisado debe señalar qué se ha cambiado (una sección al principio en las transcripciones cortas, `==highlight==` en línea en las largas) para que el principal pueda comprobarlo por muestreo.

**PDF:** déjalo tal cual. Si extraer el texto sería útil, menciónalo como paso posterior opcional; no lo hagas por defecto.

### 5. Escribe un `README.md` dentro de la carpeta de la fuente

Para cualquier **fuente de varios ficheros**, crea un `README.md` con:

```markdown
# <Source title>

- **Type:** <conference | paper | blog post | video course | ...>
- **Author / speaker:** <...>
- **Origin:** <original URL or citation>
- **Date of material:** <YYYY-MM-DD or year>
- **Date added to repo:** <YYYY-MM-DD>
- **Language:** <ca | es | en | ...>
- **Project(s) it feeds:** <list of writing projects that reference this>

## Summary
<One paragraph describing what this source contains and why it was added.>

## Files in this folder
- `<filename>` — <one-line description>
- ...

## Notes
<Anything quirky: transcription quality, missing subtitles, trailing hallucinations, OCR issues, pages to skip, etc.>
```

Las fuentes de un solo fichero no necesitan README propio: su entrada en `sources/INDEX.md` cumple esa función.

### 6. Regístrala en `sources/INDEX.md`

Añade una entrada en la sección adecuada (`shared/<type>/` o `<project>/`). Sigue el formato existente: una viñeta con el nombre del fichero o de la carpeta entre comillas invertidas, seguida de una descripción de una línea y de los metadatos imprescindibles.

**Si todavía no existe una sección para este ámbito**, créala en orden alfabético junto a las que ya hay, con el mismo estilo de encabezado.

**Comprobación de duplicados:** antes de incorporar la fuente, busca con grep en `sources/INDEX.md` la URL de origen, el título o el nombre del fichero. Si hay coincidencia, detente y avisa al principal en lugar de incorporarla dos veces.

### 7. Ofrece la integración (no la apliques por tu cuenta)

Cuando la fuente esté en su sitio e indexada, **ofrece**:
- Añadir una referencia en el documento del proyecto correspondiente (p. ej., el §16 de `writting-projects/ia-i-educacio/idees_ia_i_educacio.md`).
- Actualizar el `BACKLOG.md` del proyecto con una tarea de seguimiento del tipo «leer X y decidir si alimenta el capítulo Y».
- Actualizar la memoria del proyecto con un hecho nuevo si la fuente cambia el estado de las cosas.

**Espera confirmación** antes de hacer nada de eso. El motivo: el feedback sobre separación de dominios en `memory/feedback_domain_separation.md` y el feedback v3-overboard en `memory/feedback_v3_overboard.md` advierten contra forzar referencias entre dominios de proyecto. Deja que el principal decida qué proyecto o proyectos quieren de verdad la referencia.

### 7.5 Ofrece la integración en la wiki (también con aprobación previa, también conservadora)

Cuando la fuente esté incorporada e indexada, **ofrece** pasarla por la ingesta de la wiki. El proceso:

```bash
# Always dry-run first — shows the proposed change set, writes nothing.
python3 tools/wiki/ingest.py <source-rel-path>
```

El dry-run muestra:
- el resumen de extracción que ha producido el modelo (2-3 frases),
- las entradas existentes de la wiki que ganarían una referencia en su cronología,
- las entradas nuevas que se crearían como esqueleto (con el slug propuesto),
- las entradas ya enlazadas desde la fuente (idempotente: las fuentes ya ingeridas se saltan limpiamente).

Enseña al principal la salida del dry-run. Si la aprueba, aplica:

```bash
python3 tools/wiki/ingest.py --apply <source-rel-path>
```

Después ejecuta los dos scripts de regeneración para que las referencias cruzadas y los INDEX reflejen las entradas nuevas:

```bash
python3 tools/wiki/build_cooccurrence.py
python3 tools/wiki/render_indexes.py
```

Si el principal prefiere saltárselo, no pasa nada: la fuente sigue en `sources/` y puede ingerirse más adelante, en lote, con `tools/wiki/bootstrap.py --resume`.

**Por qué con aprobación y no automática:** el extractor a veces propone slugs nuevos de personas o de temas que son variantes de entradas existentes (p. ej., `juan-antonio-pereira` cuando ya existe `juanan-pereira`). El principal debería echar un vistazo a la lista de esqueletos nuevos antes de que entren, para que no se acumulen duplicados. La misma cautela vale para los temas: el extractor etiqueta de vez en cuando categorías genéricas más amplias que la wiki ya ha decidido no canonizar.

### 8. Informa

Termina con un informe breve al principal:
- Qué se ha añadido (ámbito + ruta).
- Qué se ha derivado (audio, transcripción, etc.).
- Qué se ha omitido (si hay algo, y por qué).
- Qué integración se ha ofrecido sin aplicarla.

## Lo que esta skill NO hace

- **No** edita borradores de proyectos, wikis de libros ni ficheros de memoria sin confirmación explícita.
- **No** mueve ni renombra ficheros que ya están en `sources/`. Si algo tiene que cambiar de ámbito, es otra tarea.
- **No** borra el original tras una derivación correcta. La política de archivo es «conservarlo todo»: el webm/mp4 original se queda junto al mp3/txt derivado.
- **No** intenta imitar la voz del principal. Si resumes una fuente en su README, que sea factual y de menos de 100 palabras. Los resúmenes con opiniones o enfoques van en los documentos del proyecto, donde el principal puede reescribirlos.

## Relacionado

- [../sources/INDEX.md](../sources/INDEX.md): el índice que mantiene esta skill.
- [../tools/transcribe/transcribe.py](../tools/transcribe/transcribe.py): el script de transcripción al que llama esta skill.
- [../tools/wiki/ingest.py](../tools/wiki/ingest.py): la herramienta de ingesta en la wiki de una sola fuente que se menciona en el paso 7.5.
- [../memory/feedback_index_maintenance.md](../memory/feedback_index_maintenance.md): por qué el índice debe mantenerse al día.
