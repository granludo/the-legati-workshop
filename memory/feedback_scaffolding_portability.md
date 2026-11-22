---
name: scaffolding-portability
description: Mantén la capa duradera (skills/, memory/, characters/, carpetas de proyecto, manuales de procedimiento) independiente del harness. La invocación en lenguaje natural es la canónica; los ficheros específicos de cada harness viven en .claude/ y .codex/, por máquina. Memoria de partida del taller original; consérvala, edítala o bórrala.
metadata:
  type: feedback
---

El repositorio es el agente duradero: el modelo va rotando por debajo, y el harness también (hoy Claude Code, Codex a su lado, más adelante otra cosa). La capa duradera debe funcionar con cualquiera de ellos sin rehacer nada.

**Por qué:** el taller original empezó con un harness y más tarde añadió un segundo. Hubo que encontrar y reescribir cada sitio donde una skill o una regla daba por supuesta la mecánica de un harness concreto. Los sitios que eran markdown y scripts sin más no necesitaron nada.

**Cómo aplicarla:**
- **La invocación en lenguaje natural es la canónica** («Revisor, mira el capítulo 3»). Un comando de barra es una comodidad al teclear que depende del analizador de un harness concreto.
- **Las skills son markdown sin más** en `skills/`: nada de frontmatter ni de marcadores específicos de un harness en el cuerpo. Un fichero en `.claude/commands/` solo puede existir como puntero de una línea a la skill.
- **Los ficheros específicos de un harness quedan fuera de la capa duradera:** la conexión de los hooks, las configuraciones MCP y los ajustes del harness viven en `.claude/` y `.codex/`. Lo que es de cada máquina va en el gitignore (`.codex/`, `.claude/settings.local.json`).
- **Las reglas viven en `AGENTS.md`**, que lee todo harness; cada harness tiene un apéndice corto con solo lo que le es específico.
- **Las herramientas son CLI o scripts** que cualquier harness puede llamar desde una shell, nunca un protocolo que solo habla un harness.
