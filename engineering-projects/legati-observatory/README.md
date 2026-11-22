---
type: project-folder
project: Legati Observatory
status: en funcionament (nucli portable + adaptadors per a Claude Code i Codex)
---

# Observatori dels Legati

Una capa d'observabilitat i coordinació lleugera **portable, estàtica i estigmèrgica** per a les sessions d'IA en paral·lel d'un taller (els legati, els teus agents amb nom). Quan diverses instàncies d'agent treballen alhora contra el mateix repositori, et diu **qui és actiu, què fa, qui orquestra qui i quant ha costat**, i els dona una manera de **no trepitjar-se** quan escriuen fitxers compartits.

**Per què fer-ne un de propi** en lloc d'instal·lar un dashboard de tercers: es manté portable entre harness (no està lligat a una sola eina), estàtic (sense servidor web, sense la superfície de confiança d'una base de dades al núvol), centrat en el problema de coordinació que de debò fa mal (instàncies en paral·lel que competeixen pel mateix fitxer) i prou llegible per servir també de material docent. És un exemple resolt d'**estigmèrgia per sobre d'orquestració**: els agents es coordinen **sense cap orquestrador central**, deixant rastres en fitxers compartits (fitxers de presència i de bloqueig consultiu com a rastres de feromones) i llegint l'estat de l'entorn. El repositori és el termiter.

## Com funciona (tres capes, un tallafoc)

```
 harness hooks  ──►  adapters/<harness>/  ──►  event schema  ──►  .observatory/  ──►  obs render  ──►  dashboard
 (Claude Code,        (the only harness-       (the contract,      (portable core:      (static)         (.md / .html)
  Codex, …)            aware code)              ADAPTERS.md)        events+presence+locks)
```

El nucli (`obs.py` + els generadors) no sap res de cap harness. Per donar suport a un harness nou, escrius **un** adaptador que emeti el mateix esquema d'esdeveniments; no canvia res més. Vegeu [`DESIGN.md`](DESIGN.md) i [`ADAPTERS.md`](ADAPTERS.md).

## Fitxers

| Fitxer | Què és |
|---|---|
| [`obs.py`](obs.py) | La CLI del nucli portable: `emit` · `task` · `heartbeat` · `who` · `agent` · `lock {acquire,check,release}` · `say` · `chat` · `render`. Només biblioteca estàndard, Python 3.9+. |
| [`DESIGN.md`](DESIGN.md) | El disseny: el tallafoc de portabilitat, l'esquema d'esdeveniments, l'organització dels fitxers, el protocol de bloqueig, els generadors. |
| [`ADAPTERS.md`](ADAPTERS.md) | El contracte de portabilitat: esquema d'esdeveniments + configuració de hooks de Claude Code d'exemple + com portar-lo a un altre harness. |
| [`adapters/claude-code/hook-handler.py`](adapters/claude-code/hook-handler.py) | Adaptador de captura de Claude Code (el codi que coneix el harness només viu als adaptadors; falla en silenci i surt amb 0, de manera que mai no pot bloquejar una sessió). |
| [`adapters/codex/hook-handler.py`](adapters/codex/hook-handler.py) | Adaptador de captura de Codex CLI (el mateix contracte). S'instal·la a cada màquina amb `bash tools/legati/install-hooks.sh codex`. |

El [`.claude/settings.json`](../../.claude/settings.json) del repositori ja connecta els cinc esdeveniments de hook de Claude Code a l'adaptador fent servir `$CLAUDE_PROJECT_DIR`, de manera que un clon nou comença a capturar des de la sessió següent. Codex necessita un pas per màquina: `bash tools/legati/install-hooks.sh codex`, i després aprovar els hooks una vegada dins Codex amb `/hooks`.

## Ús

```bash
OBS=engineering-projects/legati-observatory/obs.py
python3 $OBS agent writer                                       # on persona switch — attribute events to this legatus
python3 $OBS task "what I'm doing"                              # set current task
python3 $OBS who                                               # who's live
python3 $OBS lock acquire dashboards --task "refresh" --ttl 20  # claim before a risky shared write
python3 $OBS lock release dashboards
python3 $OBS render                                            # markdown dashboard -> render/dashboard-<host>.md
python3 $OBS render --html                                     # interactive HTML  -> render/dashboard-<host>.html
python3 $OBS render --html --since 7d                          # HTML embed window: today|7d|30d|all (default 30d)
```

**Dues superfícies, totes dues estàtiques + ignorades per git + per màquina:**
- **Markdown** (`render/dashboard-<host>.md`): la vista d'un cop d'ull: sessions actives, bloquejos, activitat i cost d'avui, graf d'orquestració en Mermaid.
- **HTML** (`render/dashboard-<host>.html`): s'obre en un navegador (`file://`, sense servidor). Les dades dels esdeveniments van incrustades com a JSON amb JS pur, de manera que els **nivells de zoom són interactius dins la pàgina**: interval de temps (ara / avui / 7d / 30d / tot), filtres per agent o projecte, cerca de text lliure, i clic sobre una sessió per veure'n la cronologia completa. Les barres de cost i els recomptes es recalculen a cada canvi de control.

Tot l'estat de la màquina viu a `<repo>/.observatory/` (ocult) i els dashboards generats a `render/`, **tots dos ignorats per git**, perquè depenen de la màquina.

> El graf d'orquestració de l'HTML fa servir Mermaid. Per generar el graf sense connexió, posa un `mermaid.min.js` a `engineering-projects/legati-observatory/vendor/` (està ignorat per git). Sense aquest fitxer l'HTML es genera igualment: el graf només es mostra com a text, i `obs render --html` n'imprimeix l'avís.

## Llicència

Vegeu la [`LICENSE`](../../LICENSE) del repositori.
