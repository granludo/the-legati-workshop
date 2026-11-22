---
name: scaffolding-portability
description: Mantén la capa duradora (skills/, memory/, characters/, carpetes de projecte, manuals d'operació) neutral respecte del harness. La invocació en llenguatge natural és la canònica; els fitxers específics de cada harness viuen a .claude/ i .codex/, per màquina. Memòria inicial del taller original; conserva-la, edita-la o esborra-la.
metadata:
  type: feedback
---

El repositori és l'agent durador: el model hi va rotant per sota, i el harness també (avui Claude Code, Codex al costat, més endavant una altra cosa). La capa duradora ha de funcionar amb qualsevol d'ells sense haver-la de refer.

**Per què:** el taller original va començar amb un harness i més endavant en va afegir un segon. Va caldre trobar i reescriure cada lloc on una skill o una regla donava per fet el funcionament d'un harness concret. Els llocs que eren markdown pla i scripts senzills no van necessitar res.

**Com aplicar-ho:**
- **La invocació en llenguatge natural és la canònica** («Revisor, mira't el capítol 3»). Una ordre de barra és una comoditat per teclejar que depèn de l'analitzador d'un harness concret.
- **Les skills són markdown pla** a `skills/`: sense frontmatter ni marcadors específics d'un harness al cos. Un fitxer a `.claude/commands/` només pot existir com a punter d'una línia cap a la skill.
- **Els fitxers específics d'un harness es queden fora de la capa duradora:** la connexió dels hooks, les configuracions MCP i els paràmetres del harness viuen a `.claude/` i `.codex/`. El que és de cada màquina està ignorat per git (`.codex/`, `.claude/settings.local.json`).
- **Les regles viuen a `AGENTS.md`**, que llegeixen tots els harness; cada harness té un apèndix curt amb només el que li és específic.
- **Les eines són CLI o scripts** que qualsevol harness pot cridar des d'una shell, mai un protocol que només parla un harness.
