# tools/refs-check/

Verificació de referències dels documents acadèmics que revisa el revisor. Embolcalla `bibsleuth` (triangulació en sis bases de dades: OpenAlex, Semantic Scholar, CrossRef, arXiv, DBLP, PubMed) i hi afegeix una passada que obté els resums, perquè el revisor pugui comparar l'**afirmació** que fa l'article revisat sobre una referència amb **el que diu realment la referència**.

Produeix un fitxer markdown `<paper-stem>-refs-checks.md` que viu al costat del document revisat i es converteix en la **font de veritat** de la verificació de referències d'aquell document: el revisor el llegeix a les revisions posteriors en lloc de tornar a consultar bibsleuth.

L'encàrrec inicial, del taller original (2026-05-28):

> «[reviewer], quan revisis un document acadèmic, crea-hi al costat un `*-refs-checks.md` paral·lel on recullis la llista de referències de l'article i la teva validació. Si pots, aconsegueix el resum de cada article, per poder verificar la probabilitat que l'article digui de debò el que l'article revisat afirma sobre la referència. Després pots tractar aquest fitxer `*-refs-checks.md` com a font de veritat, i així no cal que tornis a consultar l'eina bibsleuth.»

## Què hi ha aquí

| Fitxer | Què fa |
|---|---|
| `check_refs.py` | L'embolcall. Executa `bibsleuth check`, obté els resums (cadena d'alternatives Semantic Scholar → OpenAlex → Crossref) i genera el markdown font de veritat. Idempotent: si el tornes a executar amb una referència nova al .bib, només afegeix l'entrada nova; les anotacions manuals del revisor es conserven. |
| `setup.sh` | Preparació idempotent de la màquina. Instal·la `bibsleuth` amb `uv tool install bibsleuth --python 3.12` i fa una prova ràpida d'accés a la xarxa contra una referència que se sap real. Executa'l una vegada per màquina. |
| `README.md` | Aquest fitxer. |

## Primera configuració en una màquina nova

```bash
bash tools/refs-check/setup.sh
```

Posa `REFS_CHECK_CONTACT=you@example.org` al perfil del shell: OpenAlex i Crossref demanen una adreça de contacte als clients educats, i l'embolcall l'afegeix al seu User-Agent només quan la variable està definida.

Idempotent: el pots tornar a executar sense risc. Necessita `uv` (si falta, l'script t'explica com instal·lar-lo). Instal·la bibsleuth com a eina uv (`~/.local/bin/bibsleuth`), fixada a Python 3.12 perquè bibsleuth requereix `>=3.12`. Després de la configuració, tant `bibsleuth` com l'script embolcall del taller estan preaprovats a `.claude/settings.json`: cap petició de permís durant les execucions dels agents.

L'estat d'instal·lació de cada màquina es registra a [`memory/reference_hosts.md`](../../memory/reference_hosts.md).

## Ús diari

```bash
# Produce / refresh the source-of-truth file:
python3 tools/refs-check/check_refs.py PATH/TO/refs.bib

# Custom output path:
python3 tools/refs-check/check_refs.py PATH/TO/refs.bib -o PATH/TO/my-refs.md
```

La sortida per defecte és `<bib-stem>-refs-checks.md`, al costat de l'entrada. Per exemple:
- `academic-reviews/schweitzer_rocuts_review/thesis.bib` →
- `academic-reviews/schweitzer_rocuts_review/thesis-refs-checks.md`

## Com és el fitxer font de veritat

```markdown
# Reference verification — `thesis.bib`

**Source:** /path/to/thesis.bib
**Generated:** 2026-05-28T...
**bibsleuth version:** 0.1.3
**Providers consulted:** openalex, semantic_scholar, crossref, arxiv, dblp, pubmed
**Summary:** 47 likely, 3 unverified, 2 verified

> [!info]
> This file is the **source of truth** for reference validation on this document...

---

## [author2023key] — `likely`

**Citation:** Author Names (2023). *Paper Title*. https://doi.org/...

- **Bibsleuth verdict:** `likely` (score 0.78)
- **Entry type:** article
- **DOI:** [10.xxxx/xxxx](https://doi.org/10.xxxx/xxxx)
- **Providers with hits:** crossref, openalex, semantic_scholar (3/6)

**Abstract** (via openalex):

> [first ~300 words of abstract …]

**Cited in paper at:** _(The reviewer: fill in section / page)_
**Claim made:** _(The reviewer: what the reviewed paper says about this reference)_
**Assessment:** _(The reviewer: supported / partially supported / unsupported / claim is generic / no full-text access)_
**Flags:** _(auto-fill: chimeric / year-mismatch / author-mismatch)_

---
```

