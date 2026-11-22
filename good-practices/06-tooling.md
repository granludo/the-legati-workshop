# 6. Les eines

El taller ve amb eines que funcionen. Així és com cal pensar quina fer servir i quan.

## Els tres nivells de còmput

**Local (Ollama)**: models que corren al teu propi maquinari. Gratuïts un cop configurats, privats (les teves dades no surten de la teva màquina), lents comparats amb les API al núvol. Ideals per a feina mecànica a l'engròs: traducció entre llengües quan els models locals donen la talla, resums de documents llargs, classificació i etiquetatge, neteja de transcripcions. La regla per als models locals: com més gran, millor, gairebé sense excepció. Un model de 125B que va lent és més útil que un de 27B que va ràpid, perquè el gran fa menys errors de precisió. No facis servir models locals més petits per guanyar temps: el temps que estalvies generant l'esborrany, el perds corregint-ne els errors.

**La IA de la sessió (el model que fa anar la teva sessió de Claude Code o Codex)**: el model amb qui parles ara mateix. Ideal per a la feina intel·lectual de pes: tot el que demana la teva veu, tot el que demana sintetitzar diverses fonts, tot el que demana un judici calibrat sobre una qüestió complexa. No hi enviïs feina mecànica: és més lent per a tasques a l'engròs i costa més atenció del que val.

**API de pagament (OpenAI, o el proveïdor de models de frontera a què tinguis accés)**: segona opinió, revisió a fons, tasques en què ni el local ni la IA de la sessió arriben al nivell de qualitat que cal. Fes-la servir amb intenció. Cada crida costa diners de veritat; deixa'n constància. No hi vagis per defecte només perquè és còmode.

## La decisió d'encaminament a la pràctica

Abans d'enviar qualsevol tasca per lots a un model, pregunta't:
- És mecànica? (traducció, resum, classificació, neteja) → Ollama local
- Demana la meva veu o un judici interpretatiu? → IA de la sessió
- És una segona opinió o una revisió a fons que el local no pot fer? → API de pagament, amb consciència del cost

L'error més comú és enviar-ho tot a la IA de la sessió perquè és còmode. És el patró de la màquina expenedora: obtens respostes, però no construeixes res. Per a les tasques mecàniques, els models locals amb una plantilla són més barats i més ràpids alhora.

## Una sola porta d'entrada: l'ordre `llm`

Totes les crides a models fora de la sessió passen per una sola ordre, `llm`, de Simon Willison (https://llm.datasette.io). Els models locals d'Ollama i les API de pagament fan servir la mateixa sintaxi, i `llm` registra cada prompt i cada resposta en una base de dades SQLite a la teva màquina, de manera que després pots veure què vas enviar, a quin model i què et va tornar (`llm logs`). La configuració és a `tools/llm/README.md`.

Per als models locals, instal·la Ollama i el connector `llm-ollama` (`llm install llm-ollama`). Si Ollama corre en local, `localhost:11434` és l'adreça per defecte, i els teus models locals apareixen a `llm` al costat dels de pagament.

Els ajudants antics, `tools/ollama/call.py` i `tools/openai/call.py`, només hi són per als scripts que ja els fan servir. No els cridis a mà ni escriguis codi nou que en depengui: una crida que se salta `llm` se salta el registre.

Consulta sempre la llista de models abans d'escriure una tasca que depengui d'un model concret:
```bash
llm models
```

No fixis noms de models dins dels scripts: en Marc es baixa models nous sovint, i un script que fa referència a `qwen3.5:27b` pot estar fent servir un model pitjor que `qwen3.5:122b` sense saber-ho.

## Generació de PDF: pandoc + Typst

La skill és `/md2pdf`. Fa servir pandoc per convertir el markdown a Typst, i després Typst a PDF. La plantilla acadèmica (`academic-template.typ`) s'encarrega de les fonts, els marges, les citacions i la maquetació. En la majoria de casos no cal tocar la plantilla: la skill ja fa la crida.

Dues coses que cal saber de la cadena d'eines: Typst renderitza més de pressa que LaTeX i no demana cap instal·lació més enllà de `brew install typst`. Si ja tens fluxos de treball amb LaTeX, pots cridar pandoc amb l'opció `--pdf-engine=xelatex`. La skill admet totes dues vies.

## Transcripció: mlx-whisper

`tools/transcribe/` fa servir mlx-whisper per transcriure àudio en local. Corre de manera nativa en Apple Silicon i és prou ràpid per a l'ús pràctic. Per a cada fitxer d'àudio produeix una transcripció en brut, que hauria d'anar seguida d'una passada de revisió amb un LLM per caçar els errors característics (noms propis, termes tècnics, canvis de llengua). No citis mai una transcripció sense haver-la revisat abans.

## Verificació de referències: tools/refs-check

Abans que cap article surti del taller, s'han de verificar totes les referències. `tools/refs-check/check_refs.py` se n'encarrega: consulta diverses bases de dades acadèmiques (OpenAI, Semantic Scholar, CrossRef, arXiv), comprova que els URL responguin i recupera els resums per comparar-los. El resultat és un veredicte per referència: confirmed, title-mismatch, unreachable o escalate. Qualsevol referència que no surti com a «confirmed» bloqueja l'enviament.

La regla inflexible: no t'inventis mai un URL ni un DOI per omplir metadades que falten. Deixa el camp buit i que el cas arribi fins a tu. Un article amb unes quantes marques [URL missing] es pot arreglar. Un article amb citacions inventades, no.

## Google Workspace: el carril de l'agent de comunicacions

Si configures l'agent de comunicacions, fa servir la CLI `gws` (Google Workspace CLI) per accedir a Gmail, Calendar i Drive. La configuració demana una autenticació OAuth d'un sol cop: els passos són a `tools/google/README.md`. La restricció clau: l'abast OAuth és només de lectura. L'agent de comunicacions pot veure el teu calendari i la safata d'entrada; no pot enviar, crear esdeveniments ni modificar res. Això s'imposa a nivell de credencial.
