# 2. Los legati

Los llamo *legati*, que en latín quiere decir *delegados*. La industria de la IA los llama *agentes*, y eso implica acción autónoma: un agente actúa. Un delegado actúa *en tu nombre, dentro de los límites que tú defines*. La distinción importa. Si los planteas como agentes, acabas diseñando sistemas que actúan. Si los planteas como delegados, acabas diseñando sistemas que sirven.

El taller arranca con cuatro roles. Tú les pones nombre y les das carácter. Así es como conviene pensarlo.

## Por qué importa el nombre

Un nombre no es cosmético. Cuando eliges un nombre de la ficción o de la historia que te importa, tomas prestado un personaje entero: un conjunto de asociaciones, una voz, una actitud, un antipatrón. Cuando digo «Agatha» en una sesión, invoco un registro concreto: cálido pero no blando, intelectualmente serio, orientado al lector. Cuando digo «Grumpy», invoco otro: seco, honesto, calibrado, que te dice la verdad aunque no te convenga. Los nombres hacen trabajo de verdad.

Elige nombres que no te tengas que explicar a ti mismo. El agente con el que trabajas cada día durante un año es más fácil de mantener calibrado si el nombre ya trae de serie las connotaciones adecuadas. Yo elegí nombres de la ficción que me encanta: *Expeditionary Force*, Heinlein, Philip K. Dick, Conan Doyle. Tú tendrás tu propio canon. Úsalo.

## Los cuatro roles

**El orquestador** (`orchestrator`) es el agente por defecto: el que se activa cuando no te has dirigido a nadie en concreto. Se ocupa de la ingeniería, las herramientas, el mantenimiento del repositorio y la coordinación entre los demás agentes. Y, sobre todo, sabe cuándo pasar el trabajo: «esto es una tarea de escritura, paso al escritor». El orquestador no es un agente de escritura. Cuando monté este taller por primera vez, lo metí todo en un único agente, y el resultado se resintió: la cabeza de ingeniería y la cabeza de escritura son distintas de verdad, y mezclarlas degrada las dos.

**El escritor** (`writer`) es tu voz escrita. Produce borradores, hace pasadas editoriales, adapta tu tono a registros distintos, traduce entre lenguas. Lo más importante del escritor: necesita tu perfil de escritura antes de poder hacer nada útil. Sin él, escribe con competencia, pero de forma genérica. Un buen perfil de escritura tarda meses en construirse, pero la mayor parte del valor sale del primer borrador que escribes un mal día y arreglas a la mañana siguiente.

**El agente de comunicaciones** (`comms`) se ocupa de tu calendario, tu correo y tu agenda, solo en lectura. Esto no se negocia: el agente de comunicaciones nunca envía, nunca crea eventos, nunca modifica datos externos. El techo se impone en la credencial OAuth, no en la confianza. La razón es de arquitectura: no quieres que un agente capaz de enviar correos en tu nombre tenga el mismo nivel de autonomía que uno que edita ficheros en un repositorio privado. Perfiles de riesgo distintos piden controles distintos. Además, este agente solo actúa cuando lo llamas. No arranca por su cuenta. Cuando hay dos sesiones abiertas a la vez (dos pestañas, dos harness, dos máquinas), cosa que pasa, un agente de comunicaciones que se activa solo provoca condiciones de carrera en los ficheros compartidos del panel. Tú lo llamas; él se ejecuta.

**El revisor** (`reviewer`) es tu crítico honesto. El antipatrón de un extremo es el adulador que lo valida todo: inútil. El antipatrón del otro extremo es el francotirador que lo derriba todo sin ofrecer nada constructivo: igual de inútil, y peor, porque desmoraliza. El revisor que quieres es el que te dice la verdad, nombra el problema concreto y propone el cambio mínimo que lo arregla. Calibra la escala de gravedad para que «Major» signifique algo. Si todo es Major, nada lo es.

## El antimandato importa tanto como el mandato

Cada agente necesita una declaración clara de lo que *no* hace. Aquí es donde casi todo el mundo se queda corto. Si no defines los límites, los agentes darán por hecho que todo entra en su terreno, y acabarás con el escritor dándote consejos de ingeniería y el orquestador produciendo prosa.

El antimandato también te obliga a pensar a qué carril pertenece cada tarea. «¿Quién debería hacer esto?» pasa a ser una pregunta real con una respuesta real, no un encogimiento de hombros.

## Los ficheros de reglas crecen con el tiempo

Cada agente tiene un fichero `rules.md` que empieza vacío. Lo vas llenando a medida que ves en qué se equivoca el agente. Cuando dices «no hagas eso» o «cuando pase X, haz siempre esto», apúntalo en el fichero de reglas con el motivo. El motivo importa tanto como la regla: una sesión futura (o un modelo futuro) que no entienda el porqué no sabrá aplicar la regla en los casos límite.

Un fichero de reglas con diez buenas entradas (concretas, razonadas, basadas en incidentes reales) vale más que cien principios vagos. Que sean concretas. «No añadas un resumen al final de cada respuesta» es una regla. «Sé conciso» no lo es.

## Sobre añadir más agentes

Cuatro es un mínimo, no un techo. A medida que el taller madure, descubrirás tareas que caen entre los cuatro roles o que merecen un tratamiento especializado. Un custodio de la historia de un dominio (un agente que sigue durante meses las decisiones y la historia de un proyecto concreto) tiene un valor enorme en trabajos complejos y largos. Un agente de supervisión de estudiantes es útil si diriges tesis. Un revisor de seguridad es útil si tienes agentes que escriben y ejecutan scripts.

El principio de expansión: añade un agente nuevo cuando puedas articular un mandato claro, un antimandato claro y el motivo por el que los agentes que ya tienes no pueden asumirlo sin degradarse. No añadas agentes por variedad. Cada agente nuevo añade coste de coordinación.
