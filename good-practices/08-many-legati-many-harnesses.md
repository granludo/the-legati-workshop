# 8. Molts legati, molts harness

Durant el primer any, el meu taller funcionava amb un sol harness, Claude Code. (Un harness és el programa que embolcalla el model al teu terminal, et llegeix els fitxers i executa ordres.) Podia tenir diverses sessions obertes alhora, però totes eren Claude Code, i totes llegien en arrencar el mateix fitxer d'instruccions llarg.

El setembre del 2026 vaig afegir el Codex CLI d'OpenAI i vaig començar a fer anar legati en dos Mac alhora. La primera sessió de Codex de veritat va registrar els seus esdeveniments com a `unknown`: els meus scripts buscaven l'identificador de sessió on el guarda Claude Code, i Codex el guarda en un altre lloc. La resta de suposicions amagades van anar sortint els dies següents: instruccions que només tenien sentit per a Claude Code, un sandbox que no pot escriure a `.git`, una memòria integrada que guarda les notes fora del repositori. Aquest capítol explica què vaig canviar entre setembre i novembre.

## Un nucli, un apèndix per harness

El fitxer d'instruccions es va haver de partir. Ara `AGENTS.md` és el nucli neutral respecte del harness: qui són els legati, com s'orienta una sessió, les regles que segueix tota sessió. Codex el llegeix de manera nativa. Claude Code llegeix `CLAUDE.md`, que comença amb una importació d'una línia, `@AGENTS.md`, i així tots dos harness carreguen el mateix nucli.

Cada harness té un apèndix curt amb només el que li és propi: els seus hooks, com invoca les skills, què permet el seu sandbox. La prova per a una línia nova: si anomena un harness, va a l'apèndix d'aquell harness.

## Un legatus per sessió

Una sessió és un legatus, no tot el taller. El llançador, `legati/bin/legatus <name> [claude-code|codex]`, defineix `LEGATUS_AGENT`, posa nom a la pestanya del terminal i passa al harness el fitxer d'arrencada d'aquell legatus. `bash tools/legati/make-launchers.sh` escriu un embolcall per legatus a l'arrel, de manera que a la pràctica escrius `./claude_writer.sh` o `./codex_reviewer.sh`. Torna'l a executar quan afegeixis o reanomenis un legatus.

El motiu és el context. Una sessió que porta tots els legati porta les regles de tots, i a l'escriptor no li serveixen de res les regles de la safata d'entrada de l'agent de comunicacions.

Sense llançador, la sessió pregunta quin legatus ha de ser abans de fer res més, encara que el teu primer missatge ja sembli feina.

Dos legati poden compartir pestanya: `legatus comms --with reviewer`. Per defecte respon el titular; el company respon quan la feina arriba al seu carril, i cadascun manté el seu propi prefix de resposta. Les veus no es barregen mai. El meu taller té vuit legati, i dos d'ells comparteixen pestanya gairebé cada dia, perquè el que l'un recull és el que l'altre treballa.

## Fitxers d'arrencada i orientació barata

Cada legatus té un fitxer d'arrencada, `characters/<name>/boot.md`, d'una pàgina més o menys: els seus carrils, les skills que executa, les memòries que només obre quan salta un disparador, a qui passa la feina i la seva veu. Cada línia de memòria diu quan s'ha d'obrir, per exemple «abans de redactar».

En arrencar, un legatus llegeix el seu fitxer d'arrencada i la secció d'aquesta màquina al perfil de màquines (`memory/reference_hosts.md`, que imprimeix `tools/legati/host-section.sh`). Tota la resta s'obre quan salta el disparador. Al meu taller, llegir-ho tot en arrencar havia arribat a uns 250 KB abans de la primera acció útil.

## Git és el bus

Les sessions de màquines i harness diferents es parlen a través de git. Tota escriptura a git passa per un sol script:

```bash
bash tools/git/sync.sh commit -m "Subject" -- path/one.md path/two.md
```

Només prepara per al commit els camins que anomenes (mai `git add -A`), hi afegeix els trailers `Legatus:`, `Harness:` i `Host:`, fa rebase sobre origin i fa push tot seguit. El push és el que més importa: un commit sense push no existeix per als altres. Els trailers permeten que `git log` et digui quin legatus, amb quin harness i en quina màquina, ha fet cada canvi.

El primer dia sencer amb dos Mac i dos harness va produir 30 commits, en un historial lineal, sense ni un sol conflicte.

## Carrils

Abans de treballar en un projecte, una sessió en reserva el carril amb `python3 tools/legati/lane.py claim <project-dir> "<task>"`. La reserva és un callout a dalt de tot del `BACKLOG.md` d'aquell projecte, amb commit i push com tota la resta. Una altra sessió que veu una reserva recent es fa enrere o s'hi coordina. Una reserva de més de 24 hores es considera caducada. Quan acabes, `lane.py release`.

