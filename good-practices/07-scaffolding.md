# 7. La bastida

El repositori del taller és una bastida per a una col·laboració de llarga durada. Entendre què vol dir això en termes d'estructura val els deu minuts que trigaràs a llegir aquest capítol.

## AGENTS.md és el contracte

`AGENTS.md` és el primer que llegeix qualsevol agent en començar la sessió, sigui quin sigui el harness: Codex el llegeix de manera nativa, i Claude Code el carrega a través de la importació d'una línia, `@AGENTS.md`, que hi ha a dalt de tot de `CLAUDE.md`. No és documentació: són instruccions d'operació. Defineix, o indica on trobar:
- Qui són els agents i quins són els seus carrils
- Quines skills hi ha i com s'invoquen
- Quins nivells de còmput hi ha i quan s'han de fer servir
- Quines són les regles innegociables

Quan canvies un comportament (afegeixes un agent, retires una skill, canvies una regla d'encaminament), el canvi va a `AGENTS.md`. No a un fitxer de memòria, ni a un comentari dins d'un script. Al contracte. Si el canvi només afecta un harness, va a l'apèndix d'aquell harness (el de Claude Code és a `CLAUDE.md`; el de Codex, al final d'`AGENTS.md`).

## La disciplina de la portabilitat

La bastida del taller no hauria de dependre de cap eina, plataforma o proveïdor d'IA concret. Les skills són fitxers markdown plans. La memòria és markdown pla. Les eines són scripts de Python normals i corrents. Les identitats dels agents són markdown pla. Res d'això no necessita Claude Code en concret, ni cap versió concreta de Claude, ni cap connector concret.

No és casualitat. El repositori és la capa duradora justament perquè no depèn de cap proveïdor. Quan Claude Code afegeix un sistema de hooks nou, o canvia el format de les ordres, o el substitueix una eina millor, el taller sobreviu. La capa duradora són les skills, les memòries i les identitats d'aquest repositori. La IA és el motor que va rotant per sota.

La conseqüència pràctica: quan construeixis una skill o una eina nova, no la lliguis a un mecanisme propi de Claude Code tret que no hi hagi alternativa. Invocar-la en llenguatge natural («executa la skill status») és més portable que una ordre de barra, que depèn que l'intèrpret l'analitzi bé.

## El manteniment d'INDEX.md: la regla que no és opcional

Qualsevol canvi al sistema de fitxers (cada fitxer afegit, reanomenat, mogut o esborrat) obliga a actualitzar `INDEX.md` en el mateix commit. Sense excepcions.

Sembla una feina extra innecessària. És just el contrari. L'INDEX és el que permet que qualsevol sessió (qualsevol agent, qualsevol model, qualsevol eina futura) s'orienti al repositori sense llegir tots els fitxers. Quan l'INDEX està desfasat, el repositori es torna opac. Els repositoris opacs acumulen codi mort, esborranys superats i referències òrfenes que ningú no vol netejar perquè ningú no sap què es pot treure sense perill.

La disciplina és aquesta: «fet» vol dir que l'INDEX està actualitzat.

## La regla d'arxivar, no esborrar

No esborris mai res del taller. Esborranys vells, notes superades, scripts orfes, experiments fallits: tot va a `archive/`, amb una nota breu sobre què eren i per què es van deixar de banda. L'arxiu és una reserva per explotar en el futur, no una paperera que hagis de buidar.

El motiu és en part pràctic (voldràs recuperar aquell esborrany més sovint del que et penses) i en part intel·lectual. La història del que vas provar i vas abandonar forma part del registre intel·lectual d'un projecte. D'aquí a un any potser no recordaràs per què vas descartar un enfocament. L'entrada de l'arxiu t'ho diu.

## Diverses sessions, un mateix repositori

Quan estàs ficat de ple en un projecte, és normal tenir diverses sessions obertes alhora, amb Claude Code, amb Codex o amb tots dos: una per escriure, una per a l'enginyeria, una per a les eines de fons. No passa res, però cal coordinació. El mecanisme de coordinació és el `BACKLOG.md` de cada projecte. Abans que una sessió comenci a treballar en la carpeta d'un projecte, mira al BACKLOG què hi ha en marxa. Abans de fer commit, actualitza el BACKLOG.

El corol·lari: no facis anar alhora dues sessions que regenerin el mateix tauler o el mateix fitxer compartit. En un repositori de text pla, les condicions de carrera tenen la forma d'errors «File has been modified since read» i de commits a mitges. La convenció del BACKLOG n'evita la majoria. El capítol 8 tracta la resta: els carrils, els traspassos i la disciplina de commits que permet que diversos legati treballin entre màquines i harness.

## Quan cal afegir una skill

Afegeix una skill quan et trobis explicant a un agent la mateixa operació de diversos passos més de dues vegades. Si a cada sessió d'escriptura acabes escrivint «llegeix el perfil d'escriptura, comprova el domini, fes servir la cadena de tres documents, fes una escombrada de tics de prosa abans de lliurar», això és una skill. Escriu-la un cop; invoca-la per sempre.

El fitxer d'una skill no és un procediment. És una posada en antecedents: què és l'operació, per què importa i què ha de comprovar l'agent abans, durant i després. Un bon fitxer de skill és curt: menys de 200 línies. Si és més llarg, estàs documentant casos límit que haurien d'anar a `memory/` o al `rules.md` de l'agent.
