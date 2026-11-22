# 8. Muchos legati, muchos harness

Durante su primer año, mi taller funcionó con un solo harness, Claude Code. (Un harness es el programa que envuelve al modelo en tu terminal, lee tus ficheros y ejecuta comandos.) Podía haber varias sesiones abiertas a la vez, pero todas eran de Claude Code, y todas leían al arrancar el mismo fichero largo de instrucciones.

En septiembre de 2026 añadí el Codex CLI de OpenAI y empecé a tener legati en dos Macs a la vez. La primera sesión real de Codex registró sus eventos como `unknown`: mis scripts buscaban el identificador de sesión donde lo guarda Claude Code, y Codex lo guarda en otro sitio. Los demás supuestos ocultos fueron saliendo en los días siguientes: instrucciones que solo tenían sentido para Claude Code, un sandbox que no puede escribir en `.git`, una memoria integrada que guarda sus notas fuera del repositorio. Este capítulo recoge lo que cambié entre septiembre y noviembre.

## Un núcleo, un apéndice por harness

El fichero de instrucciones tuvo que partirse. `AGENTS.md` es ahora el núcleo común a todos los harness: quiénes son los legati, cómo se orienta una sesión, las reglas que sigue toda sesión. Codex lo lee de forma nativa. Claude Code lee `CLAUDE.md`, que empieza con una importación de una línea, `@AGENTS.md`, así que los dos harness cargan el mismo núcleo.

Cada harness tiene un apéndice corto con solo lo que le es propio: sus hooks, cómo invoca las skills, qué permite su sandbox. La prueba para una línea nueva: si nombra un harness, va en el apéndice de ese harness.

## Un legatus por sesión

Una sesión es un legatus, no el taller entero. El lanzador, `legati/bin/legatus <name> [claude-code|codex]`, define `LEGATUS_AGENT`, pone nombre a la pestaña del terminal y le pasa al harness el fichero de arranque de ese legatus. `bash tools/legati/make-launchers.sh` escribe un envoltorio por legatus en la raíz, así que en la práctica tecleas `./claude_writer.sh` o `./codex_reviewer.sh`. Vuelve a ejecutarlo cuando añadas o renombres un legatus.

El motivo es el contexto. Una sesión que lleva encima todos los legati lleva las reglas de todos, y al escritor no le sirven de nada las reglas de la bandeja de entrada del agente de comunicaciones.

Sin lanzador, la sesión pregunta qué legatus tiene que ser antes de hacer nada más, aunque tu primer mensaje ya parezca trabajo.

Dos legati pueden compartir pestaña: `legatus comms --with reviewer`. El que lleva la voz cantante responde por defecto, el acompañante responde cuando el trabajo llega a su carril, y cada uno mantiene su propio prefijo de respuesta. Las voces no se mezclan nunca. Mi taller tiene ocho legati, y dos de ellos comparten pestaña casi todos los días, porque lo que recoge uno es justo aquello con lo que trabaja el otro.

## Ficheros de arranque y una orientación barata

Cada legatus tiene un fichero de arranque, `characters/<name>/boot.md`, de una página más o menos: sus carriles, las skills que ejecuta, las memorias que solo abre cuando salta su disparador, a quién pasa el trabajo y su voz. Cada línea de memoria dice cuándo abrirla, por ejemplo «antes de redactar».

Al arrancar, un legatus lee su fichero de arranque y la sección de esta máquina en el perfil de máquinas (`memory/reference_hosts.md`, que imprime `tools/legati/host-section.sh`). Todo lo demás se abre cuando algo lo dispara. En mi taller, leerlo todo al arrancar había llegado a costar unos 250 KB antes de la primera acción útil.

## Git es el bus

Las sesiones en máquinas y harness distintos se hablan a través de git. Toda escritura en git pasa por un único script:

```bash
bash tools/git/sync.sh commit -m "Subject" -- path/one.md path/two.md
```

Solo prepara las rutas que nombras (nunca `git add -A`), añade los trailers `Legatus:`, `Harness:` y `Host:`, hace rebase sobre origin y hace push en el acto. El push es lo que más importa: un commit que no se ha subido no existe para los demás. Los trailers permiten que `git log` te diga qué legatus, con qué harness y en qué máquina hizo cada cambio.

El primer día completo con dos Macs y dos harness dio 30 commits, en un historial lineal, sin un solo conflicto.

## Carriles

Antes de trabajar en un proyecto, una sesión reserva su carril con `python3 tools/legati/lane.py claim <project-dir> "<task>"`. La reserva es un callout al principio del `BACKLOG.md` de ese proyecto, con su commit y su push como todo lo demás. Otra sesión que ve una reserva reciente se retira o se coordina. Una reserva de más de 24 horas se considera caducada. `lane.py release` cuando termines.

