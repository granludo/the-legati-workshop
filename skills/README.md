# skills/: la convención de la carpeta y la tabla

Cuando el principal invoca una skill (dirigiéndose a un legatus en lenguaje natural, «Escritor, pásale el unslop al capítulo 3»; nombrándola de pasada, «usa /add-source con esta URL»; o tecleando `/<name> <args>`), **lee `skills/<name>.md` de este repositorio y sigue las instrucciones que contiene.** Esta carpeta es la fuente de verdad de todas las skills del taller, con cualquier harness.

**La invocación en lenguaje natural es la canónica.** Un comando de barra a secas puede interceptarlo el analizador del propio harness antes de que lo vea el legatus; en ese caso, dirígete al legatus sin más. Los ficheros de skill son markdown plano, no comandos de barra del harness, así que funcionan igual en Claude Code que en Codex ([memory/feedback_scaffolding_portability.md](../memory/feedback_scaffolding_portability.md)).

**Esta tabla es la autoridad**; el `boot.md` de cada legatus enumera el subconjunto que ejecuta. Añadir una skill = el fichero + una fila aquí. Un nombre sin fichero → dilo, no lo adivines.

| Invocación | Fichero | Quién la ejecuta | Qué hace |
|---|---|---|---|
| `/start-here` | [start-here.md](start-here.md) | orchestrator | Puesta en marcha: pon nombre a tus legati, escribe tu perfil, configura los dos harness y tu primer proyecto. |
| `/status` | [status.md](status.md) | orchestrator | Resumen de orientación en solo lectura: proyectos activos, carriles, traspasos, primeros elementos del backlog, skills, decisiones abiertas. |
| `/write-as-[you]` | [write-as-user.md](write-as-user.md) | writer | Carga tu perfil de escritura y tu visión del mundo antes de cualquier tarea de escritura. Renómbrala después de la puesta en marcha. |
| `/add-source` | [add-source.md](add-source.md) | orchestrator (cadena), writer (análisis) | Incorpora una fuente (YouTube, PDF, audio, artículo web, texto) a `sources/`. |
| `/md2pdf` | [md2pdf.md](md2pdf.md) | cualquiera | Convierte markdown en PDF listos para imprimir con pandoc + Typst. |
| `/image-gen` | [image-gen.md](image-gen.md) | orchestrator | Genera una imagen diseñada mediante una API de imágenes. De pago: úsala a conciencia. |
| `/playwright` | [playwright.md](playwright.md) | cualquiera | Un navegador de verdad para páginas que dependen de JS o que exigen inicio de sesión: un script reutilizable en `tools/<slug>/`. |
| `/observatory` | [observatory.md](observatory.md) | cualquiera | Quién está activo, qué hace cada sesión, bloqueos orientativos de ficheros, chat en la misma máquina. |
| `/unslop-text` | [unslop-text.md](unslop-text.md) | writer (cualquier legatus sobre lo que produce él mismo) | Quita de un texto lo que delata a la IA: listas negras por lengua (inglés, catalán, castellano), una auditoría de adverbios, construcciones formulaicas, prosa amanerada. Solo resta. |
| `/throat-clearing-review` | [throat-clearing-review.md](throat-clearing-review.md) | writer informa, reviewer gradúa | Ajuste por etapas de un documento que va a publicarse, en cuatro pasadas: formulación, párrafos redundantes, tablas y figuras, relleno dentro de las frases. Primero el informe; no se edita nada hasta que decide el principal. |
| `/korben-dallas` | [korben-dallas.md](korben-dallas.md) | cualquiera, solo si se pide | Comprime la respuesta, no el trabajo: el veredicto primero, dos párrafos cortos como mucho. Solo en el chat; los ficheros conservan su tamaño completo. |

> [!todo] Tú
> A medida que añadas legati con skills propias (una actualización de comunicaciones, una lista de comprobación del revisor para tu campo), añade filas aquí y lista la skill en el `boot.md` de ese legatus.
