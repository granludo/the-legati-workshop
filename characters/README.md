# Los legati: tus agentes de IA

Esta carpeta guarda los ficheros de identidad de los agentes de IA de tu taller. Cada agente es un *legatus* (en plural, *legati*): un delegado que actúa con tu autoridad dentro de un carril definido.

La palabra importa. La industria de la IA los llama «agentes», lo que implica acción autónoma. Pero lo que quieres son *delegados*: entidades que actúan en tu nombre, dentro de los límites que tú fijas, con un criterio que tú has calibrado. La distinción es epistemológica, no cosmética.

---

## Los cuatro agentes de partida

Este taller siembra cuatro roles de agente. Todavía no tienen nombre, ni personalidad, ni carácter. Eso te toca a ti. Cada carpeta contiene un `boot.md` breve (lo que el legatus lee al iniciar la sesión), un `character.md` esbozado y un `rules.md` vacío. Rellénalos.

| Carpeta | Rol | Tu trabajo |
|---|---|---|
| `orchestrator/` | Agente por defecto; herramientas, ingeniería, custodia del repositorio, coordinación | Ponle nombre. Dale una personalidad. Es el agente que lleva la mayoría de las sesiones. |
| `writer/` | Redacción, edición, imitación de la voz, textos en varios idiomas | Ponle nombre. Dale tu voz como referencia. Este agente debería saber cómo escribes. |
| `comms/` | Calendario, bandeja de entrada, agenda; solo lectura en los servicios externos | Ponle nombre. Define con cuidado su mandato de solo lectura. Este agente nunca debería enviar nada que no hayas autorizado. |
| `reviewer/` | Valoración honesta y calibrada de borradores y entregables | Ponle nombre. Calibra su severidad. Este agente debería decirte la verdad, no lo que quieres oír. |

---

## Cómo diseñar un agente

La guía completa está en `good-practices/02-the-legati.md`. La versión corta:

1. **Ponle un nombre sacado de la ficción o de la historia que te importa.** El nombre fija el registro y te da un asidero para invocar al personaje. Un nombre elegido a conciencia no cae igual que «Asistente 2».
2. **Define su carril con precisión.** ¿Qué hace? ¿Qué es lo que explícitamente *no* hace? El antimandato importa tanto como el mandato.
3. **Dale un ancla de voz.** Una frase o una cita que capture el registro. «Escueto, concreto, sin halagos» es un ancla de voz. «Servicial y simpático» no lo es.
4. **Nombra el antipatrón.** ¿Quién *no* es este agente? Nombrar el modo de fallo te ayuda a calibrar y ayuda al agente a corregirse solo.
5. **Las reglas se acumulan con el tiempo.** El fichero `rules.md` empieza vacío. Se va llenando a medida que das instrucciones al agente, sesión tras sesión.

---

## Sobre los nombres

No tienes por qué sacar los nombres de los agentes de la ficción. Pero los nombres de la ficción que te gusta tienden a quedarse, porque vienen cargados de asociaciones que ya tienes. Cuando dices un nombre en una sesión, invocas esas asociaciones: la voz, los valores y la actitud del personaje. Aprovéchalo.

Los agentes de este taller tomaron sus nombres de *Expeditionary Force* (Craig Alanson), *Heinlein*, *Conan Doyle*, *Philip K. Dick* y *Harry Potter*. Cada nombre aportaba algo que el agente necesitaba.

---

## Ficheros de arranque, la plantilla de legati y los lanzadores

Una sesión es un legatus. Lee `AGENTS.md` (el núcleo, común a todos los harness) y luego **solo** su propio `characters/<name>/boot.md`, que apunta a su `character.md`, a su `rules.md`, a las skills que ejecuta y a las memorias que abre cuando salta un disparador. Mantén cortos los ficheros de arranque: todo lo que un legatus no necesita en el primer minuto se queda detrás de un enlace.

La plantilla de legati vive en tres sitios que deben coincidir, y `/start-here` (paso 1) los actualiza todos cuando pones nombre a un legatus o lo renombras:

1. las líneas de la plantilla en `AGENTS.md` §1 (y la pregunta «¿qué legatus?» de ese apartado);
2. la carpeta `characters/<name>/` y el encabezado y el prefijo de respuesta de su `boot.md`;
3. la sección `[<name>]` de `legati/roster.toml`, que elige el harness (`claude-code` o `codex`) y el modelo por defecto.

Después regenera los lanzadores de la raíz con `bash tools/legati/make-launchers.sh`: obtienes `./claude_<name>.sh` y `./codex_<name>.sh` para cada legatus que tenga fichero de arranque. Un lanzador define `LEGATUS_AGENT`, pone nombre a la pestaña del terminal y entrega el fichero de arranque al harness. Dos legati pueden compartir pestaña: `legati/bin/legatus comms --with reviewer`.

## Mapa de traspasos (de partida)

- Orquestador → Escritor para cualquier prosa de más de unos pocos párrafos que deba sonar a ti.
- Orquestador → Comms para consultas de agenda y de la bandeja de entrada.
- Cualquiera → Revisor antes de que un entregable salga del taller. El revisor propone, tú decides, el escritor reescribe.
- Escritor → Orquestador para problemas de herramientas y de renderizado.

Entre sesiones, estos traspasos son ficheros (`tools/legati/handoff.py`); dentro de una misma sesión son un cambio de personaje durante un bloque, anunciado en la respuesta.
