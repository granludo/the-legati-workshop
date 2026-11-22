---
name: index-maintenance
description: Cualquier cambio en el sistema de ficheros o en el estado de un proyecto actualiza el INDEX.md y el BACKLOG.md correspondientes en el mismo commit. Memoria de partida del taller original; consérvala, edítala o bórrala.
metadata:
  type: feedback
---

Cuando se añaden, mueven, renombran o archivan ficheros o carpetas, actualiza los mapas mantenidos **en el mismo commit**: `INDEX.md` (estructura del repositorio y proyectos), `sources/INDEX.md` (material de fuentes), el `BACKLOG.md` del proyecto (en qué se ha trabajado de verdad, qué se ha hecho o aplazado) y `memory/MEMORY.md` cuando se añade una memoria.

**Por qué:** varias sesiones trabajan en el repositorio, a menudo en paralelo y desde harness distintos. Quien vuelve después de una pausa, humano o legatus, se orienta con estos ficheros. Cuando se desvían del sistema de ficheros, todos los resúmenes construidos sobre ellos están mal, y nadie se da cuenta hasta que una sesión actúa sobre un mapa desfasado.

**Cómo aplicarla:**
- Trata la actualización del índice y del backlog como parte de «hecho», nunca como un commit posterior.
- Lee el fichero antes de añadir una entrada, para que el formato siga siendo coherente.
- Los elementos terminados del backlog pasan a una sección de hechos con la fecha; no se borran (son la historia del proyecto).
- Para añadir una fuente: usa `/add-source`, que actualiza el índice como parte del proceso.
- Nunca te lo saltes con un mensaje de commit del tipo «ya lo arreglaré».
