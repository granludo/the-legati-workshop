# /start-here: guía de puesta en marcha del taller

**Quién la ejecuta:** el legatus orquestador (`orchestrator`), con Claude Code o con Codex (lánzalo con `./claude_orchestrator.sh` o `./codex_orchestrator.sh`).

**Cuándo invocarla:** una vez, al principio, cuando el repositorio está recién creado y todavía no has personalizado nada. También se puede volver a invocar para cualquier paso que te hayas saltado.

**Qué hace:** lleva al usuario por la configuración mínima para tener un taller que funcione y que sea suyo. Los pasos están ordenados por rendimiento: lo que más importa va primero.

---

## Antes de empezar

Dile esto al usuario:

> Te doy la bienvenida. Este andamiaje está montado, pero no personalizado. Vas a poner nombre a tus agentes, escribir un primer borrador de tu perfil de escritura y configurar las herramientas. Nada de esto tiene que ser perfecto el primer día: el sistema mejora a medida que lo usas.
>
> La puesta en marcha tiene siete pasos. Los tres primeros llevan alrededor de una hora en total y te dan la mayor parte del valor. El resto puede hacerse a lo largo de la semana siguiente. Dime si quieres saltarte un paso o dejarlo para más adelante.

---

## Paso 1: Ponles nombre a tus agentes (15 minutos)

**Qué hacer:**

Hazle al usuario estas preguntas, de una en una:

1. «¿Cómo quieres llamar a tu agente orquestador por defecto, el que se ocupa de la ingeniería y la coordinación? Es el agente con el que hablarás en la mayoría de las sesiones. Elige un nombre de la ficción, de la historia o de donde quieras. Puede ser serio o juguetón: lo que importa es que te apetezca decirlo.»

2. «¿Cómo quieres llamar a tu agente escritor? Es el que redacta, edita y escribe con tu voz. La misma regla: un nombre que te diga algo.»

3. «¿Quieres un agente de comunicaciones, uno que lea tu calendario y tu correo? Si es así, ¿cómo quieres llamarlo?» (Si dice que sí, avisa de que hará falta configurar el OAuth de Google Workspace: de eso se ocupa el paso 6.)

4. «¿Quieres un revisor, un agente que te dé opiniones secas y honestas sobre tus borradores y entregables? ¿Cómo quieres llamarlo?»

**Cuando tengas los nombres** (usa nombres de carpeta en minúsculas y de una sola palabra, por ejemplo `ada`): haz lo siguiente para cada legatus; para cualquier rol que el usuario no quiera, mira la nota de más abajo.

- Renombra la carpeta con `git mv characters/orchestrator characters/<name>` (y lo mismo con `writer/`, `comms/`, `reviewer/`) para que el historial la siga.
- En `characters/<name>/boot.md`: el encabezado, «Eres …» y el prefijo de respuesta (`[ADA]`). Quita el callout `[!todo]` sobre el cambio de nombre.
- En `characters/<name>/character.md`: el encabezado.
- En `AGENTS.md` §1: las líneas de la plantilla de legati y la pregunta «¿Qué legatus?» (`ada · …`), y el nombre del legatus por defecto.
- En `legati/roster.toml`: renombra cada `[section]`.
- Cada mención del antiguo nombre de rol en las líneas de traspaso de los demás ficheros de arranque, en `characters/README.md` (tabla y mapa de traspasos), en `skills/README.md` (la columna «Quién la ejecuta») y en `INDEX.md` (la tabla de agentes).
- Regenera los lanzadores de la raíz: `bash tools/legati/make-launchers.sh` (escribe `claude_<name>.sh` y `codex_<name>.sh` y archiva los antiguos, los que llevan el nombre del rol).
- Comprueba: `LEGATUS_DRY_RUN=1 ./claude_<name>.sh` imprime el comando que ejecutaría; `grep -rn "orchestrator\|writer\|comms\|reviewer" AGENTS.md characters legati skills/README.md` encuentra lo que quede.
- Haz commit a través del sync: `bash tools/git/sync.sh commit -m "workshop init: name legati <name1>, <name2>, <name3>, <name4>" -- AGENTS.md INDEX.md characters legati skills/README.md archive claude_*.sh codex_*.sh` (si el repositorio todavía no tiene remoto, añade `--no-push`).

Un rol que el usuario no quiera (a menudo, el de comunicaciones): mueve su carpeta a `archive/characters/` con `git mv`, quita su línea de la plantilla de legati y su sección de `roster.toml`, y ejecuta `make-launchers.sh`.

Comunícaselo al usuario: «Tus legati ya tienen nombre. Abre uno con `./claude_<name>.sh` o `./codex_<name>.sh`, o llámalo por su nombre en cualquier sesión.»

---

## Paso 2: Escribe tu perfil de autor (30 minutos)

Es lo más importante que puedes hacer por la calidad de lo que produce el taller. Sáltatelo y todo lo que escriban los agentes será genérico. Hazlo y el resultado empezará a sonar a ti.

**Qué hacer:**

