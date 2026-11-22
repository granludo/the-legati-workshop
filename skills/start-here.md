# /start-here: guia de posada en marxa del taller

**Qui l'executa:** el legatus orquestrador (`orchestrator`), amb Claude Code o Codex (llança'l amb `./claude_orchestrator.sh` o `./codex_orchestrator.sh`).

**Quan s'invoca:** un cop, al principi, quan el repositori és nou i encara no has personalitzat res. També es pot tornar a invocar per a qualsevol pas de configuració que t'hagis saltat.

**Què fa:** guia l'usuari per la configuració mínima per tenir un taller personalitzat i que funcioni. Els passos estan ordenats pel que aporten: el que importa més va primer.

---

## Abans de començar

Digues això a l'usuari:

> Et dono la benvinguda. Aquesta bastida està muntada, però no personalitzada. Posaràs nom als teus agents, escriuràs un primer esborrany del teu perfil d'escriptura i configuraràs les eines. Res d'això no ha de ser perfecte el primer dia: el sistema millora a mesura que el fas servir.
>
> La configuració té set passos. Els tres primers duren més o menys una hora en total i et donen la major part del valor. La resta pot anar venint durant la setmana següent. Digues-me si vols saltar-te algun pas o tornar-hi més endavant.

---

## Pas 1: Posa nom als teus agents (15 minuts)

**Què cal fer:**

Fes a l'usuari les preguntes següents, d'una en una:

1. «Com vols que es digui el teu agent orquestrador per defecte, el que s'encarrega de l'enginyeria i la coordinació? És l'agent amb qui parlaràs en la majoria de sessions. Tria un nom de la ficció, de la història o d'on vulguis. Pot ser seriós o juganer: el que importa és que et vingui de gust dir-lo.»

2. «Com vols que es digui el teu agent d'escriptura? És el que redacta, edita i escriu amb la teva veu. La mateixa regla: un nom que et digui alguna cosa.»

3. «Vols un agent de comunicacions, que et llegeixi el calendari i la safata d'entrada? Si és que sí, com vols que es digui?» *(Si diu que sí, avisa que caldrà configurar l'OAuth de Google Workspace: se n'ocupa el pas 6.)*

4. «Vols un revisor, un agent que et doni opinions breus i honestes sobre esborranys i lliuraments? Com vols que es digui?»

