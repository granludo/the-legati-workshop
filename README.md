# The Legati Workshop

Una bastida per construir el teu propi espai de treball intel·lectual potenciat amb IA.

**Què és:** un punt de partida amb opinions pròpies per dur a terme feina intel·lectual de llarg recorregut (escriptura, recerca, direcció de treballs, docència, pensament) amb Claude Code o amb el Codex CLI d'OpenAI com a col·laborador. Inclou eines que funcionen, un sistema de memòria, un marc de skills i un conjunt de personatges d'IA amb nom. Tu poses nom als personatges, els dones missions i hi aportes la teva veu i la teva visió del món.

**Què no és:** una plantilla en blanc. La infraestructura que hi ha aquí funciona des del primer dia. La teva feina és personalitzar-la, no construir-la des de zero.

**Comença aquí:** llegeix `skills/start-here.md` i després invoca la skill: digues a Claude Code o a Codex `"start here"` o `"/start-here"`.

**Llegeix la guia:** `good-practices/` és una guia escrita per algú que fa més d'un any que porta un taller com aquest. Explica què funciona, què no i per què.

---

## Inici ràpid

1. Clona el repositori: `git clone https://github.com/granludo/the-legati-workshop.git` i `cd the-legati-workshop`.
2. Comença una sessió com a orquestrador (`orchestrator`):
   - **Claude Code:** `./claude_orchestrator.sh`. Claude Code et demana que confiïs en la carpeta la primera vegada.
   - **Codex:** una vegada per màquina, `codex login` i després `bash tools/legati/install-hooks.sh codex`. A partir d'aleshores, `./codex_orchestrator.sh`. La primera vegada, aprova els hooks dins de Codex amb `/hooks`.
3. Digues `start here`. La skill d'acollida posa nom als teus legati i escriu amb tu el teu primer perfil.
4. Dona al taller una casa pròpia: crea un repositori **privat** i fes que `origin` hi apunti (`git remote set-url origin <your-url>`). El teu taller contindrà esborranys, notes i memòries, així que no hauria de viure mai en un repositori públic. Mentre no ho facis, funciona en local i `tools/git/sync.sh` conserva els commits a la teva màquina. La skill d'acollida t'hi acompanya (pas 6).

---

## Llengües

La branca `main` és en anglès. La branca `castellano` té tots els fitxers markdown en castellà (d'Espanya), i la branca `català` els té en català: `git switch castellano` o `git switch català`, o bé clona directament una d'aquestes branques: `git clone -b castellano https://github.com/granludo/the-legati-workshop.git`. El codi, les ordres i els noms de fitxer es mantenen en anglès a totes les branques, de manera que una ordre que llegeixis en una llengua funciona en totes tres.

---

## Sobre els legati

La paraula que es fa servir a tot aquest repositori és **legati** (singular: *legatus*). A la República romana, un *legatus* era un delegat: algú que portava l'autoritat i els valors d'un principal a un àmbit concret, amb un mandat clar i uns límits clars. Et representaven; no et substituïen.

Aquest és el marc que fa servir aquest taller per als personatges d'IA. No agents: delegats. La distinció importa.

La paraula «agent» ha colonitzat el discurs sobre la IA per designar una cosa que actua de manera autònoma, persegueix objectius i fa servir eines per iniciativa pròpia. Aquest marc situa l'humà, sense que es noti, en el paper d'espectador: fixes un objectiu i després mires. El marc dels legati ho capgira: **el principal ets tu**. Cada legatus té un mandat que ve de tu, un domini, un antimandat (el que no ha de fer) i l'obligació permanent de retornar-te les decisions quan cal criteri. El repositori és el registre durador de tot això, no el model, ni la conversa, ni el servei al núvol.

Trobo que «legati» és més honest amb el que passa de debò. El model no té objectius. Té un context, un fitxer de personatge i les teves instruccions. Dir-li delegat fa que això no es perdi de vista.

Dit això: «agent» és pertot arreu, tothom el fa servir, i aquesta batalla l'he perduda. Aquest repositori fa servir «legati» perquè és el que són. Trobaràs «agent» a la documentació de les eines, al vocabulari del mateix Claude, a tots els tutorials d'internet. Hi sortiran les dues paraules. El que importa és el concepte.

---

## La idea en un paràgraf

Un taller d'escriptura i de recerca és una col·laboració de llarga durada entre tu i un conjunt de personatges d'IA. Els personatges tenen memòria persistent, rols especialitzats i eines que funcionen. Tu ets el principal: la font dels valors, del gust i del criteri. Els legati fan la feina mecànica i de síntesi, recorden el que els has dit i et retornen les decisions que demanen el teu criteri. El repositori és la capa duradora: sobreviu a qualsevol conversa, a qualsevol versió del model, a qualsevol actualització d'eines. Tot el que importa viu aquí.

---

## Qui ho ha fet

Aquesta bastida s'ha destil·lat d'un taller real de Marc Alier (Ludo) (https://wasabi.essi.upc.edu/ludo), professor de la UPC a Barcelona, que el fa servir per treballar en llibres, articles acadèmics, materials docents, direcció d'estudiants i feina institucional. La guia de bones pràctiques està escrita amb la seva veu. Les eines i les convencions són seves. Les opinions són seves. Els agents són en blanc, perquè els teus agents han de ser teus.

Es recomana fer servir Obsidian per navegar pels documents en què treballeu tu i els teus agents.

---

## Llicència

Copyright (c) 2026 Marc Alier Forment (Ludo)

Amb llicència **Creative Commons Reconeixement-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA 4.0)**.

Pots compartir i adaptar aquest material lliurement sempre que reconeguis l'autoria de Marc Alier, no el facis servir amb finalitats comercials i distribueixis qualsevol obra derivada amb la mateixa llicència.

Llicència completa: consulta `LICENSE` o bé https://creativecommons.org/licenses/by-nc-sa/4.0/
