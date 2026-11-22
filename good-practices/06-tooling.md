# 6. Herramientas

El taller viene con herramientas que funcionan. Así es como conviene pensar cuándo usar cada una.

## Los tres niveles de cómputo

**Local (Ollama)**: modelos que corren en tu propio hardware. Gratis una vez instalados, privados (tus datos no salen de tu máquina), lentos comparados con las API en la nube. Lo mejor para el trabajo mecánico en volumen: traducir entre lenguas donde los modelos locales dan la talla, resumir documentos largos, clasificar y etiquetar, limpiar transcripciones. La regla para los modelos locales: cuanto más grande, mejor, casi sin excepción. Un modelo de 125B que va lento es más útil que uno de 27B que va rápido, porque el grande comete menos errores de precisión. No uses modelos locales pequeños para ganar tiempo: el tiempo que ahorras generando el borrador lo gastas corrigiendo los errores.

**La IA de la sesión (el modelo que mueve tu sesión de Claude Code o Codex)**: el modelo con el que estás hablando ahora mismo. Lo mejor para el trabajo intelectual de peso: todo lo que requiera tu voz, todo lo que requiera síntesis entre fuentes, todo lo que requiera un juicio calibrado sobre una cuestión compleja. No mandes aquí el trabajo mecánico: para tareas en volumen es más lento, y te cuesta más atención de la que vale.

**API de pago (OpenAI, o el proveedor de frontera al que tengas acceso)**: segunda opinión, revisión a fondo, tareas en las que ni lo local ni la IA de la sesión llegan al nivel de calidad. Úsala a conciencia. Cada llamada cuesta dinero de verdad; regístrala. No vayas ahí por defecto porque sea cómodo.

## La decisión de enrutado en la práctica

Antes de mandar una tarea por lotes a un modelo, pregúntate:
- ¿Es mecánica? (traducción, resumen, clasificación, limpieza) → Ollama local
- ¿Requiere mi voz o un juicio interpretativo? → IA de la sesión
- ¿Es una segunda opinión o una revisión a fondo que lo local no puede hacer? → API de pago, sabiendo lo que cuesta

El error más común es mandarlo todo a la IA de la sesión porque es cómodo. Es el patrón de la máquina expendedora: obtienes respuestas, pero no construyes nada. Para las tareas mecánicas, los modelos locales con una plantilla son a la vez más baratos y más rápidos.

## Una sola puerta de entrada: el comando `llm`

Toda llamada a un modelo fuera de tu sesión pasa por un solo comando, `llm`, de Simon Willison (https://llm.datasette.io). Los modelos locales de Ollama y las API de pago usan la misma sintaxis, y `llm` registra cada prompt y cada respuesta en una base de datos SQLite en tu máquina, así que luego puedes ver qué enviaste, a qué modelo y qué te devolvió (`llm logs`). La instalación está en `tools/llm/README.md`.

Para los modelos locales, instala Ollama y el plugin `llm-ollama` (`llm install llm-ollama`). Si Ollama corre en local, `localhost:11434` es el valor por defecto, y tus modelos locales aparecen en `llm` junto a los de pago.

Los ayudantes antiguos, `tools/ollama/call.py` y `tools/openai/call.py`, se quedan solo para los scripts que ya los usan. No los llames a mano ni escribas código nuevo contra ellos: una llamada que esquiva `llm` esquiva el registro.

Consulta siempre la lista de modelos antes de escribir una tarea que dependa de un modelo concreto:
```bash
llm models
```

No escribas nombres de modelos a fuego en los scripts: Marc se baja modelos nuevos a menudo, y un script que hace referencia a `qwen3.5:27b` puede estar usando un modelo peor que `qwen3.5:122b` sin saberlo.

## Generación de PDF: pandoc + Typst

`/md2pdf` es la skill. Usa pandoc para convertir el markdown a Typst, y luego Typst para pasar a PDF. La plantilla académica (`academic-template.typ`) se ocupa de las fuentes tipográficas, los márgenes, las citas y la maquetación. Para casi todo no hace falta tocar la plantilla: la skill se encarga de la invocación.

Dos cosas que conviene saber de la cadena de herramientas: Typst compila más rápido que LaTeX y no necesita más instalación que `brew install typst`. Si ya tienes flujos de trabajo con LaTeX, puedes invocar pandoc con la opción `--pdf-engine=xelatex`. La skill admite las dos vías.

## Transcripción: mlx-whisper

`tools/transcribe/` usa mlx-whisper para transcribir audio en local. Corre de forma nativa en Apple Silicon y es lo bastante rápido para el uso real. Para cada fichero de audio produce una transcripción en bruto, que debería ir seguida de una pasada de revisión con un LLM para cazar los errores característicos (nombres propios, términos técnicos, cambios de idioma). No cites nunca una transcripción sin haberla revisado.

## Verificación de referencias: tools/refs-check

Antes de que un artículo salga del taller, cada referencia necesita verificación. `tools/refs-check/check_refs.py` se encarga de ello: consulta varias bases de datos académicas (OpenAI, Semantic Scholar, CrossRef, arXiv), comprueba que las URL siguen vivas y recupera los resúmenes para compararlos. El resultado es un veredicto por referencia: confirmed, title-mismatch, unreachable o escalate. Cualquier referencia que no salga como «confirmed» bloquea el envío.

La regla dura: no te inventes nunca una URL o un DOI para rellenar metadatos que faltan. Deja el campo vacío y que se escale hasta ti. Un artículo con unas cuantas marcas [URL missing] tiene arreglo. Un artículo con citas inventadas no lo tiene.

## Google Workspace: el carril del agente de comunicaciones

Si configuras el agente de comunicaciones, usará la CLI `gws` (Google Workspace CLI) para acceder a Gmail, Calendar y Drive. La configuración requiere una autenticación OAuth que se hace una sola vez: los pasos están en `tools/google/README.md`. La restricción clave: el alcance de OAuth es de solo lectura. El agente de comunicaciones puede ver tu calendario y tu correo; no puede enviar, crear eventos ni modificar nada. Esto se impone en la propia credencial.
