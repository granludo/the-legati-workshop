# /throat-clearing-review: troba la prosa que s'anuncia en lloc de parlar

Revisió a dos legati d'un document que s'ha de publicar: **l'escriptor detecta i
proposa reescriptures, el revisor en qualifica la gravetat, i el document d'origen
no es toca mai.** El resultat és un informe que el principal llegeix amb un veredicte
enganxat a cada troballa, perquè pugui aplicar, adaptar o rebutjar cadascuna amb el
bolígraf a la mà.

**Invocació:** *«Escriptor, revisió d'escurada de gola de `<file>`»* o
`/throat-clearing-review <file>`. S'activa quan el principal ho demana, no
automàticament.

**Origen (2026-08-09).** Al taller original, l'autor, llegint les proves d'un
article, va topar amb aquest paràgraf:

> "The mechanism behind that sensitivity is worth naming, because it applies to
> anyone computing this quantity. […] That is an argument for repetition, and
> for treating a configuration failure as a run that has not happened yet rather
> than as a result."

La reacció, *"If we need to say 'when a run failed due to an error in the setup we
fixed it and repeated the run', say that"*, és tota la skill. La primera execució
va produir un informe de formulació amb 25 troballes, 2 de les quals eren errors
factuals que l'escombrada d'estil va fer sortir a la llum.

---

## La prova

Per a cada frase: **podria dir què va passar, amb un verb, d'una sola tirada?**
Si la frase endarrereix un fet, decora un fet o es posa nota a si mateixa per com
lliura un fet, és una troballa.

## La taxonomia de faltes

1. **Escurada de gola**: anunciar que s'està a punt de dir una cosa en lloc de
   dir-la. Senyals característics: *"X is worth naming, because…"*, *"worth drawing
   out"*, *"worth reading carefully"*, *"worth being exact about which"*,
   *"worth separating because"*, *"What makes this worth reporting is…"*,
   *"The striking feature of this table is…"*. L'arranjament gairebé sempre és
   esborrar l'anunci: el contingut que ve després ja feia la feina.

2. **Evasió el·líptica**: un fet senzill disfressat d'aforisme, de manera que el
   lector ha de desxifrar el que es podria haver dit. Senyals de la primera execució:
   *"a run that has not happened yet rather than as a result"* (= vam arreglar la
   configuració i la vam tornar a executar), *"not a failed measurement but an absent one"*,
   *"the ledger will empty on its own"*, *"promote that from reading to
   finding"*, *"sent us back to the machine"*. L'arranjament és la regla del pa i el vi:
   al pa, pa, i al vi, vi, i dir el fet.