**Quan tinguis els noms** (fes servir noms de carpeta en minúscules, d'una sola paraula, p. ex. `ada`): fes el que segueix per a cada legatus; per als rols que l'usuari no vulgui, mira la nota de més avall.

- Reanomena la carpeta amb `git mv characters/orchestrator characters/<name>` (i el mateix per a `writer/`, `comms/`, `reviewer/`) perquè l'historial la segueixi.
- A `characters/<name>/boot.md`: el títol, «Ets …» i el prefix de resposta (`[ADA]`). Treu el callout `[!todo]` que parla de reanomenar.
- A `characters/<name>/character.md`: el títol.
- A `AGENTS.md` §1: les línies de la plantilla de legati i la pregunta «Quin legatus?» (`ada · …`), i el nom del legatus per defecte.
- A `legati/roster.toml`: reanomena cada `[section]`.
- Totes les mencions del nom de rol antic a les línies de traspàs dels altres fitxers d'arrencada, a `characters/README.md` (taula i mapa de traspassos), a `skills/README.md` (la columna «Qui l'executa») i a `INDEX.md` (la taula d'agents).
- Regenera els llançadors de l'arrel: `bash tools/legati/make-launchers.sh` (escriu `claude_<name>.sh` i `codex_<name>.sh` i arxiva els antics, els que porten nom de rol).
- Comprova: `LEGATUS_DRY_RUN=1 ./claude_<name>.sh` imprimeix l'ordre que executaria; `grep -rn "orchestrator\|writer\|comms\|reviewer" AGENTS.md characters legati skills/README.md` troba el que queda.
- Fes el commit a través de la sincronització: `bash tools/git/sync.sh commit -m "workshop init: name legati <name1>, <name2>, <name3>, <name4>" -- AGENTS.md INDEX.md characters legati skills/README.md archive claude_*.sh codex_*.sh` (si el repositori encara no té remot, afegeix `--no-push`).

Un rol que l'usuari no vol (sovint, comunicacions): mou-ne la carpeta a `archive/characters/` amb `git mv`, treu-ne la línia de la plantilla de legati i la secció de `roster.toml`, i executa `make-launchers.sh`.

Informa l'usuari: «Els teus legati ja tenen nom. Obre'n un amb `./claude_<name>.sh` o `./codex_<name>.sh`, o adreça-t'hi pel nom en qualsevol sessió.»

---

## Pas 2: Escriu el teu perfil d'autor (30 minuts)

És el més important que pots fer per a la qualitat del que produeix el taller. Si te'l saltes, tot el que escriguin els agents serà genèric. Si el fas, el resultat comença a sonar com tu.

**Què cal fer:**

Digues a l'usuari: «Ara escriurem un primer esborrany del teu perfil d'escriptura. Et faré unes quantes preguntes. Respon amb sinceritat: aquest document és per als agents, no per publicar-lo.»

Fes aquestes preguntes. Pren notes mentre l'usuari respon. Faràs servir les respostes per redactar el perfil.

1. «Com descriuries el registre de la teva escriptura? Acadèmic? Assagístic? Conversacional? Tècnic? Diferent segons el context?»
2. «Quin text teu t'agrada de debò, un en què sonaves com tu de veritat? Què el feia funcionar?»
3. «Quins tics o patrons d'escriptura saps que fas servir massa i intentes treure quan edites?»
4. «Hi ha paraules o expressions concretes que no suportes en els textos dels altres, coses que et fan aturar i arrufar el nas?»
5. «Escrius en diverses llengües? Si és així, hi ha diferències de veu que vulguis preservar?»
6. «Com estructures normalment un argument? Primer el context històric i després la tesi? O primer la tesi i després les proves? O d'una altra manera?»
7. «Com fas servir l'humor quan escrius, si és que el fas servir? Quin és l'antipatró, l'humor que a tu no et funciona?»

Redacta `principals/[your-name]/writing-profile.md` a partir de les respostes de l'usuari. Fes servir l'estructura de plantilla que ja hi ha al fitxer. Ensenya-li un esborrany i deixa que el corregeixi.

Digues-li: «Això és un primer esborrany. Cada vegada que una sessió produeixi alguna cosa que no encerti la teva veu i sàpigues explicar per què, afegeix una nota a aquest fitxer. Millora amb el temps.»

Reanomena `principals/your-name/` a `principals/[their-name]/` amb `git mv`. Actualitza les referències a `AGENTS.md` §9 i a `skills/write-as-user.md` (reanomena'l a `write-as-[their-name].md` i actualitza'n la fila a `skills/README.md` i al `boot.md` de l'escriptor).

Commit: `"init: first draft writing profile for [name]"`

---

## Pas 3: Prepara el document de visió del món (20 minuts)

Aquest és el document que ensenya als agents què penses. Sense ell, els agents escriuen coses que contradiuen les teves posicions.

**Què cal fer:**

Digues a l'usuari: «El document de visió del món és on escrius les teves posicions intel·lectuals, les coses que creus i que haurien d'informar tot el que escriguin els teus agents. No cal que l'omplis sencer ara. Amb tres o cinc posicions n'hi ha prou per començar.»

Pregunta:
1. «Quina posició defenses amb força que la majoria de la gent del teu camp no comparteix, o almenys no diu en veu alta?»
2. «Contra què et trobes argumentant més sovint, en el teu àmbit?»
3. «A quin marc o a quina metàfora tornes una vegada i una altra quan penses?»

Redacta de 3 a 5 entrades de visió del món a `principals/[their-name]/worldview.md`. Numera-les §1, §2, etc. Ensenya'n els esborranys i deixa que els corregeixi.

Digues-li: «Afegeix-hi coses cada vegada que una sessió produeixi alguna cosa que tu no diries mai. Aquell moment de “jo no ho diria mai així” és material nou per a la visió del món.»

Commit: `"init: first worldview entries for [name]"`

---

## Pas 4: Configura el teu primer projecte (10 minuts)

**Què cal fer:**

Pregunta: «Quin és el primer projecte d'escriptura que vols fer passar pel taller? Posa-li un nom curt.»

Crea `writting-projects/[project-slug]/BACKLOG.md` amb l'estructura estàndard (un directori amb un `BACKLOG.md` és el que l'eina de carrils anomena projecte: `python3 tools/legati/lane.py claim writting-projects/[project-slug] "<task>"`):

```markdown
# [Project name] — backlog

## Active
*(in progress now)*

## Up next
*(ready to start, ordered by priority)*

## Soon
*(committed but not started)*

## Done
*(completed items — most recent first)*

## Postponed
*(not now, not never)*
```

Afegeix el projecte a `INDEX.md`.

Crea `memory/project-[slug].md` a partir de la plantilla de projecte de `memory/_templates/`.

Commit: `"init: first project [project-slug]"`

---

## Pas 5: Fes la comprovació d'estat

Invoca `/status` per verificar que el repositori està en bon estat i que el procediment d'orientació funciona.

La comprovació d'estat hauria de:
- Llegir `INDEX.md` i informar dels projectes actius
- Llegir `memory/MEMORY.md` i confirmar que el perfil hi és
- Llistar les skills disponibles
- Informar de qualsevol element `> [!todo]` obert en els fitxers clau que encara necessiti l'atenció de l'usuari

Si hi ha marques `[!todo]` pendents a `AGENTS.md`, als fitxers d'arrencada o al perfil d'escriptura, fes-les aflorar ara.

---

## Pas 6: Configura aquesta màquina (20-60 minuts segons el que ja tinguis)

Fes el que calgui. Deixa constància del resultat com a secció d'aquesta màquina a `memory/reference_hosts.md` (l'exemple de la plantilla en mostra la forma; `hostname -s` et dona el títol). Tots els legati llegeixen aquesta secció en arrencar, així que mantén-la curta i certa.

