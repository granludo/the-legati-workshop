# /unslop-text: treu d'un text els indicis d'IA

**Invocació:** `/unslop-text <file>` · *"Writer, unslop `<file>`"* · *"passa l'unslop a `<file>`"* · *"pásale el unslop a `<file>`"*
**Legatus:** l'escriptor (`writer`) per defecte (és una passada de prosa). Qualsevol legatus la pot executar sobre el seu propi text abans de lliurar-lo.
**Origen:** el taller original, 2026-08-30, durant una passada sobre un capítol de llibre. La llavor és una llista de 12 elements en anglès de l'autor; les llistes de cada llengua creixen per acumulació. Afegeix-hi les teves paraules a mesura que te les trobis.

## Què fa

Una passada sobre un text que n'elimina les empremtes lèxiques de la prosa generada per IA: adverbis innecessaris, escurades de gola, farciment corporatiu i les construccions formulàries que tots els LLM fan servir massa. És una passada **subtractiva**: esborra i simplifica, no afegeix mai contingut, no reordena mai paràgrafs, no canvia mai fets, xifres, cites ni marques de verificació.

Nota d'abast: aquesta és la capa *lèxica*. El circuit per etapes d'ajustament *estructural* (paràgrafs redundants, taules, farciment) és `/throat-clearing-review`. Totes dues es combinen, i l'unslop sol anar al final.

## Procediment

1. Detecta la llengua del text i carrega la secció de llista negra corresponent de més avall. Si la llengua encara no en té, digues-ho i construeix la llista amb el principal abans d'editar (després afegeix-ne la secció aquí: així és com creix «una per a cada llengua»).
2. Fes l'escombrada de les quatre famílies: (a) paraules o expressions de la llista negra, (b) auditoria d'adverbis, (c) construccions formulàries, (d) prosa amanerada (més avall; independent de la llengua, caça el que les llistes negres encara no han après).
3. Per a cada coincidència, aplica la **prova de càrrega** (més avall). Esborra o simplifica el que no la passa; conserva el que la passa, i estigues a punt per defensar cada cosa que conserves.
4. Aplica-ho de manera mecànica, amb un assert per substitució (heredoc de Python, `assert old in s` i unicitat), perquè una àncora desfasada falli fent soroll en lloc de saltar-se en silenci.
5. Informa al xat: nombre d'eliminacions per família, més el que has conservat a consciència i per què. Fes commit amb les famílies de canvis al missatge.

## La prova de càrrega

Esborra una paraula o una construcció tret que treure-la faci perdre **informació o un argument**, no només èmfasi. Exemples resolts d'un capítol de llibre en català (2026-08-30):

- **Conservats:** «ignorarà *racionalment*» (el joc de paraules ÉS la tesi de Christensen) · «ignorant *convenientment*» (l'adverbi és l'acusació) · «dissenyat *deliberadament*» (la intenció de disseny és l'afirmació) · «es compartien *lliurement*» (temàtic: software lliure) · «per raons estructurals, *no ideològiques*» (el contrast és l'argument).
- **Tallats:** «*genuïnament* descentralitzat» · «*notablement* consistent» · «va créixer *ràpidament*» (la frase següent dona la xifra) · «participaven *activament*» · «Era, *en essència*, …» · «*simplement* no tenien» · «*per cert*» enmig de l'argument.

## Família (d): prosa amanerada, la prova que generalitza les llistes negres

Afegida el 2026-09-02 a partir de la guia de prompting d'Anthropic sobre l'estil de la prosa. Les llistes negres de més avall cacen paraules que ja hem trobat; aquesta família caça el mecanisme, i per això funciona amb paraules que encara no hem trobat i en qualsevol llengua.

**Definició.** La prosa amanerada substitueix l'afirmació directa per la metàfora i la floritura. "A dial worth turning" en lloc de "a parameter worth varying"; "earns its keep" en lloc de "still matters"; "the ledger will empty on its own" en lloc de "the backlog will drain". L'expressió hi és per lluir l'escriptor, no per transmetre la idea. A més, és imprecisa: la metàfora arrossega connotacions que l'escriptor no ha triat.