3. **Metacomentari**: el document narra la seva pròpia retòrica o la seva pròpia
   producció en lloc del tema. Senyals: *"and we state it as such"*,
   *"we state it narrowly"*, *"we note it rather than build on it"*, i el subtipus
   pitjor, la **filtració de l'historial de redacció**: text adreçat a "a reader who
   later meets an earlier draft" en un mitjà on només existeix el text final.
   Relacionats: els **verbs sense agent** ("the findings publish regardless of
   direction": les troballes no es publiquen soles, les publiquem nosaltres) i les
   **construccions que alliçonen el lector** ("A reader who takes X as Y will be
   misled, and so will one who…").

## Què NO és una falta: protegeix-ho

- **Aforismes guanyats.** Un document pot conservar les seves dues o tres millors frases
  encara que siguin retòriques: *"an instrument of this kind does not fail by
  crashing, it fails by returning a number one would have believed"* va sobreviure a
  la primera execució perquè enuncia el risc central de l'article, una sola vegada, allà
  on l'incident se l'havia guanyat. La qualificació Keep existeix perquè netejar de més
  sigui un error qualificat, no una virtut.
- **Senyalització que porta informació.** *"Two conclusions follow, and they
  are separable"* diu al lector que pot acceptar l'una sense l'altra. Es conserva.
- **Cauteles científiques que delimiten una afirmació** ("on these data", "we report it as
  observations on one model"). Delimitar l'abast és contingut, no escurada de gola.

## El circuit: quatre passos, aplicats d'un en un

La revisió va **per etapes**. Cada pas produeix un informe o una llista numerada,
el principal en decideix, s'aplica la decisió, i només llavors comença el pas
següent. **Després d'aplicar cada pas, proposa el següent i explica en una línia
en què consisteix.** No facis mai dos passos en una sola passada: cada pas llegeix
el document tal com l'ha deixat el pas anterior.

Tots els passos segueixen el mateix contracte: **primer l'informe, no s'edita res fins
que el principal decideix.** Les decisions s'apliquen a una nova versió menor (v10.2, v10.3, …)
i al fitxer de publicació en la mateixa passada, verificades i renderitzades de nou.

### Pas 1: passada de formulació (escurada de gola, el·lipsi, metacomentari)

L'escriptor llegeix el document de cap a cap, en ordre (res de passades només amb grep),
i informa de cada troballa: **ubicació, cita literal completa, falta identificada,
reescriptura amb la veu del principal**, a `<stem>-phrasing-report.md`, al costat del
document d'origen. El revisor qualifica cada troballa al mateix fitxer: **Blocker / Major / Minor / Polish /
Keep**, amb un recompte i un veredicte. La qualificació Keep és un calibratge obligatori:
un document conserva els seus dos o tres aforismes guanyats, i netejar de més és un error
qualificat. El principal decideix editant el mateix informe (canviar un veredicte a Keep
és una decisió); «aplica-ho tot» vol dir aplicar tot el que no estigui marcat com a Keep.

### Pas 2: passada de redundància de paràgrafs

Relectura completa amb una pregunta per paràgraf: *si això desaparegués, desapareixeria
amb ell alguna afirmació, xifra o advertiment?* Proposa ~10 paràgrafs sencers que es
puguin treure sense perdre res o millorant l'article, **com a llista numerada al xat
amb el text complet de cada paràgraf** i una justificació d'una línia (causes habituals:
una història explicada tres vegades, un senyal que apunta al paràgraf següent, un
advertiment que respon una pregunta que ningú no ha fet, una afirmació que ha quedat
desfasada). El principal decideix número per número. Quan una supressió deixa una frase
veïna sense antecedent, fes l'empalmament mínim i informa'n: l'empalmament forma part de
la supressió, no és una reescriptura.

### Pas 3: claredat de taules i figures (el revisor)

El revisor repassa **totes les taules i figures**: cada columna i cada dimensió estan
definides allà on mira el lector? Comprovacions fixes, apreses a la primera execució:
les columnes agregades que barregen models amb preus per token diferents ho han de dir
al peu; cada preu necessita una font declarada i una data de consulta **a l'article**,
no només al repositori; les referències creuades dels peus han d'apuntar a seccions que
continguin de debò el material referit; els recomptes dels peus es podreixen més de
pressa que els de les taules. Informa al xat amb les gravetats; cap edició fins que hi hagi decisió.

### Pas 4: passada de farciment a nivell de frase

El gra més fi: ~20 expressions dins dels paràgrafs que, **si es treuen, guanyen
claredat**: intensificadors buits (*remarkably*, *simply*, *duly*), frases d'anunci que
les passades anteriors no van veure (*"X deserves a note"*, *"The practical reading is
direct"*), hipòtesis escenificades (*"A reviewer may reasonably ask…"*), veredictes
repetits, cauteles que dilueixen el que s'està establint (*"is understood to
be"*) i cues decoratives després d'una idea ja completa. Llista numerada al xat amb cada
expressió dins de la seva frase i el que queda en treure-la. El principal decideix; aplica-ho.

### Cada pas també és una escombrada d'errors

A la primera execució, cadascun dels quatre passos va trobar errors factuals: un recompte
de bastides equivocat a la Discussió (pas 1), una afirmació que havia esdevingut falsa
després que canviessin les dades (pas 2), dos recomptes desfasats i una referència de preu
penjada als peus (pas 3), articles gramaticals mal posats i un altre recompte desfasat (pas 4).
**Les passades d'estil enxampen errors aritmètics perquè obliguen a rellegir frases que
ningú no ha mirat en setmanes.** Informa dels errors al costat de les troballes d'estil;
passen per davant de tot.

## Relació amb les passades existents

Aquest circuit és una capa diferent de `/unslop-text` (l'escombrada de tics de prosa).
L'escombrada de tics caça **vocabulari**: *delve*, *crucial*, *tapestry*. Aquest
circuit caça **jugades** (pas 1), **redundància** (passos 2 i 4) i
**dimensions no definides** (pas 3), que sobreviuen a qualsevol filtre de vocabulari
perquè cada paraula, per separat, és innocent. Fes primer l'escombrada de tics
(és barata) i després aquest circuit, en qualsevol text que s'hagi de publicar i on la prosa importi.

## Exemple resolt

La primera execució completa es va fer sobre l'esborrany d'arXiv d'un article de recerca (2026-08-09):
el pas 1 va produir 25 troballes (2 Blockers), el pas 2 va treure nou paràgrafs i va corregir
una afirmació falsa, el pas 3 va restaurar la procedència dels preus sobre la qual s'aguantaven
les columnes en dòlars, i el pas 4 va treure vint expressions i quatre errors. Balanç: dues
pàgines menys, cap xifra canviada, 60 comprovacions del verificador en verd de principi a fi.
