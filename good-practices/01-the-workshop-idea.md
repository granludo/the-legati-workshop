# 1. La idea del taller

Casi todo el mundo usa la IA como usa Google: una pregunta, una respuesta, siguiente pregunta. La sesión termina y todo se reinicia. La IA no ha aprendido nada sobre ti, y tú no has aprendido nada sobre la IA. Es una máquina expendedora: útil, pero no un colaborador.

Un taller es justo lo contrario. La sesión termina y algo persiste: la memoria de en qué estás trabajando, la memoria de cómo piensas y escribes, la memoria de las decisiones que has tomado y por qué. La siguiente sesión empieza con un contexto que ha costado tiempo de verdad construir. Con los meses, la diferencia se acumula.

Lo que noto (y es lo que intento explicar a los colegas que me preguntan por ello) no es que sea más productivo. No lo soy. Saco más o menos el mismo número de artículos. Lo que cambia es la profundidad del trabajo. Problemas que se quedaban años en un cajón porque nunca conseguía hincarles el diente se vuelven abordables. La IA no los resuelve. Pero sostiene el contexto mientras pienso, hace mejores preguntas de las que me haría yo y me obliga a articular posiciones que llevaba encima de forma vaga. Eso no es productividad. Es palanca intelectual.

## Qué hace el repositorio

El repositorio del taller es la capa duradera. Sobrevive a cualquier conversación, a cualquier versión del modelo, a cualquier actualización de las herramientas. La IA que lo lee hoy puede ser un modelo distinto del que lo lea el año que viene, pero el repositorio recuerda lo que aprendieron las dos sesiones. Esta es la idea estructural: **no estás construyendo un chatbot. Estás construyendo un colaborador de largo recorrido que acumula contexto.**

El repositorio contiene:
- El sistema de memoria: lo que los agentes saben de ti, de tu trabajo y de tus preferencias
- Las definiciones de las skills: qué operaciones pueden hacer los agentes
- Las herramientas: scripts que funcionan de verdad para generar PDF, transcribir, procesar fuentes y verificar bibliografía
- Las identidades de los agentes: los personajes que has dado a cada rol especializado

Nada de esto está en los pesos de la IA. Está todo aquí, en texto plano, bajo control de versiones. Cuando la IA lo lee al empezar la sesión, se convierte en el agente que has diseñado, no en un asistente genérico.

## La diferencia que marca

El perfil de escritura es el ejemplo más concreto. Después de un año con este taller, tengo un documento que describe cómo escribo: mi ritmo, las expresiones que evito, cómo estructuro los argumentos, las metáforas a las que recurro, los cambios de registro entre los artículos académicos y los ensayos para el público general. Cuando empiezo una sesión con «carga el perfil de escritura», el resultado deja de sonar a IA y empieza a sonar a mí. No del todo: la calibración no se acaba nunca. Pero ahora el primer borrador es aprovechable, y no una obra de demolición.

Ese documento no existía cuando empecé. Lo construí fijándome en cuándo fallaban los borradores, articulando por qué y escribiendo la regla. Lo mismo con el documento de visión del mundo: las posiciones intelectuales acumuladas que impiden que los agentes escriban cosas que yo nunca diría. Lo mismo con los ficheros de memoria que registran lo que pasó en sesiones anteriores. El sistema mejora porque inviertes en él.

## La inversión mínima viable

No hace falta que nada de esto sea perfecto el primer día. El andamiaje viene con plantillas y esbozos. Lo que tienes que hacer el primer mes:

1. Escribe un primer borrador de tu perfil de escritura. Saldrá escueto. No pasa nada: crece.
2. Ponles nombre a tus agentes y dales al menos una misión de una frase. Para empezar, basta.
3. Haz unas cuantas sesiones y fíjate en lo que sale mal. Escribe esas correcciones en `memory/` como ficheros de feedback.

El sistema se vuelve útil antes de lo que crees. La primera vez que un agente aplica una corrección de hace tres semanas sin que tengas que repetírsela, entiendes por qué vale la pena montarlo.

## Lo que no hace

Un taller no te hace más rápido. No automatiza tu pensamiento. Los agentes no toman decisiones: las tomas tú. Sostienen el contexto, generan borradores, verifican referencias, hacen aflorar patrones. El criterio siempre es tuyo.

Esto es una virtud, no una limitación. El objetivo es el trabajo profundo, no el trabajo delegado. Un agente que tomara decisiones por ti estaría sustituyendo tu producción intelectual por la suya. Lo que quieres es un agente que prepare el terreno para que tu producción intelectual pueda ir más hondo.
