# Els legati: els teus agents d'IA

Aquesta carpeta conté els fitxers d'identitat dels agents d'IA del teu taller. Cada agent és un *legatus* (plural: *legati*): un delegat que actua amb la teva autoritat dins d'un carril definit.

La paraula importa. La indústria de la IA en diu «agents», cosa que implica acció autònoma. Però el que vols són *delegats*: entitats que actuen en nom teu, dins dels límits que tu fixes, amb un criteri que tu has calibrat. La distinció és epistemològica, no cosmètica.

---

## Els quatre agents inicials

Aquest taller sembra quatre rols d'agent. Encara no tenen nom, ni personalitat, ni personatge. Això és feina teva. Cada carpeta conté un `boot.md` curt (el que el legatus llegeix en començar la sessió), un `character.md` esquemàtic i un `rules.md` buit. Omple'ls.

| Carpeta | Rol | La teva feina |
|---|---|---|
| `orchestrator/` | Agent per defecte; eines, enginyeria, custòdia del repositori, coordinació | Posa-li nom. Dona-li una personalitat. És l'agent que porta la majoria de sessions. |
| `writer/` | Redacció, edició, imitació de la veu, textos en diverses llengües | Posa-li nom. Dona-li la teva veu d'escriptura com a referència. Aquest agent ha de saber com escrius. |
| `comms/` | Calendari, safata d'entrada, agenda: només lectura als serveis externs | Posa-li nom. Defineix amb cura el seu mandat de només lectura. Aquest agent no hauria d'enviar mai res que no hagis autoritzat. |
| `reviewer/` | Opinió honesta i calibrada sobre esborranys i lliuraments | Posa-li nom. Calibra'n la severitat. Aquest agent t'ha de dir la veritat, no el que vols sentir. |

---

## Com dissenyar un agent

Consulta `good-practices/02-the-legati.md` per a la guia completa. La versió curta:

1. **Posa-li un nom tret de la ficció o de la història que t'estimes.** El nom fixa el registre i et dona una nansa per invocar el personatge. Un nom triat a consciència no fa el mateix efecte que «Assistent 2».
2. **Defineix-ne el carril amb precisió.** Què fa? Què és el que explícitament *no* fa? L'antimandat és tan important com el mandat.
3. **Dona-li una àncora de veu.** Una frase o una cita que en capti el registre. «Concís, concret, sense afalacs» és una àncora de veu. «Servicial i amable» no ho és.
4. **Anomena l'antipatró.** Qui *no* és aquest agent? Posar nom al mode de fallada t'ajuda a calibrar-lo i ajuda l'agent a corregir-se tot sol.
5. **Les regles s'acumulen amb el temps.** El fitxer `rules.md` comença buit. S'omple a mesura que dones instruccions a l'agent al llarg de les sessions.

---

## Sobre els noms

No cal que posis als agents noms de ficció. Però els noms de la ficció que t'estimes solen quedar-se, perquè arriben carregats d'associacions que ja tens. Quan dius un nom en una sessió, invoques aquestes associacions: la veu, els valors i l'actitud del personatge. Aprofita-ho.

Els agents d'aquest taller van rebre noms d'*Expeditionary Force* (Craig Alanson), de *Heinlein*, de *Conan Doyle*, de *Philip K. Dick* i de *Harry Potter*. Cada nom portava alguna cosa que l'agent necessitava.

---

## Fitxers d'arrencada, la plantilla de legati i els llançadors

Una sessió és un legatus. Llegeix `AGENTS.md` (el nucli, compartit per tots els harness) i després **només** el seu `characters/<name>/boot.md`, que apunta al seu `character.md`, al seu `rules.md`, a les skills que executa i a les memòries que obre quan salta un disparador. Mantén curts els fitxers d'arrencada: tot el que un legatus no necessita el primer minut es queda darrere d'un enllaç.

La plantilla de legati té tres llocs que han de coincidir, i `/start-here` (pas 1) els actualitza tots quan poses nom a un legatus o el reanomenes:

1. les línies de la plantilla a `AGENTS.md` §1 (i la pregunta «quin legatus?» que hi ha);
2. la carpeta `characters/<name>/` i l'encapçalament i el prefix de resposta del seu `boot.md`;
3. la secció `[<name>]` de `legati/roster.toml`, que tria el harness per defecte (`claude-code` o `codex`) i el model.

Després regenera els llançadors de l'arrel amb `bash tools/legati/make-launchers.sh`: obtens `./claude_<name>.sh` i `./codex_<name>.sh` per a cada legatus que tingui fitxer d'arrencada. Un llançador defineix `LEGATUS_AGENT`, posa nom a la pestanya del terminal i passa el fitxer d'arrencada al harness. Dos legati poden compartir una pestanya: `legati/bin/legatus comms --with reviewer`.

## Mapa de traspassos (inicial)

- Orquestrador → Escriptor per a qualsevol prosa de més d'uns quants paràgrafs que hagi de semblar teva.
- Orquestrador → Comunicacions per a consultes d'agenda i de safata d'entrada.
- Qualsevol → Revisor abans que un lliurament surti del taller. El revisor proposa, tu decideixes, l'escriptor reescriu.
- Escriptor → Orquestrador per a problemes d'eines i de renderitzat.

Entre sessions, aquests traspassos són fitxers (`tools/legati/handoff.py`); dins d'una sessió són un canvi de personatge durant un bloc, anunciat a la resposta.
