# 7. El andamiaje

El repositorio del taller es el andamiaje de una colaboración de largo recorrido. Entender qué quiere decir eso en términos de estructura vale los diez minutos que se tarda en leer esto.

## AGENTS.md es el contrato

`AGENTS.md` es lo primero que lee cualquier agente al empezar la sesión, con cualquier harness: Codex lo lee de forma nativa, y Claude Code lo carga mediante la importación de una línea, `@AGENTS.md`, que hay al principio de `CLAUDE.md`. No es documentación: son instrucciones de funcionamiento. Define, o señala:
- Quiénes son los agentes y cuáles son sus carriles
- Qué skills hay y cómo se invocan
- Qué niveles de cómputo existen y cuándo usarlos
- Cuáles son las reglas innegociables

Cuando cambias un comportamiento (añadir un agente, retirar una skill, cambiar una regla de enrutado), el cambio vive en `AGENTS.md`. No en un fichero de memoria, no en un comentario dentro de un script. En el contrato. Si el cambio solo afecta a un harness, va en el apéndice de ese harness (el de Claude Code está en `CLAUDE.md`; el de Codex, al final de `AGENTS.md`).

## La disciplina de la portabilidad

El andamiaje del taller no debería depender de ninguna herramienta, plataforma o proveedor de IA concretos. Las skills son ficheros markdown planos. La memoria es markdown plano. Las herramientas son scripts de Python sin más. Las identidades de los agentes son markdown plano. Nada de esto requiere Claude Code en particular, ni ninguna versión concreta de Claude, ni ningún plugin concreto.

No es casualidad. El repositorio es la capa duradera precisamente porque no depende del proveedor. Cuando Claude Code añada un sistema de hooks nuevo, o cambie el formato de sus comandos, o lo sustituya una herramienta mejor, el taller sobrevivirá. La capa duradera son las skills, las memorias y las identidades de este repositorio. La IA es el motor que va rotando por debajo.

La consecuencia práctica: cuando construyas una skill o una herramienta nueva, no la ates a un mecanismo propio de Claude Code a menos que no haya alternativa. Invocar en lenguaje natural («ejecuta la skill de status») es más portable que un comando de barra, que depende de que la shell lo interprete bien.

## El mantenimiento de INDEX.md: la regla que no es opcional

Cada cambio en el sistema de ficheros (cada fichero que se añade, se renombra, se mueve o se borra) exige actualizar `INDEX.md` en el mismo commit. Sin excepciones.

Parece una carga innecesaria. Es lo contrario. El INDEX es lo que permite a cualquier sesión (cualquier agente, cualquier modelo, cualquier herramienta futura) orientarse en el repositorio sin leer todos los ficheros. Cuando el INDEX está desfasado, el repositorio se vuelve opaco. Los repositorios opacos acumulan código muerto, borradores superados y referencias huérfanas que nadie quiere limpiar porque nadie sabe qué se puede quitar sin peligro.

La disciplina es esta: «terminado» quiere decir que el INDEX está actualizado.

## La regla de archivar, no borrar

No borres nunca nada del taller. Borradores viejos, notas superadas, scripts huérfanos, experimentos fallidos: todo va a `archive/`, con una nota breve sobre qué era y por qué se apartó. El archivo es conservación para excavar en el futuro, no una papelera que haya que vaciar.

El motivo es en parte práctico (querrás recuperar ese borrador más a menudo de lo que crees) y en parte intelectual. La historia de lo que probaste y abandonaste forma parte del registro intelectual de un proyecto. Dentro de un año puede que no recuerdes por qué descartaste un enfoque. La entrada del archivo te lo dice.

## Varias sesiones, un mismo repositorio

Cuando estás metido a fondo en un proyecto, es habitual tener varias sesiones a la vez, con Claude Code, con Codex o con los dos: una para escribir, otra para ingeniería, otra con las herramientas en segundo plano. No pasa nada, pero exige coordinación. El mecanismo de coordinación es el `BACKLOG.md` de cada proyecto. Antes de que una sesión empiece a trabajar en la carpeta de un proyecto, mira en el BACKLOG qué hay en curso. Antes de hacer commit, actualiza el BACKLOG.

El corolario: no tengas dos sesiones regenerando a la vez el mismo panel o el mismo fichero compartido. Las condiciones de carrera en un repositorio de texto plano se manifiestan como errores de «File has been modified since read» y commits a medias. La convención del BACKLOG evita la mayoría. El capítulo 8 cubre el resto: los carriles, los traspasos y la disciplina de commits que mantiene a varios legati trabajando en varias máquinas y con varios harness.

## Cuándo añadir una skill

Añade una skill cuando te descubras explicándole a un agente la misma operación de varios pasos más de dos veces. Si en cada sesión de escritura tecleas «lee el perfil de escritura, comprueba el dominio, usa la cadena de tres documentos, haz un barrido de tics de prosa antes de entregar», eso es una skill. Escríbela una vez; invócala siempre.

El fichero de la skill no es un procedimiento. Es un briefing: qué es la operación, por qué importa y qué tiene que comprobar el agente antes, durante y después. Un buen fichero de skill es corto: menos de 200 líneas. Si es más largo, estás documentando casos límite que van en `memory/` o en el `rules.md` del agente.
