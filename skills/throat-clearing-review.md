# /throat-clearing-review — find the prose that announces itself instead of speaking

Two-legatus review of a release-bound document: **the writer detects and
proposes rewrites, the reviewer grades severity, the source document is never
altered.** The output is a report the principal reads with a verdict attached to
every finding, so they can apply, adapt or reject each one with the pen in hand.

**Invoke:** *"Writer, throat-clearing review on `<file>`"* or
`/throat-clearing-review <file>`. Fires on the principal's request, not
automatically.

**Origin (2026-08-09).** In the original workshop, the author, reading the
proof of a paper, hit this paragraph:

> "The mechanism behind that sensitivity is worth naming, because it applies to
> anyone computing this quantity. […] That is an argument for repetition, and
> for treating a configuration failure as a run that has not happened yet rather
> than as a result."

The reaction — *"If we need to say 'when a run failed due to an error in the
setup we fixed it and repeated the run', say that"* — is the whole skill. The
first execution produced a phrasing report with 25 findings, 2 of them factual
errors the style sweep flushed out.

---

## The test

For every sentence: **could it say what happened, with a verb, in one pass?**
If the sentence delays a fact, decorates a fact, or grades its own delivery of
a fact, it is a finding.

## The offense taxonomy

1. **Throat-clearing** — announcing that something is about to be said instead
   of saying it. Signatures: *"X is worth naming, because…"*, *"worth drawing
   out"*, *"worth reading carefully"*, *"worth being exact about which"*,
   *"worth separating because"*, *"What makes this worth reporting is…"*,
   *"The striking feature of this table is…"*. The fix is almost always
   deletion of the announcement — the substance that follows was already doing
   the job.

2. **Elliptical evasion** — a plain fact dressed as an aphorism, so the reader
   must decode what could have been stated. Signatures from the first run:
   *"a run that has not happened yet rather than as a result"* (= we fixed the
   config and re-ran it), *"not a failed measurement but an absent one"*,
   *"the ledger will empty on its own"*, *"promote that from reading to
   finding"*, *"sent us back to the machine"*. The fix is the spade rule:
   call a spade a spade and say the fact.

3. **Meta-commentary** — the document narrating its own rhetoric or its own
   production instead of its subject. Signatures: *"and we state it as such"*,
   *"we state it narrowly"*, *"we note it rather than build on it"*, and the
   worst subtype, **drafting-history bleed**: text addressed to "a reader who
   later meets an earlier draft" in a venue where only the final text exists.
   Related: **agentless verbs** ("the findings publish regardless of
   direction" — findings don't publish; we publish them) and
   **lecture-the-reader constructions** ("A reader who takes X as Y will be
   misled, and so will one who…").

## What is NOT an offense — protect these

- **Earned aphorisms.** A document may keep its two or three best sentences even
  if they are rhetorical — *"an instrument of this kind does not fail by
  crashing, it fails by returning a number one would have believed"* survived
  the first run because it states the paper's central hazard, once, where the
  incident earned it. The Keep grade exists so over-cleaning is a graded error,
  not a virtue.
- **Signposting that carries information.** *"Two conclusions follow, and they
  are separable"* tells the reader they may accept one without the other. Keep.
- **Scientific hedging that scopes a claim** ("on these data", "we report it as
  observations on one model"). Scoping is content, not throat-clearing.

## The pipeline — four steps, applied one at a time

The review is **staged**. Each step produces a report or a numbered list, the
principal rules on it, the ruling is applied, and only then does the next step
begin. **After applying each step, suggest the next step and say in one line
what it consists of.** Never run two steps in one pass — each step reads
the document as the previous step left it.

Every step follows the same contract: **report first, edit nothing until the
principal rules.** Rulings are applied to a new point version (v10.2, v10.3, …) and to the
release file in the same pass, verified and re-rendered.

### Step 1 — Phrasing pass (throat-clearing, ellipsis, meta-commentary)

The writer reads the document end to end, sequentially — no grep-only pass —
and reports every finding: **location, full verbatim quote, offense named,
rewrite in the principal's voice**, to `<stem>-phrasing-report.md` beside the
source. The reviewer grades each finding in the same file: **Blocker / Major / Minor / Polish /
Keep**, with a tally and verdict. The Keep grade is mandatory calibration — a
document keeps its two or three earned aphorisms, and over-cleaning is a graded
error. The principal edits the report itself to rule (changing a verdict to Keep is a
ruling); "apply it all" means apply everything not marked Keep.

### Step 2 — Paragraph-redundancy pass

Full re-read with one question per paragraph: *if this vanished, would any
claim, number or caveat vanish with it?* Propose ~10 whole paragraphs whose
removal loses nothing or improves the paper, **as a numbered chat list with the
full text of each paragraph** and a one-line rationale (usual causes: a story
told three times, a signpost pointing at the next paragraph, a caveat answering
an unasked question, a claim gone stale). The principal rules per number. When a
deletion orphans an antecedent in a neighbouring sentence, make the minimal
splice and report it — a splice is part of the deletion, not a rewrite.

### Step 3 — Tables and figures clarity (the reviewer)

The reviewer reviews **every table and figure**: is each column and dimension defined
where the reader is looking? Standing checks, learned from the first run:
aggregate columns that mix models with different per-token prices must say so in
the caption; every price needs a stated source and capture date **in the
paper**, not just the repo; caption cross-references must point at sections
that actually contain the referenced material; counts in captions rot faster
than counts in tables. Report in chat with severities; no edits until ruled.

### Step 4 — Phrase-level padding pass

The finest grain: ~20 intra-paragraph phrases whose **removal adds clarity** —
empty intensifiers (*remarkably*, *simply*, *duly*), announcer sentences the
earlier passes missed (*"X deserves a note"*, *"The practical reading is
direct"*), staged hypotheticals (*"A reviewer may reasonably ask…"*), repeated
verdicts, hedges that dilute the thing being established (*"is understood to
be"*), and decorative tails after a complete point. Numbered chat list with each
phrase in its sentence and what removal leaves. The principal rules; apply.

### Every step is also a bug sweep

Each of the four steps found factual errors on the first run: a wrong
scaffolding count in the Discussion (step 1), a claim gone false after the data
changed (step 2), two stale counts and a dangling price reference in captions
(step 3), broken articles and another stale count (step 4). **Style passes
catch arithmetic because they force a reread of sentences nobody has looked at
in weeks.** Report bugs alongside the style findings; they outrank everything.

## Relationship to the existing passes

This pipeline is a different layer from `/unslop-text` (the prose-tic sweep).
The tic sweep catches **vocabulary** — *delve*, *crucial*, *tapestry*. This
pipeline catches **moves** (step 1), **redundancy** (steps 2 and 4) and
**undefined dimensions** (step 3), which survive any vocabulary filter because
every individual word in them is innocent. Run the tic sweep first (it is
cheap), then this pipeline, on anything release-bound where the prose matters.

## Worked example

The first full execution ran on a research paper's arXiv draft (2026-08-09): step 1
produced 25 findings (2 Blockers), step 2 removed nine paragraphs and fixed one
false claim, step 3 restored the price provenance the dollar columns stood on,
step 4 removed twenty phrases and four bugs. Net: two pages shorter, no number
changed, 60 verifier checks green throughout.
