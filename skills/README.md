# skills/: la convenció de la carpeta i la taula

Quan el principal invoca una skill (adreçant-se a un legatus en llenguatge natural, «Escriptor, passa l'unslop al capítol 3»; anomenant-la de passada, «fes servir /add-source amb aquest URL»; o escrivint `/<name> <args>`), **llegeix `skills/<name>.md` d'aquest repositori i segueix les instruccions que conté.** Aquesta carpeta és la font de veritat de totes les skills del taller, amb qualsevol harness.

**La invocació en llenguatge natural és la canònica.** Una ordre de barra sola pot quedar interceptada per l'analitzador del mateix harness abans que el legatus la vegi; en aquest cas, adreça't directament al legatus. Els fitxers de skill són markdown pla, no ordres de barra del harness, i per això funcionen igual a Claude Code i a Codex ([memory/feedback_scaffolding_portability.md](../memory/feedback_scaffolding_portability.md)).

**Aquesta taula és l'autoritat**; el `boot.md` de cada legatus llista el subconjunt que executa. Afegir una skill = el fitxer + una fila aquí. Un nom sense fitxer → digues-ho, no endevinis.

| Invocació | Fitxer | Qui l'executa | Què fa |
|---|---|---|---|
| `/start-here` | [start-here.md](start-here.md) | orchestrator | Posada en marxa: posa nom als teus legati, escriu el teu perfil, configura tots dos harness i el teu primer projecte. |
| `/status` | [status.md](status.md) | orchestrator | Resum d'orientació, només lectura: projectes actius, carrils, traspassos, primers elements del backlog, skills, decisions obertes. |
| `/write-as-[you]` | [write-as-user.md](write-as-user.md) | writer | Carrega el teu perfil d'escriptura i la teva visió del món abans de qualsevol tasca d'escriptura. Reanomena-la després de la configuració. |
| `/add-source` | [add-source.md](add-source.md) | orchestrator (circuit), writer (anàlisi) | Incorpora una font (YouTube, PDF, àudio, article web, text) a `sources/`. |
| `/md2pdf` | [md2pdf.md](md2pdf.md) | qualsevol | Converteix markdown en PDF a punt per imprimir amb pandoc + Typst. |
| `/image-gen` | [image-gen.md](image-gen.md) | orchestrator | Genera una imatge dissenyada a través d'una API d'imatges. De pagament: fes-la servir amb intenció. |
| `/playwright` | [playwright.md](playwright.md) | qualsevol | Un navegador de debò per a pàgines renderitzades amb JS o que demanen iniciar sessió: un script reutilitzable a `tools/<slug>/`. |
| `/observatory` | [observatory.md](observatory.md) | qualsevol | Qui està actiu, què fa cada sessió, bloquejos de fitxers indicatius, xat dins de la mateixa màquina. |
| `/unslop-text` | [unslop-text.md](unslop-text.md) | writer (qualsevol legatus sobre el seu propi text) | Treu d'un text els indicis d'IA: llistes negres per llengua (anglès, català, castellà), una auditoria d'adverbis, construccions formulàries, prosa amanerada. Només resta. |
| `/throat-clearing-review` | [throat-clearing-review.md](throat-clearing-review.md) | writer informa, reviewer qualifica | Ajustament per etapes d'un document que s'ha de publicar, en quatre passades: formulació, paràgrafs redundants, taules i figures, farciment a nivell de frase. Primer l'informe; no s'edita res fins que el principal decideix. |
| `/korben-dallas` | [korben-dallas.md](korben-dallas.md) | qualsevol, només si es demana | Comprimeix la resposta, no la feina: el veredicte primer, dos paràgrafs curts com a màxim. Només al xat; els fitxers es queden sencers. |

> [!todo] Tu
> A mesura que afegeixis legati amb skills pròpies (una actualització de comunicacions, una llista de comprovació de revisor per al teu camp), afegeix-hi files i posa la skill al `boot.md` d'aquell legatus.
