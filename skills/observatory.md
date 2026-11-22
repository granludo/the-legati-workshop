# /observatory: mira qui treballa i no li trepitgis la feina

**Quan invocar-la:** sempre que hi pugui haver més d'una sessió d'agent treballant alhora contra aquest repositori: abans de regenerar un fitxer compartit (un dashboard, un índex, un backlog), quan vulguis saber qui més està actiu, o quan canviïs de persona i vulguis que la teva activitat s'atribueixi correctament. També és la skill que has de llegir quan vulguis generar el dashboard.

**Qui l'executa:** qualsevol agent (qualsevol legatus). La captura és automàtica a través dels hooks; aquesta skill és la capa d'**autoinforme + coordinació** que només l'agent pot conduir.

El disseny complet és a [`../engineering-projects/legati-observatory/README.md`](../engineering-projects/legati-observatory/README.md) i [`DESIGN.md`](../engineering-projects/legati-observatory/DESIGN.md). Aquesta skill n'és la guia operativa.

---

## L'única variable d'entorn

```bash
OBS=engineering-projects/legati-observatory/obs.py
```

## A cada canvi de persona: atribueix els teus esdeveniments

Els hooks capturen automàticament cada crida d'eina, però necessiten saber quin legatus actua. Just en el moment de canviar de persona, executa:

```bash
python3 $OBS agent <your-legatus-name>     # e.g. orchestrator, writer, reviewer
```

Això escriu un marcador per sessió que preval sobre el valor per defecte de la sessió, de manera que tots els esdeveniments capturats a partir d'aleshores s'atribueixen al legatus actiu fins al canvi següent. És idempotent i barat: executa'l a cada canvi.

## Indica què estàs fent (opcional però útil)

```bash
python3 $OBS task "drafting the methodology paper §5"
```

`current_task` és el «què estic fent» llegible per humans que només saps tu; apareix a la taula de presència.

## Abans d'una escriptura compartida arriscada: comprova i bloqueja

Aquest és el sentit de tot plegat. Si estàs a punt de regenerar un fitxer que una altra sessió també podria estar escrivint (un dashboard, un `INDEX.md`, un `BACKLOG.md`):

```bash
python3 $OBS who                                          # 1. who else is live, doing what?
python3 $OBS lock acquire <slug> --task "..." --ttl 15    # 2. claim it (atomic; fails if already held)
#   ... do the write ...
python3 $OBS lock release <slug>                          # 3. release when done
```

`lock acquire` fa servir la creació exclusiva atòmica, de manera que **dos agents que cooperen no poden guanyar tots dos el mateix bloqueig**. Si l'adquisició **falla**, torna el propietari actual: **fes-ho saber a l'usuari i retira't**, no hi competeixis. Un bloqueig s'allibera sol en acabar el seu TTL si el propietari ha caigut (no hi ha interbloqueig).

El bloqueig és consultiu: funciona perquè els agents que cooperen el respecten. Escriu aquesta disciplina a la guia del teu agent: **abans de regenerar qualsevol fitxer compartit, adquireix-ne el bloqueig; si es denega l'adquisició, retira't.**

## Genera el dashboard

```bash
python3 $OBS render            # markdown -> render/dashboard-<host>.md  (read it in your editor)
python3 $OBS render --html     # interactive single-file HTML -> render/dashboard-<host>.html (open in a browser)
```

Totes dues superfícies són estàtiques, ignorades per git i per màquina. El markdown és la vista d'un cop d'ull; l'HTML és interactiu (filtres per agent, projecte o temps, detall d'una sessió, barres de cost).

## El que NO cal que facis

- **No cal que engeguis cap servidor ni cap dimoni.** Tot són fitxers estàtics generats a demanda.
- **No cal que en facis commit.** git ignora `.observatory/` i `render/`: depenen de la màquina.
- **No cal que configuris la captura a cada sessió.** Els hooks de `.claude/settings.json` ja la connecten; un clon nou captura des de la sessió següent.