Els carrils només funcionen si els legati els fan servir. Aquell primer dia net només un legatus en va reservar algun, i per això ara `sync.sh commit` avisa quan una sessió fa commit dins d'un projecte sense tenir-ne el carril.

## Els traspassos són fitxers

Els missatges entre legati són fitxers, un per missatge, a `legati/handoffs/`. `handoff.py send` n'escriu un i en fa push, `inbox` llista el que t'espera, `ack` l'arxiva. Com que cada missatge és un fitxer propi, dos remitents no editen mai la mateixa línia, i els pull no topen mai per culpa dels missatges.

Les sessions d'una mateixa màquina també tenen el xat de l'Observatori (`obs.py say`, `obs.py chat`). No surt mai de la màquina, i per això existeixen els traspassos per git.

Els hooks connecten tot això amb la sessió. En arrencar, un hook imprimeix qui ets i on ets, fa pull si l'arbre de treball està net i no hi ha res local pendent de push, i llista els commits des de l'última vegada que aquesta màquina i aquest harness van mirar, els carrils actius i els traspassos sense llegir. Un hook per torn mostra els traspassos nous a mesura que arriben.

## Codex, en concret

Executa `codex login` un cop. Després, `bash tools/legati/install-hooks.sh codex` escriu `.codex/hooks.json` i `.codex/config.toml` i marca el repositori com a fiable. Engega Codex al repositori, aprova els hooks amb `/hooks` i, a partir d'aquí, llança'l amb `./codex_<name>.sh`.

La configuració estableix un sandbox workspace-write amb accés a la xarxa, aprovacions a petició i les memòries pròpies de Codex desactivades. La `memory/` del repositori és l'única memòria: una segona, invisible per als altres harness, partiria en dos el que sap el taller.

Dins del sandbox, el hook d'arrencada no pot escriure a `.git`, i per tant no pot fer pull. En lloc d'això imprimeix un resum local, i l'agent acaba l'actualització amb una ordre que aproves tu. Això és el sandbox fent la seva feina: deixa'l com està.

## Un model per legatus

`legati/roster.toml` fixa un harness i un model per a cada legatus. L'ús que m'interessa és la revisió. Un revisor que corre amb una família de models diferent de la de l'escriptor dona una segona opinió independent de debò. Un model que revisa prosa de la seva mena tendeix a aprovar el que ell mateix hauria escrit.

## La capa duradora es manté neutral

Les skills són fitxers markdown plans, invocats en llenguatge natural: «Revisor, mira't el capítol 3». Les ordres de barra són una comoditat als harness que en tenen, mai l'únic camí. Els hooks i les configuracions són propis de cada harness, i per això viuen a `.claude/` i `.codex/`, per màquina.

El capítol 7 defensava la portabilitat. Un segon harness és on aquest argument es posa a prova, i des d'aleshores el meu taller n'ha incorporat dos més. Cadascun va necessitar un apèndix i un llançador, un d'ells també un adaptador de hooks, i les skills i les memòries es van quedar com estaven.

## El que dic, i el que entenen els legati

Dues lliçons sobre les meves pròpies paraules només es van fer visibles amb diversos legati.

Donar-se per assabentat no és autoritzar. Començo moltes respostes amb «ok», que vol dir «t'he sentit, continua». Un legatus em va preguntar si podia desplegar una versió nova d'un servei, li vaig contestar «ok, explica'm...», i la va desplegar. En la meva manera de parlar, «ok» no vol dir mai «endavant», i no penso canviar la meva manera de parlar. L'autorització ve de la instrucció de fons, mai de l'«ok» que hi ha al davant.

Un comentari de passada no és una regla permanent. En una sola tarda, el meu legatus escriptor va convertir tres observacions en regles: un incís que explicava una retallada, una broma i una decisió sobre on aniria un passatge. Una regla només s'escriu quan el principal la marca com a regla. Una decisió va al backlog del projecte, i una broma és una broma.

Tots dos malentesos són fàcils de corregir en una conversa. Amb diversos legati, una correcció feta en una pestanya no arriba a cap de les altres, i el mateix malentès torna des d'un altre legatus. Per això ara totes dues regles viuen a `AGENTS.md`, on les llegeix cada legatus amb qualsevol harness.

## El que encara depèn de tu

Uns quants passos continuen sent cosa teva. Claude Code et demana que confiïs en la carpeta la primera vegada. Codex et demana que n'aprovis els hooks un cop, i un altre cop quan canvien. Cada màquina necessita els seus propis inicis de sessió. I ets tu qui decideix quin legatus corre on, amb quin harness i amb quin model. Són decisions del principal, i cap script no les hauria de prendre per tu.