Los carriles solo funcionan si los legati los usan. Aquel primer día limpio, solo un legatus reservó alguno, así que ahora `sync.sh commit` avisa cuando una sesión hace commit en un proyecto sin tener su carril.

## Los traspasos son ficheros

Los mensajes entre legati son ficheros, uno por mensaje, en `legati/handoffs/`. `handoff.py send` escribe uno y lo sube, `inbox` lista lo que te espera, `ack` lo archiva. Como cada mensaje es su propio fichero, dos remitentes nunca editan la misma línea, y los pull nunca chocan en los mensajes.

Las sesiones de una misma máquina tienen además el chat del Observatorio (`obs.py say`, `obs.py chat`). Nunca sale de la máquina, y por eso existen los traspasos por git.

Los hooks conectan todo esto con la sesión. Al arrancar, un hook muestra quién eres y dónde estás, hace pull cuando el árbol de trabajo está limpio y no hay nada local pendiente de subir, y lista los commits desde la última vez que miraron esta máquina y este harness, los carriles activos y los traspasos sin leer. Un hook por turno muestra los traspasos nuevos a medida que llegan.

## Codex, en concreto

Ejecuta `codex login` una vez. Luego `bash tools/legati/install-hooks.sh codex` escribe `.codex/hooks.json` y `.codex/config.toml` y marca el repositorio como de confianza. Arranca Codex en el repositorio, aprueba los hooks con `/hooks` y, a partir de ahí, lánzalo con `./codex_<name>.sh`.

La configuración fija un sandbox workspace-write con acceso a la red, aprobaciones bajo petición y las memorias propias de Codex desactivadas. El `memory/` del repositorio es la única memoria: una segunda, invisible para los demás harness, partiría en dos lo que sabe el taller.

Dentro del sandbox, el hook de arranque no puede escribir en `.git`, así que no puede hacer pull. En su lugar imprime un resumen local, y el agente completa la actualización con un comando que apruebas tú. Es el sandbox haciendo su trabajo: déjalo como está.

## Un modelo por legatus

`legati/roster.toml` fija un harness y un modelo para cada legatus. El uso que me importa es la revisión. Un revisor que funciona con una familia de modelos distinta de la del escritor da una segunda opinión independiente de verdad. Un modelo que revisa prosa de su misma especie tiende a aprobar lo que él mismo habría escrito.

## La capa duradera sigue siendo neutral

Las skills son ficheros markdown planos que se invocan en lenguaje natural: «Revisor, mira el capítulo 3». Los comandos de barra son una comodidad en los harness que los tienen, nunca el único camino. Los hooks y las configuraciones son propios de cada harness, así que viven en `.claude/` y `.codex/`, en cada máquina.

El capítulo 7 defendía la portabilidad. Un segundo harness es donde ese argumento se pone a prueba, y desde entonces mi taller ha incorporado dos más. Cada uno ha necesitado un apéndice y un lanzador, uno de ellos también un adaptador de hooks, y las skills y las memorias se han quedado como estaban.

## Lo que digo y lo que oyen los legati

Dos lecciones sobre mis propias palabras solo se hicieron visibles con varios legati.

Un acuse de recibo no es una autorización. Empiezo muchas respuestas con «ok», que quiere decir «te he oído, sigue». Un legatus preguntó si podía desplegar una versión nueva de un servicio, le contesté «ok, explica...», y desplegó. En mi manera de hablar, «ok» no quiere decir nunca «adelante», y no pienso cambiar mi manera de hablar. La autorización sale de la instrucción en sí, nunca del «ok» que va delante.

Un comentario de pasada no es una regla permanente. En una sola tarde, mi legatus escritor convirtió tres comentarios en reglas: un inciso que explicaba un corte, una broma y una decisión sobre dónde iría un pasaje. Una regla solo se escribe cuando el principal la marca como tal. Una decisión va al backlog del proyecto, y una broma es una broma.

Los dos malentendidos se corrigen fácilmente en una conversación. Con varios legati, una corrección dada en una pestaña no llega a ninguna de las demás, y el mismo malentendido vuelve de la mano de otro legatus. Por eso las dos reglas viven ahora en `AGENTS.md`, donde las lee cada legatus con cada harness.

## Lo que sigue necesitándote

Unos cuantos pasos siguen siendo cosa tuya. Claude Code te pide que confíes en la carpeta la primera vez. Codex te pide que apruebes sus hooks una vez, y otra vez cada vez que cambian. Cada máquina necesita sus propios inicios de sesión. Y tú decides qué legatus corre dónde, con qué harness y con qué modelo. Son decisiones del principal, y ningún script debería tomarlas por ti.
