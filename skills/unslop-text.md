# /unslop-text — strip AI giveaways from a text

**Invoke:** `/unslop-text <file>` · *"Writer, unslop `<file>`"* · *"passa l'unslop a `<file>`"* · *"pásale el unslop a `<file>`"*
**Legatus:** the writer by default (it is a prose pass). Any legatus may run it on its own output before delivering.
**Origin:** the original workshop, 2026-08-30, during a book-chapter pass. A 12-item English list from the author is the seed; the per-language lists grow by accretion. Add your own words as you meet them.

## What it does

One pass over a text that removes the lexical fingerprints of AI-generated prose: unnecessary adverbs, throat-clearing, corporate filler, and the formulaic constructions every LLM overuses. It is a **subtractive** pass: it deletes and simplifies, it never adds content, never reorders paragraphs, never changes facts, numbers, quotes or verify marks.

Scope note: this is the *lexical* layer. The staged *structural* tightening pipeline (redundant paragraphs, tables, padding) is `/throat-clearing-review` — the two compose, unslop usually last.

## Procedure

1. Detect the text's language; load the matching blacklist section below. If the language has no section yet, say so and build the list with the principal before editing (then add the section here — that is how "one for each language" grows).
2. Sweep for the four families: (a) blacklisted words/phrases, (b) adverb audit, (c) formulaic constructions, (d) mannered prose (below; language-agnostic, catches what the blacklists have not learned yet).
3. For each hit, apply the **load-bearing test** (below). Delete or simplify what fails it; keep what passes, and be ready to defend each keep.
4. Apply mechanically with per-replacement asserts (python heredoc, `assert old in s` and uniqueness) so a stale anchor fails loudly instead of silently skipping.
5. Report in chat: count of removals by family, plus the deliberate keeps and why. Commit with the change families in the message.

## The load-bearing test

Delete a word or construction unless removing it loses **information or an argument**, not just emphasis. Worked examples from a Catalan book chapter (2026-08-30):

