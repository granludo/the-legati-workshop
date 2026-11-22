# tools/wiki/

Scripts que construeixen i mantenen la capa d'índex wiki sobre el markdown del taller.

> [!note] Fet per al taller original
> Aquests scripts es van escriure per a un taller concret: les seves carpetes, els seus legati i els seus servidors de models (vegeu els selectors `SERVERS` / backend a l'inici de `ingest.py` i `bootstrap.py`). Llegeix-los com un exemple resolt per adaptar, no com una eina llesta per fer servir. Els registres d'execució (`*-log.md`) s'escriuen al costat dels scripts i git els ignora.

## Fitxers

- **`bootstrap.py`**: esquelets de primera passada. Recorre les carpetes dins l'abast, crida Ollama (qwen3.5:122b) per a cada fitxer amb un pressupost de context de 16k, agrega els resultats de tots els fitxers i escriu els esquelets de cada faceta a `wiki/<facet>/<slug>.md`. Memòria cau per hash del fitxer → idempotent en tornar-lo a executar. S'executa amb `python3 tools/wiki/bootstrap.py [--smoke|--dry-run|--resume|--limit N|--skip-write]`.
- **`chunk.py`**: divideix el markdown llarg en fragments que caben en un context de 16k per a Ollama. Estratègia: divisió per H2 → per paràgrafs → per frases. Reutilitzable des de qualsevol eina propera a l'arrencada de la wiki.
- **`validate.py`**: comprovador de coherència de l'arbre de la wiki: wikilinks trencats, slugs duplicats, entrades sense fonts, fonts que no són al disc. Executa'l després d'un bootstrap; es pot tornar a executar sense risc en qualsevol moment.
- **`bootstrap-log.md`**: registre d'execució de només addició escrit per `bootstrap.py`. Recull cada anàlisi per fitxer, cada recompte agregat, cada fallada i cada element que «necessita una decisió del principal».
- **`cache/`**: ignorat per git. Sortides d'Ollama per fitxer, indexades per l'SHA-256 del contingut del fitxer. Tornar a executar `bootstrap.py --resume` salta els fitxers el hash dels quals coincideix.

## Abast

Carpetes dins l'abast (només fitxers markdown):
- `writting-projects/`: excepte els directoris de tema i de compilació de Hugo (`themes/`, `public/`, `resources/`, `layouts/`, `archetypes/`, `static/`)
- `characters/`: els fitxers d'identitat dels legati
- `principals/`: els autors humans (tu)
- `memory/`: el sistema de memòria persistent
- `sources/`: els materials font en brut
- `engineering-projects/`: les carpetes de treball d'enginyeria
- Fitxers de l'arrel seleccionats: `INDEX.md`, `BACKLOG.md`, `PROJECTS.md`, `TODO.md`, `CLAUDE.md`, `README.md`

Fora de l'abast:
- `inbox/`: el material de correu i calendari del legatus comms (volàtil, en un carril separat, una regla del taller original)
- `archive/`: conservat però inactiu
- `confidential/`: ignorat per git
- `worldview-draft/`: pilot de graf per màquina (ignorat per git, pot no existir a totes les màquines)

## Restriccions

- **Només `qwen3.5:122b`** (segons `memory/feedback_ollama_big_guns_only.md`). Tots dos Studios accessibles des d'aquesta màquina.
- **Context màxim de 16k** (segons `memory/feedback_ollama_context_under_16k.md`). `chunk.py` imposa un pressupost de treball de 10k tokens d'entrada per crida.
- **Cap commit de git** durant el bootstrap. L'script escriu fitxers; el principal en fa el commit.

## Sortida

- `wiki/<facet>/<slug>.md`: esquelets per entrada. Frontmatter (type, slug, status, dates, source-count) + Summary + Timeline (construïda automàticament a partir del git log de les fonts enllaçades) + espai reservat per a Evolution + llista de Sources + espai reservat per a Cross-references.
- `wiki/<facet>/INDEX.md`: índex alfabètic de la faceta.
- `wiki/INDEX.md`: mapa de primer nivell de la wiki.
- `wiki/keywords/keywords.md`: referència alfabètica plana de paraules clau (termes que apareixen en ≥2 fitxers, amb una heurística de tokens en majúscula).

## Tornar-lo a executar

Dos motius per tornar-lo a executar:
1. **Reprendre després d'una execució parcial**: `python3 tools/wiki/bootstrap.py --resume`. Els encerts de la memòria cau són gratuïts; només es tornen a analitzar els fitxers canviats.
2. **Iterar sobre el prompt o l'esquema**: esborra la memòria cau (`rm -rf tools/wiki/cache/`) i torna'l a executar. Força crides noves a Ollama per a tot.

Després de qualsevol reexecució, executa `python3 tools/wiki/validate.py` per detectar enllaços trencats i entrades òrfenes.

## Manteniment a partir d'ara

El bootstrap és una primera passada. Manteniment en règim estable:
- **En tocar un fitxer**: quan s'afegeix, s'edita o es mou un fitxer de contingut dins les carpetes de l'abast, les entrades de la wiki que el referencien també s'han de tocar al mateix commit. El hook de pre-commit de `tools/git-hooks/pre-commit-wiki-check.sh` avisa quan aquesta disciplina falla.
- **Escombrada setmanal de l'orquestrador**: una execució periòdica de `validate.py` i propostes d'actualització per a les entrades amb un `last-touched` endarrerit.
- **Omplir la cua llarga**: el bootstrap deixa moltes entrades com a esquelets (frontmatter generat automàticament + fonts + cronologia; Summary/Evolution com a espais reservats). L'orquestrador i l'escriptor omplen els resums i l'evolució de mica en mica, a mesura que la feina toca els fitxers subjacents. Les entrades de més valor (projectes principals, persones amb nom, idees clau) tenen prioritat.
