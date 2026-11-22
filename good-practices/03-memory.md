# 3. El sistema de memoria

El sistema de memoria es lo que convierte una serie de sesiones en una colaboración continua. Sin él, cada sesión empieza de cero: el agente no sabe quién eres, en qué trabajas, qué correcciones le has dado ya ni qué decisiones has tomado. Con él, los primeros cinco minutos de cada sesión se pueden dedicar a trabajar de verdad en lugar de a reconstruir el contexto.

La idea clave es la distinción entre un fichero de memoria y una nota. Una nota es algo que has escrito tú. Un fichero de memoria es algo que el agente lee al empezar la sesión. La disciplina de escribir ficheros de memoria es la disciplina de preguntarse: «¿qué necesitaría saber un agente nuevo, que solo lee este repositorio, para servirme bien?».

## Los cuatro tipos de memoria

**Las memorias de usuario** tratan de ti: tu rol, tu experiencia, cómo prefieres trabajar, qué te saca de quicio. Una buena memoria de usuario no es una biografía; es un briefing. «Tengo veinte años de experiencia en ingeniería del software, pero esta es mi primera incursión seria en la escritura académica» es útil. «Me gusta trabajar por la mañana y prefiero respuestas cortas» es útil a medias. «Soy una persona reflexiva que valora el trabajo bien hecho» es ruido.

**Las memorias de feedback** recogen correcciones y confirmaciones. Cuando le dices a un agente «no hagas eso», eso es una memoria de feedback. Cuando le dices «sí, exacto, sigue así», también lo es (la gente se olvida de apuntar estas, pero importan igual: si solo guardas correcciones, los agentes se volverán demasiado prudentes). La regla: primero la regla, luego el motivo. Una corrección sin motivo se aplicará mal.

**Las memorias de proyecto** siguen el estado del trabajo en marcha: qué está en curso, qué se ha decidido, qué está bloqueado. Caducan deprisa: una memoria de proyecto de hace tres meses puede estar obsoleta. Incluye siempre la fecha y una nota sobre cuándo deja de ser relevante.

**Las memorias de referencia** apuntan a recursos externos: dónde se registran los bugs, qué calendario manda, dónde está la normativa de un proceso concreto. Son punteros, no contenido.

## Qué no guardar

Aquí es donde la gente se equivoca. La tentación es guardarlo todo: cada conversación, cada decisión, cada pedazo de contexto. No lo hagas.

No guardes lo que se puede deducir del código o del historial de git. Si la arquitectura se ve en los ficheros, no necesitas un fichero de memoria sobre ella. No guardes soluciones de depuración ni recetas de arreglos: el arreglo está en el código y el mensaje de commit tiene el contexto. No guardes detalles efímeros de tareas: lo que estás haciendo ahora mismo va en un gestor de tareas, no en la memoria.

La memoria es para lo que no resulta evidente a partir del estado actual del repositorio y que un agente nuevo que lo leyera necesitaría para servirte bien. Si un agente futuro lo puede averiguar leyendo los ficheros, no es una memoria.

## El índice MEMORY.md

`memory/MEMORY.md` es un índice, no un almacén de contenido. Se carga en el contexto de cada sesión. Mantenlo por debajo de las 200 líneas: no es un panel de control, es un fichero de punteros. Cada entrada es una línea: un enlace al fichero de memoria y una descripción de una línea lo bastante concreta para que un agente futuro pueda decidir si abre el fichero.

«Perfil de usuario» es una mala entrada de índice. «El usuario es ingeniero de caminos con diez años de experiencia en diseño de puentes y nuevo en la escritura académica» es una buena entrada: el agente puede decidir sin abrir el fichero si es relevante para la tarea que tiene entre manos.

## La regla de archivar, no borrar

Los ficheros de memoria antiguos que ya no son exactos no se borran. Van a `archive/`. Los motivos son prácticos: primero, una memoria descartada a veces vuelve a ser relevante. Segundo, la historia de lo que creías en distintos momentos es informativa por sí misma. Tercero, el archivo no cuesta nada: el agente no leerá los ficheros archivados a menos que se lo pidas.

Esta regla se extiende a todo el taller. No borres nada. Archiva.
