---
name: add-source
description: Incorpora una font nova (vídeo de YouTube, PDF, fitxer d'àudio, article web, text) a l'arbre sources/ del taller, per a un projecte d'escriptura concret o per a ús compartit. S'encarrega de la descàrrega, l'extracció d'àudio, la transcripció, la ubicació, el README i el registre a INDEX.md.
---

# /add-source

Fes-la servir quan el principal vulgui portar material font nou al repositori. La skill cobreix tot el procés d'entrada: adquirir → derivar → ubicar → documentar → registrar. És **conservadora per disseny**: deixa la font al seu lloc i ofereix enllaçar-la des dels documents del projecte, però no edita automàticament les wikis ni la memòria del projecte. La integració és un pas a part que aprova el principal.

## Quan invocar-la

El principal diu coses com:
- «afegeix aquesta font: <URL>»
- «/add-source <URL o camí>»
- «he trobat aquest article, el pots posar al lloc que toca?»
- «aquí tens una gravació nova d'una conferència per al llibre ia-i-educacio»

## Entrades

Accepta qualsevol d'aquestes, i detecta'n el tipus automàticament:
- **URL de YouTube** → fes servir `yt-dlp` (ja instal·lat en aquest entorn).
- **URL d'article web o article acadèmic** (PDF o HTML) → fes servir `curl` o `WebFetch`. Si la pàgina ofereix el PDF, descarrega sempre el PDF.
- **PDF local o un altre binari** → mou-lo o copia'l a la ubicació de destinació.
- **Fitxer local d'àudio o vídeo** → el mateix, amb els passos derivats d'àudio i transcripció.
- **Text o markdown enganxat** → escriu-lo directament en un fitxer `.md` a la carpeta que toca.

Si l'entrada és ambigua (per exemple, un nom de fitxer sol), pregunta al principal abans de continuar.

## Procés (segueix l'ordre)

### 1. Identifica l'àmbit

Pregunta al principal (o dedueix-ho del context) a quin àmbit pertany la font:
- **`sources/shared/<type>/`** si alimenta diversos projectes o és d'interès general.
- **`sources/<project>/`** si només té sentit per a un projecte d'escriptura concret. Slugs de projecte vàlids avui: `ia-i-educacio`, `palantir-paper`, `aprenentatge-personalitzat`, `aac-book`.

Si dubtes, **per defecte, `shared/`**. És més fàcil separar-la més endavant que no pas tornar-la a compartir ara.

### 2. Tria un slug de carpeta

Crea una carpeta dins l'àmbit triat amb un nom en minúscules i kebab-case. Convencions:
- **Xerrades i conferències:** `{year}-{venue}-{topic}`, per exemple `2024-udl-sputnik/`.
- **Llibres i articles:** `{firstauthor}-{year}-{shortname}`, per exemple `weller-2022-metaphors/`.
- **Cursos i classes magistrals:** `{name}-{subtitle}`, per exemple `lamb-101-rag-masterclass/`.
- **Entrades de blog i fonts d'un sol fitxer:** sense carpeta; posa el fitxer directament dins l'àmbit amb un nom descriptiu.

Per a una font de diversos fitxers (vídeo + àudio + transcripció + metadades), fes servir sempre una carpeta. Per a un PDF únic i autònom, deixa'l directament dins l'àmbit.

### 3. Obtén els bytes

**URL de YouTube:**
```bash
cd <scope-folder>
yt-dlp --write-info-json --write-subs --write-auto-subs \
       --sub-langs "ca,es,en,ca.*,es.*,en.*" \
       -f "bv*+ba/b" \
       -o "%(title)s.%(ext)s" "<URL>"
```
Si ffmpeg no està instal·lat a tot el sistema, yt-dlp deixarà els fluxos de vídeo i d'àudio per separat, i no passa res. L'àudio per a la transcripció serà al fitxer `.webm` (Opus) o `.m4a`.

**URL web (PDF):**
```bash
curl -sSL -o <filename>.pdf "<URL>"
```

**URL web (article HTML):** fes servir `WebFetch` amb un prompt que demani el text de l'article en markdown, i desa'n el resultat.

**Fitxer local:** `mv` o `cp` al seu lloc.

### 4. Deriva formats útils

**Vídeo → àudio (MP3 per transcriure o escoltar):**
```bash
uv run --with imageio-ffmpeg python -c "
import imageio_ffmpeg, subprocess
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ffmpeg, '-y', '-i', 'input.webm', '-vn',
                '-codec:a', 'libmp3lame', '-b:a', '128k', '-ar', '44100',
                'output.mp3'])
"
```

**Àudio → transcripció:** fes servir l'eina que ja hi ha al repositori.
```bash
uv run --project tools/transcribe tools/transcribe/transcribe.py --lang ca <audio.mp3>
```
(Canvia-ho per `--lang es` o `--lang en` segons correspongui.) Escriu `.srt` i `.txt` al costat de l'entrada. La llengua es dedueix del context; si el principal no l'especifica, pregunta.

**Revisió obligatòria de la transcripció amb un LLM.** Whisper fa errors grossos (noms propis, sigles, canvis de llengua, vocabulari intern d'un grup) amb prou freqüència perquè el `.txt` en brut no es pugui considerar apte per citar. Conserva el fitxer en brut com a rastre d'auditoria i produeix un `<slug>.reviewed.txt` amb una passada d'LLM. El nivell de model segueix les regles de còmput (`AGENTS.md` §6): el model de la sessió, o un model frontera a través de `llm`, per a qualsevol llengua que un model local escrigui malament; un model local gran a través de `llm` serveix per a la correcció mecànica de noms propis en llengües que maneja bé; revisió amb un model frontera quan el contingut és determinant. El fitxer revisat ha d'indicar què s'ha canviat (una secció inicial per a transcripcions curtes, `==highlight==` en línia per a les llargues) perquè el principal ho pugui comprovar per mostreig.

**PDF:** deixa'l tal com és. Si l'extracció de text és útil, esmenta-la com a pas posterior opcional; no la facis per defecte.

### 5. Escriu un `README.md` dins la carpeta de la font

Per a qualsevol **font de diversos fitxers**, crea un `README.md` amb:

```markdown
# <Source title>

- **Type:** <conference | paper | blog post | video course | ...>
- **Author / speaker:** <...>
- **Origin:** <original URL or citation>
- **Date of material:** <YYYY-MM-DD or year>
- **Date added to repo:** <YYYY-MM-DD>
- **Language:** <ca | es | en | ...>
- **Project(s) it feeds:** <list of writing projects that reference this>

## Summary
<One paragraph describing what this source contains and why it was added.>

## Files in this folder
- `<filename>` — <one-line description>
- ...

## Notes
<Anything quirky: transcription quality, missing subtitles, trailing hallucinations, OCR issues, pages to skip, etc.>
```

Les fonts d'un sol fitxer no necessiten README propi: la seva entrada a `sources/INDEX.md` ja en fa la funció.

### 6. Registra-la a `sources/INDEX.md`

Afegeix una entrada a la secció que toca (`shared/<type>/` o `<project>/`). Segueix el format existent: una vinyeta amb el nom del fitxer o de la carpeta entre accents greus, seguida d'una descripció d'una línia i de les metadades crítiques.

**Si encara no existeix una secció per a aquest àmbit**, crea-la per ordre alfabètic entre les existents, amb el mateix estil d'encapçalament.

**Comprovació de duplicats:** abans de desar la font, cerca amb grep a `sources/INDEX.md` l'URL d'origen, el títol o el nom del fitxer. Si hi ha coincidència, atura't i digues-ho al principal en lloc d'incorporar-la dues vegades.

### 7. Ofereix la integració (no l'apliquis automàticament)

Quan la font sigui al seu lloc i indexada, **ofereix**:
- Afegir-hi un punter al document del projecte corresponent (per exemple, el §16 de `writting-projects/ia-i-educacio/idees_ia_i_educacio.md`).
- Actualitzar el `BACKLOG.md` del projecte amb una tasca de seguiment com ara «llegir X i decidir si alimenta el capítol Y».
- Actualitzar la memòria del projecte amb un fet nou si la font canvia l'estat de les coses.

**Espera confirmació** abans de fer cap d'aquestes coses. El motiu: la memòria sobre separació de dominis a `memory/feedback_domain_separation.md` i la memòria sobre l'excés de la v3 a `memory/feedback_v3_overboard.md` alerten contra forçar referències entre dominis de projecte. Deixa que el principal decideixi quins projectes volen realment el punter.

### 7.5 Ofereix la integració a la wiki (també amb permís previ, també conservadora)

Un cop la font sigui al seu lloc i indexada, **ofereix** passar-la per la ingesta de la wiki. El procés:

```bash
# Always dry-run first — shows the proposed change set, writes nothing.
python3 tools/wiki/ingest.py <source-rel-path>
```

La prova en sec informa de:
- el resum d'extracció que ha produït el model (2-3 frases),
- les entrades de wiki existents que guanyarien un punter a la cronologia,
- les entrades noves que es crearien en esquelet (amb el slug proposat),
- les entrades ja enllaçades des de la font (idempotent: les fonts ja ingerides se salten netament).

Mostra la sortida de la prova en sec al principal. Si el principal l'aprova, aplica-la:

```bash
python3 tools/wiki/ingest.py --apply <source-rel-path>
```

Després executa els dos scripts de regeneració perquè les referències creuades i els INDEX reflecteixin les entrades noves:

```bash
python3 tools/wiki/build_cooccurrence.py
python3 tools/wiki/render_indexes.py
```

Si el principal ho salta, cap problema: la font continua a `sources/` i es pot ingerir més endavant en lot amb `tools/wiki/bootstrap.py --resume`.

**Per què amb permís previ i no automàtic:** l'extractor de vegades proposa slugs nous de persona o de tema que són variants d'entrades existents (per exemple, `juan-antonio-pereira` quan ja existeix `juanan-pereira`). El principal hauria de donar un cop d'ull a la llista d'esquelets nous abans que es desin, perquè no s'acumulin duplicats. La mateixa precaució val per als temes: l'extractor de tant en tant etiqueta categories genèriques més àmplies que la wiki ja ha decidit no fer canòniques.

### 8. Informe

Acaba amb un informe breu al principal:
- Què s'ha afegit (àmbit + camí).
- Què s'ha derivat (àudio, transcripció, etc.).
- Què s'ha omès (si escau, i per què).
- Quina integració s'ha ofert però no s'ha aplicat.

## Què NO fa aquesta skill

- **No** edita esborranys de projecte, wikis de llibres ni fitxers de memòria sense confirmació explícita.
- **No** mou ni canvia el nom de fitxers que ja són a `sources/`. Si cal moure alguna cosa d'un àmbit a un altre, és una tasca a part.
- **No** esborra l'original després d'una derivació correcta. La política d'arxiu és «conservar-ho tot»: el webm/mp4 original es queda al costat del mp3/txt derivat.
- **No** intenta endevinar la veu del principal. Si resumeixes una font al seu README, que sigui factual i de menys de 100 paraules. Els resums amb opinions o enfocaments van als documents del projecte, on el principal els pot reescriure.

## Relacionat

- [../sources/INDEX.md](../sources/INDEX.md): l'índex que manté aquesta skill.
- [../tools/transcribe/transcribe.py](../tools/transcribe/transcribe.py): l'script de transcripció que crida aquesta skill.
- [../tools/wiki/ingest.py](../tools/wiki/ingest.py): l'eina d'ingesta d'una sola font a la wiki, esmentada al pas 7.5.
- [../memory/feedback_index_maintenance.md](../memory/feedback_index_maintenance.md): per què l'índex s'ha de mantenir al dia.