## Veredictes del revisor: què volen dir

L'embolcall calcula un **veredicte del revisor** (el «Reviewer verdict») a partir de la sortida de bibsleuth, combinant la triangulació en bases de dades acadèmiques amb una comprovació de disponibilitat de l'URL (obre l'URL, segueix les redireccions i compara el títol i el cos de la pàgina amb el títol citat).

| Veredicte | Significat | Acció |
|---|---|---|
| ✅ `confirmed` | Bibsleuth `verified`/`likely` **o** URL viu + el títol o el cos de la pàgina coincideixen amb el títol citat | Es pot enviar |
| ⚠️ `title-mismatch` | L'URL existeix i la pàgina torna 200, però el títol de la pàgina no coincideix amb el títol citat | Cal mirar-ho: pot ser que l'editorial hagi reformulat el títol (correcte) o una referència quimèrica (crític) |
| 🚫 `unreachable` | L'URL torna 4xx/5xx o se n'esgota el temps | Enllaç trencat o invenció: troba l'URL viu o treu la citació |
| ❓ `escalate` | Ni URL, ni DOI, ni candidats a les bases de dades acadèmiques | **El principal ho ha de verificar a mà.** Cap article surt fins que aquesta llista estigui buida. |

## Veredictes de bibsleuth: la capa inferior

Bibsleuth mateix genera `verified` / `likely` / `unverified`. Aquests veredictes alimenten el veredicte del revisor, però **no són l'última paraula**: en concret, `verified` per a una entrada `@misc` amb un camp d'URL només vol dir «aquí hi ha una cadena d'URL», no pas «l'URL apunta a una pàgina real». El principal va detectar aquest forat el 2026-05-28; la capa de disponibilitat d'URL n'és la solució.

| Veredicte de bibsleuth | Significat a la capa de bases de dades acadèmiques |
|---|---|
| `verified` | Coincidència d'alta confiança en diversos proveïdors (referències acadèmiques); O BÉ un marcador de posició «misc amb URL» (literatura grisa: cal comprovar la disponibilitat de l'URL per a una verificació real) |
| `likely` | Coincidència probable a les bases de dades acadèmiques; alguna desviació de metadades, però és el mateix article |
| `unverified` | Per sota del llindar de coincidència a tots els proveïdors. Pot ser un article real amb metadades dolentes, O BÉ una invenció. Ho comprova el principal o el revisor. |

El cas **quimèric** és el subtil: el bib té un DOI fals; bibsleuth segueix el DOI i en treu un article real però diferent. La comparació de títols del pas de disponibilitat d'URL ho detecta: l'URL és viu, però el títol de la pàgina no coincideix amb el títol citat → marca `title-mismatch`.

## La capa de disponibilitat d'URL: què fa

