# tools/ollama/

> [!note] Preferible: `llm`
> El trabajo nuevo llama a los modelos mediante el comando `llm` ([tools/llm/README.md](../llm/README.md)), que también llega a Ollama con el plugin `llm-ollama` y registra todas las llamadas. Este script auxiliar se queda para los scripts que ya lo usan (`tools/wiki/`).

Script auxiliar para uno o varios servidores Ollama: un ordenador de sobremesa potente de tu red, o `localhost`. Edita la lista `SERVERS` al principio de `call.py` con tus direcciones (los valores que trae son los de la red local del taller original y en la tuya no responderán).

El script auxiliar sondea los servidores por orden y elige el primero accesible que tenga el modelo pedido. Prefiere modelos grandes: los modelos locales pequeños se degradan enseguida con contextos largos y en idiomas distintos del inglés.

## Uso rápido

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

Cero dependencias: solo usa `urllib` de la biblioteca estándar. Funciona con `python3` sin más o con `uv run`.

## Cuando falla

Dos modos de fallo:

**Código de salida 2: ningún servidor accesible.** Ningún servidor de `SERVERS` ha respondido al sondeo. Normalmente esta máquina está fuera de la red donde vive el servidor (un portátil en la wifi de un congreso), o el servidor está apagado.

```
ERROR: no Ollama server reachable. Tried: <your SERVERS list>
HINT:  Fall back to the session model for this task and tell the principal you fell back.
```

**Código de salida 3: modelo no disponible.** Había un servidor accesible, pero no tenía el modelo pedido. El script auxiliar imprime lo que sí está disponible para que puedas elegir una alternativa.

**Protocolo de respaldo:** cuando un agente que lo llama (Claude) ve el código de salida 2:
1. Avisa al principal de que ha recurrido al modelo de la sesión.
2. Hace la tarea directamente en la conversación actual.
3. No se degrada en silencio ni reintenta en bucle.

Cuando el agente ve el código de salida 3: ejecuta `list` para ver la flota actual, elige una alternativa sensata y reintenta una vez. Si sigue sin estar disponible, avisa al principal.

## Política de ventana de contexto

Según la experiencia del taller original, los **modelos pequeños** (por debajo de 70B parámetros) se degradan cuando el contexto pasa de ~64k, así que el script auxiliar limita `num_ctx` a 65536 para ellos. Los modelos más grandes (70B o más) usan su valor por defecto (que en este servidor está configurado alto). Puedes cambiarlo con `--num-ctx N` si sabes lo que haces.

## Tiempos de espera

Por defecto, 900 segundos (15 min). Los modelos locales son lentos en la primera llamada (calentamiento) y en las generaciones largas. Si no basta, cámbialo con `TIMEOUT_SECONDS` en `call.py` o pasa un prompt más corto.

## Descubrimiento dinámico de modelos

Los modelos de los servidores cambian con el tiempo. **Ejecuta siempre `list` primero** para ver qué hay disponible en lugar de dar por hecho que existe un modelo concreto. Los modelos de hoy pueden no ser los de ayer, y qué servidor tiene qué modelo puede cambiar entre descargas.

## Cuándo mandar tareas aquí y cuándo a Claude Opus

**Usa el Ollama local (Qwen 3.5 122B o el modelo «rápido» que toque) para:**
- Borradores rutinarios de traducción (CA ↔ ES ↔ EN, que el principal reescribirá)
- Resúmenes de material de fuentes largo
- Clasificación / etiquetado
- Limpieza de transcripciones (corregir entidades con nombre, eliminar alucinaciones)
- Esqueletos de esquema iniciales que el principal sobrescribirá
- Operaciones masivas sobre texto (las regex no bastan; con semántica basta)

**Usa Opus para:**
- Todo lo que requiera la voz del principal (necesita el perfil de escritura + la visión del mundo)
- Síntesis intelectual, razonamiento entre dominios
- El diálogo editorial con el principal
- Versiones finales de capítulos y artículos
- Decisiones y compromisos estructurales

**Regla práctica:** si una tarea es **mecánica y voluminosa**, Ollama. Si es **interpretativa y crítica**, Opus.

## Referencia en la memoria

Consulta [../../memory/reference_ollama_server.md](../../memory/reference_ollama_server.md) para la referencia canónica de infraestructura, que se mantiene al día con cualquier cambio de modelos o de servidores.
