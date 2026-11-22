# /unslop-text: quitar de un texto lo que delata a la IA

**Invocación:** `/unslop-text <file>` · «Writer, unslop `<file>`» · «passa l'unslop a `<file>`» · «pásale el unslop a `<file>`»
**Legatus:** el escritor (`writer`) por defecto (es una pasada de prosa). Cualquier legatus puede ejecutarla sobre lo que produce él mismo antes de entregarlo.
**Origen:** el taller original, 2026-08-30, durante una pasada sobre un capítulo de libro. La semilla es una lista en inglés de 12 elementos que hizo el autor; las listas de cada lengua crecen por acumulación. Añade tus propias palabras a medida que te las encuentres.

## Qué hace

Una pasada sobre un texto que elimina las huellas léxicas de la prosa generada por IA: adverbios innecesarios, carraspeo, relleno corporativo y las construcciones formulaicas de las que abusan todos los LLM. Es una pasada **sustractiva**: borra y simplifica; nunca añade contenido, nunca reordena párrafos, nunca cambia hechos, números, citas ni marcas de verificación.

Nota de alcance: esta es la capa léxica. La cadena de ajuste estructural por etapas (párrafos redundantes, tablas, relleno) es `/throat-clearing-review`; las dos se combinan, y el unslop suele ir al final.

## Procedimiento

1. Detecta la lengua del texto; carga la sección de lista negra que le corresponda, más abajo. Si la lengua todavía no tiene sección, dilo y construye la lista con el principal antes de editar (luego añade la sección aquí: así es como crece lo de «una para cada lengua»).
2. Barre el texto en busca de las cuatro familias: (a) palabras y expresiones de la lista negra, (b) auditoría de adverbios, (c) construcciones formulaicas, (d) prosa amanerada (más abajo; no depende de la lengua y caza lo que las listas negras todavía no han aprendido).
3. Para cada caso, aplica la **prueba de carga** (más abajo). Borra o simplifica lo que no la pase; conserva lo que la pase, y prepárate para defender cada cosa que conserves.
4. Aplica los cambios de forma mecánica, con asserts en cada sustitución (heredoc de python, `assert old in s` y unicidad), para que un ancla desfasada falle de forma ruidosa en lugar de saltarse en silencio.
5. Informa en el chat: número de eliminaciones por familia, más lo que has conservado a propósito y por qué. Haz commit con las familias de cambios en el mensaje.

## La prueba de carga

Borra una palabra o una construcción salvo que quitarla haga perder **información o un argumento**, no solo énfasis. Ejemplos de un capítulo de libro en catalán (2026-08-30):

- **Se conservan:** «ignorarà *racionalment*» (el juego de palabras ES la tesis de Christensen) · «ignorant *convenientment*» (el adverbio es la acusación) · «dissenyat *deliberadament*» (la intención de diseño es lo que se afirma) · «es compartien *lliurement*» (es el tema: software lliure) · «per raons estructurals, *no ideològiques*» (el contraste es el argumento).
- **Se cortan:** «*genuïnament* descentralitzat» · «*notablement* consistent» · «va créixer *ràpidament*» (la frase siguiente da el número) · «participaven *activament*» · «Era, *en essència*, …» · «*simplement* no tenien» · «*per cert*» en mitad del argumento.

## Familia (d): prosa amanerada, la prueba que generaliza las listas negras

Añadida el 2026-09-02 a partir de las pautas de Anthropic sobre el estilo de la prosa. Las listas negras de abajo cazan palabras que ya nos hemos encontrado; esta familia caza el mecanismo, así que funciona con palabras que todavía no hemos visto y en cualquier lengua.

**Definición.** La prosa amanerada sustituye la afirmación directa por la metáfora y el adorno. «A dial worth turning» en lugar de «a parameter worth varying»; «earns its keep» en lugar de «still matters»; «the ledger will empty on its own» en lugar de «the backlog will drain». La expresión existe para lucir a quien escribe, no para transmitir la idea. Además es imprecisa: la metáfora arrastra connotaciones que el autor no ha elegido.

**La prueba, caso por caso.** ¿Hay una expresión literal que diga lo mismo? Si la hay, la metáfora es amanerada: sustitúyela por la expresión literal. Si ninguna expresión literal hace el mismo trabajo en más o menos el mismo espacio, la metáfora está haciendo trabajo analítico y se queda (es la misma prueba de carga, aplicada a las micrometáforas en lugar de a los adverbios). Una calibración de un capítulo en catalán: «va saltar pels aires» → «va entrar en crisi» (amanerada, se corta); «tot per al poble, però sense el poble» (ninguna expresión literal transmite la ironía: se conserva).

**Excepción: las metáforas del propio autor se quedan.** La prueba se aplica a la prosa generada. Una figura que escribió el principal no es un caso: menciónala en el resumen del diff si parece amanerada, pero no la sustituyas. Decide el principal. Cuando no está claro de dónde viene, un `git blame` o un `git log -p` sobre el párrafo lo aclara antes de que la pasada lo toque.