Dile al usuario: «Ahora vamos a escribir un primer borrador de tu perfil de escritura. Te haré unas preguntas. Contesta con sinceridad: este documento es para los agentes, no para publicarlo.»

Haz estas preguntas. Toma notas mientras el usuario contesta. Usarás las respuestas para redactar el perfil.

1. «¿Cómo describirías el registro de lo que escribes? ¿Académico? ¿Ensayístico? ¿Conversacional? ¿Técnico? ¿Distinto según el contexto?»
2. «¿Qué texto tuyo te enorgullece, uno en el que de verdad sonabas a ti? ¿Qué hizo que funcionara?»
3. «¿Qué tics o patrones de escritura sabes que usas demasiado y procuras quitar al editar?»
4. «¿Hay palabras o expresiones concretas que odies cuando las escriben otros, cosas que te hacen parar y torcer el gesto?»
5. «¿Escribes en varias lenguas? Si es así, ¿hay diferencias de voz que quieras conservar?»
6. «¿Cómo sueles estructurar un argumento? ¿Primero el contexto histórico y luego la tesis? ¿Primero la tesis y luego las pruebas? ¿Otra cosa?»
7. «¿Cómo usas el humor cuando escribes, si es que lo usas? ¿Cuál es el antipatrón, el humor que a ti no te funciona?»

Redacta `principals/[your-name]/writing-profile.md` a partir de las respuestas del usuario. Usa la estructura de plantilla que ya tiene el fichero. Enséñale un borrador y deja que lo corrija.

Dile: «Esto es un primer borrador. Cada vez que una sesión produzca algo que no da con tu voz y sepas articular por qué, añade una nota a este fichero. Mejora con el tiempo.»

Renombra `principals/your-name/` a `principals/[their-name]/` con `git mv`. Actualiza las referencias en `AGENTS.md` §9 y en `skills/write-as-user.md` (renómbralo a `write-as-[their-name].md` y actualiza su fila en `skills/README.md` y en el `boot.md` del escritor).

Commit: `"init: first draft writing profile for [name]"`

---

## Paso 3: Prepara el documento de visión del mundo (20 minutos)

Es el documento que enseña a los agentes lo que crees. Sin él, los agentes escriben cosas que contradicen tus posiciones.

**Qué hacer:**

Dile al usuario: «El documento de visión del mundo es donde escribes tus posiciones intelectuales: lo que crees y que debería informar todo lo que escriban tus agentes. No hace falta que lo rellenes entero ahora. Con tres a cinco posiciones basta para empezar.»

Pregunta:
1. «¿Qué posición defiendes con fuerza que la mayoría de la gente de tu campo no defiende, o al menos no dice en voz alta?»
2. «¿Contra qué te descubres argumentando más a menudo en tu ámbito?»
3. «¿A qué marco o metáfora vuelves una y otra vez cuando piensas?»

Redacta de 3 a 5 entradas de visión del mundo en `principals/[their-name]/worldview.md`. Numéralas §1, §2, etc. Enséñale los borradores y deja que los corrija.

Dile: «Añade cosas aquí siempre que una sesión produzca algo que tú nunca dirías. Ese momento de "yo nunca lo diría así" es material nuevo para la visión del mundo.»

Commit: `"init: first worldview entries for [name]"`

---

## Paso 4: Configura tu primer proyecto (10 minutos)

**Qué hacer:**

Pregunta: «¿Cuál es el primer proyecto de escritura que quieres pasar por el taller? Ponle un nombre corto.»

Crea `writting-projects/[project-slug]/BACKLOG.md` con la estructura estándar (un directorio con un `BACKLOG.md` es lo que la herramienta de carriles llama proyecto: `python3 tools/legati/lane.py claim writting-projects/[project-slug] "<task>"`):

```markdown
# [Project name] — backlog

## Active
*(in progress now)*

## Up next
*(ready to start, ordered by priority)*

## Soon
*(committed but not started)*

## Done
*(completed items — most recent first)*

## Postponed
*(not now, not never)*
```

Añade el proyecto a `INDEX.md`.

Crea `memory/project-[slug].md` a partir de la plantilla de proyecto de `memory/_templates/`.

Commit: `"init: first project [project-slug]"`

---

## Paso 5: Ejecuta la comprobación de estado

Invoca `/status` para verificar que el repositorio está en buen estado y que el procedimiento de orientación funciona.

La comprobación de estado debería:
- Leer `INDEX.md` e informar de los proyectos activos
- Leer `memory/MEMORY.md` y confirmar que el perfil está en su sitio
- Listar las skills disponibles
- Señalar cualquier elemento `> [!todo]` abierto en los ficheros clave que todavía necesite la atención del usuario

Si quedan marcas `[!todo]` sin resolver en `AGENTS.md`, en los ficheros de arranque o en el perfil de escritura, sácalas ahora.

---

## Paso 6: Prepara esta máquina (de 20 a 60 minutos, según lo que tengas)