- **Kept:** «ignorarà *racionalment*» (the wordplay IS Christensen's thesis) · «ignorant *convenientment*» (the adverb is the accusation) · «dissenyat *deliberadament*» (design intent is the claim) · «es compartien *lliurement*» (thematic: software lliure) · «per raons estructurals, *no ideològiques*» (the contrast is the argument).
- **Cut:** «*genuïnament* descentralitzat» · «*notablement* consistent» · «va créixer *ràpidament*» (the next sentence gives the number) · «participaven *activament*» · «Era, *en essència*, …» · «*simplement* no tenien» · «*per cert*» mid-argument.

## Family (d): mannered prose — the test the blacklists generalise

Added 2026-09-02 from Anthropic's prompting guidance on prose style. The blacklists below catch words we have already met; this family catches the mechanism, so it works on words we have not met and in every language.

**Definition.** Mannered prose substitutes metaphor and flourish for direct statement. "A dial worth turning" for "a parameter worth varying"; "earns its keep" for "still matters"; "the ledger will empty on its own" for "the backlog will drain". The phrase exists to display the writer, not to convey the idea. It is also imprecise: the metaphor drags in connotations the writer did not choose.

**The test, per hit.** *Is a literal phrase available that says the same thing?* If yes, the metaphor is mannered: replace it with the literal phrase. If no literal phrase does the job in roughly the same space, the metaphor is doing analytical work and stays (this is the same load-bearing test, applied to micro-metaphors instead of adverbs). A calibration from a Catalan chapter: *"va saltar pels aires"* → *"va entrar en crisi"* (mannered, cut); *"tot per al poble, però sense el poble"* (no literal phrase carries the irony, kept).

**Exemption: the author's own metaphors stay.** The test applies to generated prose. A figure the principal wrote is not a hit: report it in the diff summary if it looks mannered, do not replace it. They rule. When provenance is unclear, `git blame` or `git log -p` on the paragraph settles it before the pass touches it.

**Where to look.** Verbs first (the heightened verb is the commonest form: *soar, shatter, unravel, bleed, carve out, weather*, and the CA/ES *saltar pels aires, fer miques, teixir, navegar*), then sentence closers (the flourish clusters where a paragraph ends), then anything that would sound like a keynote line if read aloud.

**Prompt use.** When asking any model for a rewrite, the definition paragraph above pasted into the user message works better than a blacklist, and the short form *"remove all mannered prose"* also works.

## Language: English (the seed list — the original 12)

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

Additions by accretion: "leverage" (verb), "landscape" (metaphorical), "navigate" (metaphorical), "unpack", "foster", "underscore", "testament to", "a rich …", "in today's …", "It's worth noting that", "Interestingly,", "dive deep", "game-changer", "at the end of the day", "moreover/furthermore" chains, triads-for-rhythm ("clear, concise, and compelling").

## Language: Catalan

**Throat-clearing / filler:** «cal destacar que», «val a dir que», «és important assenyalar», «en aquest sentit», «per cert» (mid-argument), «en essència», «en molts sentits», «en certa mesura», «en definitiva» (as paragraph opener), «dit d'una altra manera» (when nothing is re-said), «com veurem» (call-forwards).

**Inflated vocabulary (the «delve» family):** «aprofundir en» / «endinsar-nos en» (as topic-opener), «crucial», «cabdal» (when everything is cabdal), «pivotal», «tapís», «teixit» (metaphorical), «paisatge» (metaphorical), «navegar» (metaphorical), «robust» (outside engineering), «fluid/seamless», «àmbit/reialme» chains, «posar en relleu», «palanquejar».

**Adverb audit (the -ment sweep):** grep `[a-zà-ú]ment\b` and test each: «genuïnament», «notablement», «ràpidament», «activament», «massivament», «silenciosament», «radicalment», «simplement», «literalment», «òbviament», «certament», «precisament/exactament» when decorative (they often ARE load-bearing in a paradox — test, don't purge). Ration «simultàniament» to the one place simultaneity is the claim; elsewhere «alhora».

**Formulaic constructions:** «No és X, és Y» / «no era X: era Y» — *careful*: paradox-then-resolution can be an author's own tool, so the rule is **ration, and the contrast must carry information, not drama**. One per section is seasoning; three per page is slop. Also: false ranges («des de X fins a Y» listing everything), triads-for-rhythm, «tant… com…» chains, «una mena de» hedging.

**Known false friend:** «eventualment» → «amb el temps» (in Catalan «eventualment» means «per casualitat», not «finalment»).

## Language: Spanish

**Throat-clearing / filler:** «cabe destacar que», «es importante señalar», «en este sentido», «dicho esto», «en esencia», «en cierta medida», «a fin de cuentas» (opener), «como veremos».

**Inflated vocabulary:** «profundizar en» / «adentrarnos en» (topic-opener), «crucial», «fundamental» (when serial), «tapiz», «tejido» (metaphorical), «paisaje» (metaphorical), «navegar» (metaphorical), «robusto» (outside engineering), «fluido/sin fisuras», «poner de relieve», «apalancar».

**Adverb audit:** the -mente sweep: «genuinamente», «notablemente», «rápidamente», «activamente», «masivamente», «silenciosamente», «radicalmente», «simplemente», «literalmente», «obviamente», «ciertamente», «precisamente/exactamente» when decorative. Spanish tolerates -mente chains even worse than Catalan: never two in one sentence.

**Formulaic constructions:** «No es X, es Y» — same rationing rule as Catalan. «no solo… sino también» chains, triads-for-rhythm, «una suerte de» hedging.

## Hard limits

- Never touch quotes, verify marks `==(...)==`, callouts' content semantics, code spans, or figure captions' factual text.
- Never "fix" the author's voice markers: if the principal wrote it, flag it in the report instead of editing (their call).
- Editorial rules of the active project still bind (for example: no em-dashes, no call-forwards, notes to the author as callouts).
- The pass is per-file and committed separately, so the diff IS the report.