**Dónde mirar.** Primero los verbos (el verbo exaltado es la forma más común: *soar, shatter, unravel, bleed, carve out, weather*, y en CA/ES *saltar pels aires, fer miques, teixir, navegar*), luego los cierres de frase (el adorno se acumula donde termina un párrafo) y luego todo lo que sonaría a frase de conferencia magistral si se leyera en voz alta.

**Uso en prompts.** Cuando le pidas una reescritura a cualquier modelo, el párrafo de definición de arriba, pegado en el mensaje del usuario, funciona mejor que una lista negra, y la versión corta «remove all mannered prose» también funciona.

## Lengua: inglés (la lista semilla, los 12 originales)

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

Añadidos por acumulación: "leverage" (como verbo), "landscape" (metafórico), "navigate" (metafórico), "unpack", "foster", "underscore", "testament to", "a rich …", "in today's …", "It's worth noting that", "Interestingly,", "dive deep", "game-changer", "at the end of the day", cadenas de "moreover/furthermore", tríadas por ritmo ("clear, concise, and compelling").

## Lengua: catalán

**Carraspeo / relleno:** «cal destacar que», «val a dir que», «és important assenyalar», «en aquest sentit», «per cert» (en mitad del argumento), «en essència», «en molts sentits», «en certa mesura», «en definitiva» (para abrir párrafo), «dit d'una altra manera» (cuando no se vuelve a decir nada), «com veurem» (anuncios de lo que vendrá).

**Vocabulario inflado (la familia de «delve»):** «aprofundir en» / «endinsar-nos en» (para abrir tema), «crucial», «cabdal» (cuando todo es cabdal), «pivotal», «tapís», «teixit» (metafórico), «paisatge» (metafórico), «navegar» (metafórico), «robust» (fuera de la ingeniería), «fluid/seamless», cadenas de «àmbit/reialme», «posar en relleu», «palanquejar».

**Auditoría de adverbios (el barrido de -ment):** haz grep de `[a-zà-ú]ment\b` y pon a prueba cada uno: «genuïnament», «notablement», «ràpidament», «activament», «massivament», «silenciosament», «radicalment», «simplement», «literalment», «òbviament», «certament», «precisament/exactament» cuando son decorativos (en una paradoja a menudo SÍ cargan peso: ponlos a prueba, no los purgues). Reserva «simultàniament» para el único sitio donde la simultaneidad es lo que se afirma; en el resto, «alhora».

**Construcciones formulaicas:** «No és X, és Y» / «no era X: era Y». **Cuidado:** la paradoja seguida de su resolución puede ser una herramienta del propio autor, así que la regla es **racionar, y el contraste tiene que aportar información, no dramatismo**. Una por sección es condimento; tres por página es slop. También: los falsos rangos («des de X fins a Y» para enumerarlo todo), las tríadas por ritmo, las cadenas de «tant… com…», el «una mena de» como cautela.

**Falso amigo conocido:** «eventualment» → «amb el temps» (en catalán, «eventualment» quiere decir «per casualitat», no «finalment»).

## Lengua: castellano

**Carraspeo / relleno:** «cabe destacar que», «es importante señalar», «en este sentido», «dicho esto», «en esencia», «en cierta medida», «a fin de cuentas» (para abrir), «como veremos».

**Vocabulario inflado:** «profundizar en» / «adentrarnos en» (para abrir tema), «crucial», «fundamental» (en serie), «tapiz», «tejido» (metafórico), «paisaje» (metafórico), «navegar» (metafórico), «robusto» (fuera de la ingeniería), «fluido/sin fisuras», «poner de relieve», «apalancar».

**Auditoría de adverbios:** el barrido de -mente: «genuinamente», «notablemente», «rápidamente», «activamente», «masivamente», «silenciosamente», «radicalmente», «simplemente», «literalmente», «obviamente», «ciertamente», «precisamente/exactamente» cuando son decorativos. El castellano tolera las cadenas de -mente todavía peor que el catalán: nunca dos en la misma frase.

**Construcciones formulaicas:** «No es X, es Y», con la misma regla de racionamiento que en catalán. Las cadenas de «no solo… sino también», las tríadas por ritmo, el «una suerte de» como cautela.

## Límites estrictos

- No toques nunca las citas, las marcas de verificación `==(...)==`, el sentido del contenido de los callouts, los fragmentos de código ni el texto factual de los pies de figura.
- No «arregles» nunca las marcas de voz del autor: si lo escribió el principal, señálalo en el informe en lugar de editarlo (la decisión es suya).
- Las reglas editoriales del proyecto activo siguen vigentes (por ejemplo: nada de rayas, nada de anuncios de lo que vendrá, las notas al autor como callouts).
- La pasada se hace fichero a fichero y con su propio commit, así que el diff ES el informe.