Haz lo que aplique. Anota el resultado como la sección de esta máquina en `memory/reference_hosts.md` (el ejemplo de la plantilla muestra la forma; `hostname -s` te da el encabezado). Todos los legati leen esa sección al arrancar, así que mantenla corta y fiel a la realidad.

**Remoto de Git (muy recomendable):**
- Pregunta: «¿Está este taller en un remoto de Git privado (GitHub, GitLab, tu propio servidor)? Es lo que permite que varias sesiones y varias máquinas compartan un mismo taller.»
- Si todavía no lo está: crea un repositorio **privado**, luego `git remote set-url origin <url>` (o `git remote add origin <url>`) y `bash tools/git/sync.sh push`. No subas nunca un taller personal a un repositorio público: contendrá borradores, notas y memorias.

**Claude Code:**
- No hay nada que instalar en el repositorio: el `.claude/settings.json` versionado ya lleva los hooks. Claude Code te pide una vez que confíes en la carpeta.
- Prueba: `./claude_<name>.sh` abre una pestaña con el nombre de ese legatus, y las primeras líneas de la sesión muestran el resumen `[legati]`.

**Codex (opcional, recomendable para tener una segunda familia de modelos):**
- `codex login` (flujo en el navegador), luego `bash tools/legati/install-hooks.sh codex`.
- Arranca Codex en el repositorio una vez y aprueba los hooks con `/hooks`.
- Prueba: `./codex_<name>.sh`; la sesión debería responder con el prefijo de ese legatus. Dentro del sandbox de Codex, el hook de arranque da un resumen local y pide ejecutar `bash tools/legati/session-start.sh --refresh` mediante una aprobación: es lo esperado.
- Opcional: asigna un legatus a Codex en `legati/roster.toml` (un revisor con una familia de modelos distinta de la del escritor da una segunda opinión independiente).

**La puerta de entrada `llm` (otros modelos):**
- Mira `tools/llm/README.md`: `uv tool install llm`, luego los plugins que necesites (`llm install llm-ollama` para un servidor Ollama local) y `llm keys set openai` para una clave de pago.
- Prueba: `llm models` lista lo que esta máquina puede llamar; `llm -m <model> 'say hi'` responde; `llm logs -n 1` muestra que ha quedado registrado.

**Generación de PDF:**
- Prueba: `pandoc --version && typst --version`
- Si falta alguno: `brew install pandoc typst` (macOS) o consulta la documentación de tu sistema operativo.
- Prueba la cadena completa: escribe un fichero markdown corto y ejecuta `/md2pdf` sobre él.

**Comprobación de referencias (si escribes trabajo académico):** `bash tools/refs-check/setup.sh`, y pon tu dirección de correo en `REFS_CHECK_CONTACT` (mira `tools/refs-check/README.md`).

**Google Workspace (para el legatus de comunicaciones, si está activado):**
- Mira `tools/google/README.md` para el procedimiento de configuración de OAuth.
- Necesitas: una cuenta de Google, crear una app OAuth en Google Cloud Console y pasar una vez por el flujo de autenticación. La primera vez lleva unos 30 minutos.

---

## Paso 7: Añade tu primera fuente

Elige algo que estés leyendo o con lo que estés trabajando ahora y ejecuta `/add-source` sobre ello. Así confirmas que la cadena de entrada de fuentes funciona y tienes un ejemplo concreto de cómo queda una fuente procesada.

Buenas primeras fuentes: un artículo en PDF que hayas leído hace poco, una charla de YouTube que quieras citar, un artículo web que guardaste en marcadores.

---

## Después de la puesta en marcha

Dile al usuario:

> El taller está montado. A partir de aquí, evoluciona a medida que lo usas. Unas cuantas cosas que conviene tener presentes:
>
> - Cuando un agente haga algo que quieras que deje de hacer, añade una memoria de feedback. Cuando haga algo perfecto, apúntalo también: las dos direcciones importan.
> - El perfil de escritura y la visión del mundo crecen mejor con el uso que rellenando plantillas por adelantado. Haz sesiones. Fíjate en lo que falla. Añade la regla.
> - Vale la pena leer la guía de buenas prácticas de `good-practices/` a lo largo de la próxima semana. No todo será relevante todavía: léela cuando tengas una duda sobre cómo debería funcionar algo.
> - Cuando añadas algo al sistema de ficheros, actualiza `INDEX.md` en el mismo commit. Es la única regla que de verdad no es opcional.
> - Haz commit con `bash tools/git/sync.sh commit -m "…" -- <paths>`, para que todas las sesiones y todas las máquinas vean el trabajo enseguida.
> - ¿Vas a tener varios legati a la vez, o dos harness, o dos máquinas? Lee antes `good-practices/08-many-legati-many-harnesses.md`.

Haz un último commit `"workshop setup complete"` que recoja lo que quede pendiente.

---

## Si el usuario quiere saltarse pasos

No pasa nada. Los tres más importantes son el paso 1 (nombres), el paso 2 (perfil de escritura) y el paso 4 (primer proyecto). El resto puede hacerse cuando haga falta. No impongas un orden lineal.
