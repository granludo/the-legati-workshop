# /playwright: dona a un agent un navegador real

El patró establert per a qualsevol tasca de navegador que vagi més enllà d'una sola lectura. Llegeix-la quan tu (qualsevol agent) necessitis carregar una pàgina generada amb JS, superar un bloqueig antibots, conduir un flux de diversos passos o capturar una pantalla o un PDF, i `WebFetch` no n'hi hagi prou.

Aquesta skill és la capa de **com aconseguir un navegador**. La regla que la governa és el codi com a acció: escriu un script i conserva'l. El navegador és d'un sol ús; l'script és el bé durador.

## Primera decisió: de debò necessites Playwright?

| Forma de la tasca | Què fer servir | Per què |
|---|---|---|
| Llegir una pàgina pública i estàtica; extreure'n una cosa | **`WebFetch`** | El més barat, dins el context. L'opció per defecte. |
| GitHub (issues, PR, versions) | **CLI `gh`** | Mai `WebFetch` contra github.com. |
| Gmail / Calendar / Drive | **una CLI de Workspace** (carril de l'agent comms) | Amb àmbit OAuth, no un navegador. |
| Moodle / LMS | **l'API de serveis web del LMS** | Fes servir el punt d'accés WS, no un navegador. |
| **Generada amb JS / diversos passos / amb estat / bloqueig antibots / captura com a lliurable** | **Playwright** (aquesta skill) | Quan les opcions anteriors no hi arriben. |

Si `WebFetch` torna una carcassa buida, una paret d'inici de sessió o un `403`, és el senyal per passar a Playwright.

## Dues maneres de fer servir Playwright aquí: tria segons si es repetirà

**Mode A: script de biblioteca (codi com a acció). És l'opció per defecte per a tot el que es repetirà.**
Escriu un script petit `.mjs` (o Python) amb la biblioteca `playwright`, fes-ne commit a `tools/<task-slug>/`, i torna'l a executar o fes-ne una variant la propera vegada. El navegador és d'un sol ús; **l'script és el bé durador**.

- Crea un directori `tools/<task-slug>/` amb l'script, un `package.json` i un README breu; fes que git ignori `node_modules/` i qualsevol `outputs/`.
- Parteix d'un exemple que funciona: [`tools/refs-check/verify-urls.mjs`](../tools/refs-check/verify-urls.mjs), en Node/`.mjs`, carrega una llista d'URL, registra l'estat HTTP i el títol de la pàgina, i modifica un fitxer markdown. Una bona plantilla per a «carregar N URL, extreure'n un camp de cadascuna i escriure'n els resultats».

**Mode B: `@playwright/cli` per a exploracions interactives puntuals.**
Quan només has de tafanejar una pàgina una vegada (fer-ne una instantània, llegir-ne un valor, fer una captura) i no hi ha res que valgui la pena conservar, la CLI és més ràpida que escriure un script: `npx --yes @playwright/cli@latest <command>`. Regla de tokens: millor `snapshot` que bolcar el DOM amb `eval`.

**No** condueixis el navegador pas a pas des del xat («ara clica això, ara desplaça't»). Si la tasca té més de ~2 passos, és el mode A: escriu l'script.

## Configuració inicial de la màquina (una sola vegada)

Per a un directori d'eina nou:
```bash
cd tools/<task-slug>/
npm install playwright                  # local dep; add node_modules/ to .gitignore
npx playwright install chromium         # ~150 MB, one-time per host, reused after
```
Per al mode B: `npx --yes @playwright/cli@latest <command>`, sense instal·lació; es desa a la memòria cau la primera vegada.

**Avisa l'usuari de la descàrrega per endavant.** El primer aprovisionament de navegador en una màquina nova baixa de ~150 MB (només Chromium) a ~500 MB (tots els motors). Digues-ho a l'usuari abans de començar, com amb qualsevol instal·lació llarga.

## Paranys apresos a la pràctica

- **Un navegador real de vegades també topa amb bloquejos antibots.** Els servidors darrere de Cloudflare tornen una pàgina intersticial `403` (`"Just a moment…"` / `"Access Denied"`) fins i tot a un Chromium headless amb un User-Agent correcte. Quan passa, l'URL és darrere d'un repte dur: no ho prenguis com a prova que el recurs és fals; passa-ho a una persona perquè hi faci clic.
- **Posa un User-Agent realista + `Accept-Language`.** El UA per defecte de Playwright es rebutja més sovint. Fes servir un bloc `newContext({ userAgent, extraHTTPHeaders })`.
- **`waitUntil: 'domcontentloaded'`** sol ser suficient i és molt més ràpid que `networkidle` per a comprovacions del tipus «s'ha carregat aquesta pàgina i quin títol té».
- **Els scripts de verificació només han de millorar l'evidència, mai esborrar un positiu anterior.** Una comprovació de navegador que falla (bloqueig o temps esgotat) és indeterminada, no negativa: conserva el veredicte que ja tenies. Només una evidència nova positiva (la pàgina s'ha carregat, el contingut coincideix) ha de canviar un veredicte.
- **L'autenticació es queda fora de git.** Inicia sessió només amb les credencials que l'usuari proporcioni per a aquell script (entorn / `.env`). No desis mai galetes ni sessions al repositori. Els fluxos amb 2FA tornen a l'usuari.

## Nota de portabilitat

Aquesta skill és markdown pla i s'invoca en llenguatge natural («fes servir Playwright per carregar…»), sense cap mecanisme propi d'una bastida concreta. La capa duradora és: aquesta skill + els scripts versionats + `package.json`. `node_modules/` i els binaris dels navegadors són locals de cada màquina i es tornen a aprovisionar amb `npm install`. Qualsevol bastida d'agents que pugui executar `node`/`npx` els fa córrer sense canvis.

## Relacionat

- [`tools/refs-check/verify-urls.mjs`](../tools/refs-check/verify-urls.mjs): l'exemple resolt del mode A.

---

La invocació canònica és en llenguatge natural; `/playwright` és la drecera curta.