**La prova, per a cada coincidència.** *Hi ha una expressió literal que digui el mateix?* Si n'hi ha, la metàfora és amanerada: substitueix-la per l'expressió literal. Si cap expressió literal no fa la feina en un espai semblant, la metàfora fa feina analítica i es queda (és la mateixa prova de càrrega, aplicada a micrometàfores en lloc d'adverbis). Un calibratge d'un capítol en català: *"va saltar pels aires"* → *"va entrar en crisi"* (amanerada, tallada); *"tot per al poble, però sense el poble"* (cap expressió literal no porta la ironia, conservada).

**Excepció: les metàfores de l'autor es queden.** La prova s'aplica a la prosa generada. Una figura que ha escrit el principal no és una coincidència: si sembla amanerada, esmenta-la al resum del diff, però no la substitueixis. Decideix el principal. Quan l'origen no és clar, un `git blame` o un `git log -p` sobre el paràgraf ho resol abans que la passada el toqui.

**On mirar.** Primer els verbs (el verb inflat és la forma més comuna: *soar, shatter, unravel, bleed, carve out, weather*, i els CA/ES *saltar pels aires, fer miques, teixir, navegar*), després els finals de frase (la floritura s'acumula on acaba un paràgraf) i després qualsevol cosa que, llegida en veu alta, sonaria com una frase de conferència inaugural.

**Ús en un prompt.** Quan demanis una reescriptura a qualsevol model, enganxar el paràgraf de definició de més amunt al missatge de l'usuari funciona millor que una llista negra, i la forma curta *"remove all mannered prose"* també funciona.

## Llengua: anglès (la llista llavor, els 12 originals)

1. **"Delve."** You've never said it out loud. Once.
2. **"Crucial / pivotal."** Nothing is that pivotal.
3. **"Tapestry."** No human speaks like this.
4. **"Here's the thing."** There is no thing.
5. **"Hope this helps."** It doesn't. It outs you.
6. **"After careful consideration."** Without considering.
7. **"To provide a quick update."** Just give the update.
8. **"Most people…"** The lazy oversimplification.
9. **"Robust / seamless / realm."** The corporate AI.
10. **Adverb abuse.** "X quietly runs Y." Nothing runs quietly.
11. **"It's not X, it's Y."** The famous AI sentence, alive.
12. **"This isn't a budget. It's a statement of intent."** No.

Afegits per acumulació: "leverage" (verb), "landscape" (metaphorical), "navigate" (metaphorical), "unpack", "foster", "underscore", "testament to", "a rich …", "in today's …", "It's worth noting that", "Interestingly,", "dive deep", "game-changer", "at the end of the day", "moreover/furthermore" chains, triads-for-rhythm ("clear, concise, and compelling").

## Llengua: català

**Escurada de gola / farciment:** «cal destacar que», «val a dir que», «és important assenyalar», «en aquest sentit», «per cert» (enmig de l'argument), «en essència», «en molts sentits», «en certa mesura», «en definitiva» (per obrir paràgraf), «dit d'una altra manera» (quan no es torna a dir res), «com veurem» (anuncis del que vindrà).

**Vocabulari inflat (la família de «delve»):** «aprofundir en» / «endinsar-nos en» (per obrir un tema), «crucial», «cabdal» (quan tot és cabdal), «pivotal», «tapís», «teixit» (metafòric), «paisatge» (metafòric), «navegar» (metafòric), «robust» (fora de l'enginyeria), «fluid/seamless», cadenes «àmbit/reialme», «posar en relleu», «palanquejar».

**Auditoria d'adverbis (l'escombrada de -ment):** fes grep de `[a-zà-ú]ment\b` i prova'ls un per un: «genuïnament», «notablement», «ràpidament», «activament», «massivament», «silenciosament», «radicalment», «simplement», «literalment», «òbviament», «certament», «precisament/exactament» quan són decoratius (en una paradoxa sovint SÍ que aguanten pes: prova'ls, no els purguis). Raciona «simultàniament» a l'únic lloc on la simultaneïtat és l'afirmació; a la resta, «alhora».

**Construccions formulàries:** «No és X, és Y» / «no era X: era Y». *Compte*: la paradoxa seguida de resolució pot ser una eina pròpia de l'autor, així que la regla és **racionar, i el contrast ha de portar informació, no dramatisme**. Una per secció és condiment; tres per pàgina és slop. També: falsos intervals («des de X fins a Y» per enumerar-ho tot), tríades per fer ritme, cadenes «tant… com…», «una mena de» com a cautela.

**Fals amic conegut:** «eventualment» → «amb el temps» (en català «eventualment» vol dir «per casualitat», no «finalment»).

## Llengua: castellà

**Escurada de gola / farciment:** «cabe destacar que», «es importante señalar», «en este sentido», «dicho esto», «en esencia», «en cierta medida», «a fin de cuentas» (per obrir), «como veremos».

**Vocabulari inflat:** «profundizar en» / «adentrarnos en» (per obrir un tema), «crucial», «fundamental» (en sèrie), «tapiz», «tejido» (metafòric), «paisaje» (metafòric), «navegar» (metafòric), «robusto» (fora de l'enginyeria), «fluido/sin fisuras», «poner de relieve», «apalancar».

**Auditoria d'adverbis:** l'escombrada de -mente: «genuinamente», «notablemente», «rápidamente», «activamente», «masivamente», «silenciosamente», «radicalmente», «simplemente», «literalmente», «obviamente», «ciertamente», «precisamente/exactamente» quan són decoratius. El castellà tolera les cadenes de -mente encara pitjor que el català: mai dos en una frase.

**Construccions formulàries:** «No es X, es Y», amb la mateixa regla de racionament que en català. Cadenes «no solo… sino también», tríades per fer ritme, «una suerte de» com a cautela.

## Límits estrictes

- No toquis mai les cites, les marques de verificació `==(...)==`, la semàntica del contingut dels callouts, els fragments de codi ni el text factual dels peus de figura.
- No «arreglis» mai les marques de veu de l'autor: si ho ha escrit el principal, assenyala-ho a l'informe en lloc d'editar-ho (la decisió és seva).
- Les regles editorials del projecte actiu continuen vigents (per exemple: cap guió llarg, cap anunci del que vindrà, notes a l'autor com a callouts).
- La passada es fa fitxer per fitxer i amb commits separats, de manera que el diff ÉS l'informe.