Per a cada entrada del `.bib` amb un camp `url` (i per a l'URL resolt de cada DOI):

1. **Obre l'URL** amb un User-Agent semblant al de Safari (les editorials sovint bloquegen els UA per defecte de Python).
2. **Segueix les redireccions** fins al límit habitual.
3. **Classifica la resposta:**
   - 200 → viu; n'extreu el títol de la pàgina (og:title → `<title>` → primer `<h1>`) i el cos
   - 401/403/429 → bloquejat (mur de pagament, bloqueig antibots, límit de freqüència: la pàgina pot existir, però no es pot confirmar)
   - 404/410 → mort: enllaç trencat o invenció
   - 5xx / temps esgotat / connexió rebutjada → inaccessible
4. **Compara el títol citat amb el títol de la pàgina** amb una heurística de solapament de tokens. Si la coincidència només amb el títol falla, recorre a cercar-lo al cos de la pàgina (així es resolen les editorials que reformulen els títols: per exemple, Khan Academy embolcalla el títol de la xerrada TED de Khan amb la seva pròpia capçalera).
5. **Passa el resultat al veredicte del revisor.**

L'embolcall espera ~0,3 s entre obertures d'URL per ser respectuós amb les API gratuïtes i els servidors de les editorials.

## La capa de recomprovació d'URL amb Playwright: `verify-urls.mjs`

La passada d'URL de `check_refs.py` fa servir un client HTTP simple. Molts servidors d'editorials i de blogs (Macmillan, BJET, RIED, theconversation, llocs darrere de Cloudflare) **bloquegen els clients que no són navegadors** i li tornen `403`, cosa que deixa un mur de veredictes `escalate` que en realitat només volen dir «han rebutjat el meu client», no pas «aquesta referència és sospitosa». `verify-urls.mjs` és la **capa d'escalada**: torna a carregar aquests URL en un Chromium headless real (User-Agent i capçaleres correctes), que passa per sobre de la majoria de bloquejos antibots suaus, i escriu el resultat al `*-refs-checks.md`.

```bash
# Re-check every not-yet-`alive` URL in a refs-checks file (default):
node tools/refs-check/verify-urls.mjs PATH/TO/foo-refs-checks.md

# Preview without writing:
node tools/refs-check/verify-urls.mjs PATH/TO/foo-refs-checks.md --dry

#   --only-blocked   re-check only `blocked` (403) entries, skip `unreachable`
#   --all            re-check every URL block, even ones already `alive`
#   --timeout MS     per-page nav timeout (default 25000)
```

Llegeix els títols citats del `.bib` germà (o de `--bib PATH`), carrega cada URL de destinació, registra l'estat HTTP final i el `<title>` de la pàgina, calcula una coincidència de títol per solapament de tokens i modifica **només** el subbloc `**URL check**`, la vinyeta `**The reviewer verdict:**`, el veredicte de la capçalera `## [key]` i el resum agregat. Mai no toca les anotacions manuals de Claim/Assessment.

**L'única invariant estricta: la recomprovació només pot millorar.** La disponibilitat de l'URL i la triangulació a les bases de dades acadèmiques són eixos d'evidència independents. Una referència que les bases de dades de bibsleuth ja han deixat en `confirmed` **mai** no pot baixar a `escalate` només perquè una editorial bloqueja el navegador. Per això, davant d'un `403` o d'un error de navegació, l'script conserva el veredicte anterior (i només actualitza les notes de la comprovació d'URL); un `404` dur apareix com a `unreachable`, però tampoc no esborra un `confirmed` per les bases de dades. Viu + títol coincident → `confirmed`; viu + títol no coincident → `title-mismatch` (olor de quimera), tret que la referència ja estigués confirmada per les bases de dades. (Aquesta invariant existeix perquè la primera versió ho feia malament i el 2026-05-29 va rebaixar quatre referències confirmades per les bases de dades; aquest error és el motiu que la regla estigui escrita.)

Un `403` residual fins i tot des del navegador real (normalment una pàgina intersticial de Cloudflare: `"Just a moment…"` / `"Access Denied"`) vol dir que l'URL és realment darrere d'un repte dur: el veredicte es queda com estava, i una referència sense evidència prèvia es queda en `escalate` perquè el principal la confirmi a mà.

La configuració la fa `setup.sh` (pas 6: instal·la el paquet npm `playwright` localment i aprovisiona Chromium). `node_modules/` està ignorat per git; els elements duradors versionats són `verify-urls.mjs`, `package.json` i `.gitignore`.

## La regla estricta contra les al·lucinacions

**No inventis mai un URL o un DOI per «omplir» una entrada amb metadades que falten.** És el mode de fallada que tot el sistema existeix per evitar. Del mateix encàrrec:

> «El que és CRÍTIC, i vull dir CRÍTIC, és que no podem enviar un article amb una referència [no] verificada del tot... intentar publicar amb referències al·lucinades és una pèrdua de prestigi que no vull arriscar.»

Si una entrada del `.bib` no té URL ni DOI al material font, deixa el camp buit. La referència apareixerà a la secció `❓ Refs to confirm manually` (referències per confirmar a mà). El principal troba l'URL correcte; el revisor actualitza el .bib; torna-ho a executar amb `--force`.

Al taller original, el revisor (2026-05-28) es va adonar que s'estava inventant un URL de la Comissió Europea d'aparença plausible mentre extreia el .bib de RIED. La detecció automàtica i la reversió van ser correctes. La lliçó: la temptació d'«omplir» un URL que falta és exactament el mode de fallada. Resisteix-la.

## La cadena d'alternatives per obtenir resums

Bibsleuth mateix no torna resums. `check_refs.py` hi afegeix:

1. **Semantic Scholar**: el camp de resum més net, sense clau d'API, nivell gratuït amb límit de freqüència.
2. **OpenAlex**: format d'índex invertit, que l'script desinverteix en text corrent.
3. **Crossref**: XML JATS al camp `abstract`, sense l'HTML.

Cada referència dispara d'una a tres peticions GET (guanya el primer proveïdor que respon). Espera de 0,4 segons entre referències per mantenir-nos per sota dels límits del nivell gratuït.

Si cap dels tres proveïdors no torna un resum (habitual en llibres, tesis, literatura grisa, pòsters de congressos), l'entrada mostra «Abstract: not retrievable» i el revisor ho anota explícitament al camp Assessment.

## Regles d'idempotència

`check_refs.py` analitza les seccions `## [refkey]` del markdown existent abans d'escriure. Per a cada referència del .bib:

- **La clau ja és al fitxer** → se salta. Els camps manuals del revisor (Cited-at, Claim, Assessment, Flags manuals) es conserven.
- **Clau nova que no és al fitxer** → s'executa la comprovació de bibsleuth + s'obté el resum + s'afegeix.

Això vol dir que, a mesura que la llista de referències d'un article creix durant l'escriptura, tornes a executar l'script i només es processen les referències noves. La feina de revisió acumulada es manté intacta.

## Què fa el revisor amb aquest fitxer

La versió curta del flux de treball del revisor:

1. Extreu el .bib del document que es revisa (l'ideal és el que proporciona l'autor; extret amb GROBID per als PDF sense font).
2. Executa aquest script → obtens el `*-refs-checks.md`.
3. Per a cada referència: localitza l'afirmació que la cita a l'article, enganxa-la a Claim made, compara-la amb l'Abstract i escriu l'Assessment.
4. Agrega les troballes al document principal de revisió del revisor (un per encàrrec, a `academic-reviews/<engagement>/`). Els problemes de citació s'assignen a la matriu de gravetat: **Crític** per a referències inventades o quimèriques, **Greu** per a citacions que no sostenen l'afirmació, **Retoc** per a DOI que falten o metadades que no coincideixen.

## Limitacions

- **Encara no hi ha extractor de referències de PDF.** L'entrada de documents dona per fet una font `.bib`. Per als PDF sense font: demana-la a l'autor, o executa GROBID a part (previst com a eina de seguiment quan arribi el primer encàrrec només amb PDF).
- **Per defecte es fa servir el mode `--no-llm` de bibsleuth**, per determinisme i cost. El mode assistit per LLM detecta més citacions semànticament errònies, però costa crides a l'API i fa el resultat menys reproduïble. Si un encàrrec crític justifica la comprovació més profunda, afegeix `--llm-on` a la invocació del subprocés de bibsleuth (ara mateix no està exposat com a opció de `check_refs.py`; afegir-l'hi és trivial).
- **Els resums no són el text complet.** El revisor pot verificar a partir d'un resum que una afirmació genèrica hi encaixa, però no una afirmació específica («l'article diu X sobre Y», on X és un detall enterrat a la pàgina 14). Per a aquests casos cal el text complet de l'article citat o una comprovació manual.

## Relacionat

- [Les regles del revisor: fan que la verificació de referències no sigui opcional](../../characters/reviewer/rules.md)
- [Mode de treball de codi com a acció](../../memory/feedback_browser_tasks_code_as_action.md): la mateixa actitud aplicada a les tasques de navegador; la verificació de referències segueix el mateix patró (eina petita i dedicada, fitxer de sortida persistent, reexecucions idempotents).
- [bibsleuth upstream](https://github.com/yy/bibsleuth): MIT, en desenvolupament actiu el març del 2026.

---

Creat el 2026-05-28 al taller original, per a la verificació de referències del revisor.