**Remot de Git (molt recomanable):**
- Pregunta: «Aquest taller és en un remot de Git privat (GitHub, GitLab, un servidor teu)? És el que permet que diverses sessions i diverses màquines comparteixin un mateix taller.»
- Si encara no ho és: crea un repositori **privat** i després `git remote set-url origin <url>` (o `git remote add origin <url>`) i `bash tools/git/sync.sh push`. No facis mai push d'un taller personal a un repositori públic: hi haurà esborranys, notes i memòries.

**Claude Code:**
- Res a instal·lar al repositori: el `.claude/settings.json` versionat ja porta els hooks. Claude Code demana un cop que confiïs en la carpeta.
- Prova: `./claude_<name>.sh` obre una pestanya amb el nom d'aquell legatus, i les primeres línies de la sessió mostren el resum `[legati]`.

**Codex (opcional, recomanat per tenir una segona família de models):**
- `codex login` (flux al navegador), després `bash tools/legati/install-hooks.sh codex`.
- Engega Codex un cop al repositori i aprova els hooks amb `/hooks`.
- Prova: `./codex_<name>.sh`; la sessió hauria de respondre amb el prefix d'aquell legatus. Dins del sandbox de Codex, el hook d'arrencada dona un resum local i demana executar `bash tools/legati/session-start.sh --refresh` mitjançant una aprovació: és el que s'espera.
- Opcional: fixa un legatus a Codex a `legati/roster.toml` (un revisor amb una família de models diferent de la de l'escriptor dona una segona opinió independent).

**La porta d'entrada `llm` (altres models):**
- Mira `tools/llm/README.md`: `uv tool install llm`, després els connectors que necessitis (`llm install llm-ollama` per a un servidor Ollama local), `llm keys set openai` per a una clau de pagament.
- Prova: `llm models` llista el que pot cridar aquesta màquina; `llm -m <model> 'say hi'` respon; `llm logs -n 1` mostra que ha quedat registrat.

**Generació de PDF:**
- Prova: `pandoc --version && typst --version`
- Si en falta algun: `brew install pandoc typst` (macOS) o consulta la documentació del teu sistema operatiu.
- Prova tot el circuit: escriu un fitxer markdown curt i passa-hi `/md2pdf`.

**Verificació de referències (si escrius textos acadèmics):** `bash tools/refs-check/setup.sh`, i posa la teva adreça electrònica a `REFS_CHECK_CONTACT` (mira `tools/refs-check/README.md`).

**Google Workspace (per al legatus de comunicacions, si està activat):**
- Mira `tools/google/README.md` per al procediment de configuració d'OAuth.
- Cal: un compte de Google, crear una aplicació OAuth a Google Cloud Console i passar pel flux d'autenticació un cop. La primera vegada són 30 minuts.

---

## Pas 7: Afegeix la teva primera font

Tria alguna cosa que estiguis llegint o amb què estiguis treballant ara i passa-hi `/add-source`. Això confirma que el circuit d'entrada de fonts funciona i et dona un exemple concret de com és una font processada.

Bones primeres fonts: un article en PDF que hagis llegit fa poc, una xerrada de YouTube que vulguis citar, un article web que tinguis a les adreces d'interès.

---

## Després de la configuració

Digues a l'usuari:

> El taller ja està configurat. A partir d'aquí, evoluciona a mesura que el fas servir. Unes quantes coses a tenir presents:
>
> - Quan un agent faci alguna cosa que vols que deixi de fer, afegeix una memòria de feedback. Quan faci alguna cosa perfecta, apunta-ho també: totes dues direccions compten.
> - El perfil d'escriptura i la visió del món creixen millor amb l'ús que no pas omplint plantilles per avançat. Fes sessions. Fixa't en què falla. Afegeix la regla.
> - La guia de bones pràctiques de `good-practices/` val la pena llegir-la durant la setmana que ve. No tot serà rellevant encara: llegeix-la quan tinguis un dubte sobre com hauria de funcionar alguna cosa.
> - Quan afegeixis alguna cosa al sistema de fitxers, actualitza `INDEX.md` en el mateix commit. Aquesta és l'única regla que de debò no és opcional.
> - Fes els commits a través de `bash tools/git/sync.sh commit -m "…" -- <paths>`, perquè totes les sessions i totes les màquines vegin la feina a l'instant.
> - Fas anar diversos legati alhora, o des de dos harness o dues màquines? Llegeix primer `good-practices/08-many-legati-many-harnesses.md`.

Fes un últim commit, `"workshop setup complete"`, que reculli qualsevol element obert que quedi.

---

## Si l'usuari vol saltar-se passos

Cap problema. Els tres més importants són el pas 1 (noms), el pas 2 (perfil d'escriptura) i el pas 4 (primer projecte). La resta pot venir quan calgui. No imposis un ordre lineal.
