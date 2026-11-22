# tools/wiki/

Scripts que construyen y mantienen la capa de wiki e índices sobre el markdown del taller.

> [!note] Hechos para el taller original
> Estos scripts se escribieron para un taller concreto: sus carpetas, sus legati y sus servidores de modelos (mira los selectores `SERVERS` / backend al principio de `ingest.py` y `bootstrap.py`). Léelos como un ejemplo resuelto que adaptar, no como una herramienta llave en mano. Los registros de ejecución (`*-log.md`) se escriben junto a los scripts y están en el gitignore.

## Ficheros

- **`bootstrap.py`**: esqueleto de primera pasada. Recorre las carpetas del ámbito, llama a Ollama (qwen3.5:122b) para cada fichero con un presupuesto de 16k de contexto, agrega los resultados de todos los ficheros y escribe esqueletos por faceta en `wiki/<facet>/<slug>.md`. Caché por hash de fichero → idempotente al volver a ejecutarlo. Se ejecuta con `python3 tools/wiki/bootstrap.py [--smoke|--dry-run|--resume|--limit N|--skip-write]`.
- **`chunk.py`**: divide el markdown largo en trozos que caben en 16k de contexto para Ollama. Estrategia: cortes por H2 → por párrafo → por frase. Reutilizable desde cualquier herramienta afín al bootstrap de la wiki.
- **`validate.py`**: comprobador de coherencia del árbol de la wiki: wikilinks rotos, slugs duplicados, entradas sin fuentes, fuentes que no están en disco. Ejecútalo después de un bootstrap; se puede volver a ejecutar en cualquier momento sin riesgo.
- **`bootstrap-log.md`**: registro de ejecución, solo de anexado, que escribe `bootstrap.py`. Recoge cada análisis por fichero, cada recuento agregado, cada fallo y cada punto de «decisión que necesita el principal».
- **`cache/`**: en el gitignore. Salidas de Ollama por fichero, indexadas por el SHA-256 del contenido. Al volver a ejecutar `bootstrap.py --resume` se saltan los ficheros cuyo hash coincide.

## Ámbito

Carpetas dentro del ámbito (solo ficheros markdown):
- `writting-projects/`: salvo los directorios de tema y de compilación de Hugo (`themes/`, `public/`, `resources/`, `layouts/`, `archetypes/`, `static/`)
- `characters/`: los ficheros de identidad de los legati
- `principals/`: los autores humanos (tú)
- `memory/`: el sistema de memoria persistente
- `sources/`: el material de fuentes en bruto
- `engineering-projects/`: carpetas de trabajo de ingeniería
- Ficheros seleccionados de la raíz: `INDEX.md`, `BACKLOG.md`, `PROJECTS.md`, `TODO.md`, `CLAUDE.md`, `README.md`

Fuera del ámbito:
- `inbox/`: el saber de correo y calendario del legatus comms (volátil, en un carril aparte, una regla del taller original)
- `archive/`: conservado pero inactivo
- `confidential/`: en el gitignore
- `worldview-draft/`: piloto de grafo por máquina (en el gitignore, puede no existir en todas las máquinas)

## Restricciones

- **Solo `qwen3.5:122b`** (según `memory/feedback_ollama_big_guns_only.md`). Los dos Studios son accesibles desde esta máquina.
- **Contexto máximo de 16k** (según `memory/feedback_ollama_context_under_16k.md`). `chunk.py` impone un presupuesto de trabajo de 10k tokens de entrada por llamada.
- **Ningún commit de git** durante el bootstrap. El script escribe ficheros; el principal hace el commit.

## Salida

- `wiki/<facet>/<slug>.md`: esqueletos por entrada. Frontmatter (type, slug, status, fechas, source-count) + Summary + Timeline (construida automáticamente a partir del git log de las fuentes enlazadas) + marcador de Evolution + lista de Sources + marcador de Cross-references.
- `wiki/<facet>/INDEX.md`: índice alfabético de la faceta.
- `wiki/INDEX.md`: mapa de primer nivel de la wiki.
- `wiki/keywords/keywords.md`: referencia plana y alfabética de palabras clave (términos que aparecen en ≥2 ficheros, heurística de tokens con mayúscula inicial).

## Volver a ejecutarlo

Dos motivos para volver a ejecutarlo:
1. **Reanudar tras una ejecución incompleta**: `python3 tools/wiki/bootstrap.py --resume`. Los aciertos de caché son gratis; solo se vuelven a analizar los ficheros que han cambiado.
2. **Iterar sobre el prompt o el esquema**: borra la caché (`rm -rf tools/wiki/cache/`) y vuelve a ejecutarlo. Obliga a hacer llamadas nuevas a Ollama para todo.

Tras cualquier reejecución, ejecuta `python3 tools/wiki/validate.py` para detectar enlaces rotos y huérfanos.

## Mantenimiento a partir de ahora

El bootstrap es una **primera pasada**. Mantenimiento en régimen estable:
- **Al tocar**: cuando se añade, edita o mueve un fichero de contenido en las carpetas del ámbito, las entradas de la wiki que lo referencian deberían tocarse también en el mismo commit. El hook pre-commit de `tools/git-hooks/pre-commit-wiki-check.sh` avisa cuando se relaja esta disciplina.
- **Barrido semanal del orquestador**: ejecución periódica de `validate.py`, con propuestas de actualización para las entradas cuyo `last-touched` se ha quedado atrás.
- **Rellenar la cola larga**: el bootstrap deja muchas entradas como esqueletos (frontmatter generado + fuentes + cronología; Summary/Evolution de relleno). El orquestador y el escritor van rellenando resúmenes y evolución a medida que el trabajo toca los ficheros subyacentes. Las entradas de más valor (proyectos principales, personas con nombre, ideas clave) tienen prioridad.
