# tools/refs-check/

Reference verification for academic documents Grumpy reviews. Wraps `bibsleuth` (six-database triangulation: OpenAlex, Semantic Scholar, CrossRef, arXiv, DBLP, PubMed) and adds an abstract-fetch pass so Grumpy can compare the **claim** the reviewed paper makes about a reference against **what the reference actually says**.

Produces a `<paper-stem>-refs-checks.md` markdown file that lives next to the reviewed document and becomes the **source of truth** for that document's reference verification — Grumpy reads it on subsequent reviews rather than re-querying bibsleuth.

Marc 2026-05-28 (the commissioning brief):

> *"grumpy when you review an academic document, create a paralet `*-refs-checks.md` there you compile the list of references of the paper and your validation. If possible get the paper abstract, so you can verify the likelihood that the paper actually provides the claims the reviewed paper is making about the reference. Then you can treat this `*-refs-checks.md` file as source of truth so you do not have to re-query the bibsleuth tool."*

## What's in here

| File | What it does |
|---|---|
| `check_refs.py` | The wrapper. Runs `bibsleuth check`, fetches abstracts (Semantic Scholar → OpenAlex → Crossref fallback chain), emits the source-of-truth markdown. Idempotent — re-running with a new ref in the .bib appends only the new entry; Grumpy's manual annotations are preserved. |
| `setup.sh` | Idempotent host bootstrap. Installs `bibsleuth` via `uv tool install bibsleuth --python 3.12`, runs a network-reachability smoke test against a known-real reference. Run once per host. |
| `README.md` | This file. |

## First-time setup on a new host

```bash
bash tools/refs-check/setup.sh
```

Idempotent — re-runs safely. Requires `uv` (the script will tell you how to install if missing). Installs bibsleuth as a uv tool (`~/.local/bin/bibsleuth`), pinned to Python 3.12 because bibsleuth requires `>=3.12`. After setup, both `bibsleuth` and the workshop wrapper script are pre-approved in `.claude/settings.json` — no permission prompts during agent runs.

Per-host install state is recorded in [`memory/reference_hosts.md`](../../memory/reference_hosts.md).

## Daily use

```bash
# Produce / refresh the source-of-truth file:
python3 tools/refs-check/check_refs.py PATH/TO/refs.bib

# Custom output path:
python3 tools/refs-check/check_refs.py PATH/TO/refs.bib -o PATH/TO/my-refs.md
```

Default output is `<bib-stem>-refs-checks.md` alongside the input. So:
- `academic-reviews/schweitzer_rocuts_review/thesis.bib` →
- `academic-reviews/schweitzer_rocuts_review/thesis-refs-checks.md`

## What the source-of-truth file looks like

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

**Cited in paper at:** _(Grumpy: fill in section / page)_
**Claim made:** _(Grumpy: what the reviewed paper says about this reference)_
**Assessment:** _(Grumpy: supported / partially supported / unsupported / claim is generic / no full-text access)_
**Flags:** _(auto-fill: chimeric / year-mismatch / author-mismatch)_

---
```

## Grumpy verdicts — what they mean

The wrapper computes a **Grumpy verdict** on top of bibsleuth's output, combining the academic-DB triangulation with a URL-liveness check (fetch the URL, follow redirects, compare the page title and body to the cited title).

| Verdict | Meaning | Action |
|---|---|---|
| ✅ `confirmed` | Bibsleuth `verified`/`likely` **or** URL alive + page title/body matches cited title | OK to ship |
| ⚠️ `title-mismatch` | URL exists, page returns 200, but page title doesn't match cited title | Inspect — could be publisher reframing (OK) or chimeric ref (Critical) |
| 🚫 `unreachable` | URL returns 4xx/5xx/timeout | Link rot or fabrication — find the live URL or remove the citation |
| ❓ `escalate` | No URL, no DOI, no academic-DB candidates | **Marc must verify manually.** No paper ships until this list is empty. |

## Bibsleuth verdicts — the lower layer

Bibsleuth itself outputs `verified` / `likely` / `unverified`. These feed into the Grumpy verdict but **aren't the final word** — in particular, `verified` for a `@misc` entry with a URL field only means *"there is a URL string here"*, not *"the URL points at a real page"*. Marc 2026-05-28 caught this gap; the URL-liveness layer is the fix.

| Bibsleuth verdict | Meaning at the academic-DB layer |
|---|---|
| `verified` | High-confidence match across multiple providers (academic refs); OR misc-with-URL placeholder (gray-lit refs — URL liveness needed for real verification) |
| `likely` | Probable academic-DB match; some metadata drift but the same paper |
| `unverified` | Below match threshold across all providers. May be a real paper with bad metadata, OR a fabrication. Marc/Grumpy checks. |

The **chimeric** case is the subtle one: the bib has a fake DOI; bibsleuth follows the DOI and gets back a real-but-different paper. The URL-liveness step's title-comparison catches this: the URL is alive, but the page title doesn't match the cited title → `title-mismatch` flag.

## The URL-liveness layer — what it does

For every `.bib` entry with a `url` field (and for every DOI's resolved URL):

1. **Fetch the URL** with a Safari-like User-Agent (publishers often block default Python UAs).
2. **Follow redirects** up to the standard limit.
3. **Classify the response:**
   - 200 → alive; extract page title (og:title → `<title>` → first `<h1>`) and body
   - 401/403/429 → blocked (paywall, bot-blocker, rate limit — page may exist; can't confirm)
   - 404/410 → dead — link rot or fabrication
   - 5xx / timeout / connection refused → unreachable
4. **Compare cited title to page title** via token-overlap heuristic. If title-only match fails, fall back to searching the page body (handles publishers who reframe titles — e.g. Khan Academy wraps Khan's TED talk title in their own header).
5. **Feed the result into the Grumpy verdict.**

The wrapper rate-limits to ~0.3s between URL fetches to be polite to free-tier APIs and publisher servers.

## The Playwright URL re-check layer — `verify-urls.mjs`

`check_refs.py`'s URL pass uses a plain HTTP client. Many publisher and blog hosts (Macmillan, BJET, RIED, theconversation, Cloudflare-fronted sites) **bot-block non-browser clients** and return `403` to it — leaving a wall of `escalate` verdicts that are really just *"my fetcher got refused,"* not *"this reference is suspect."* `verify-urls.mjs` is the **escalation layer**: it re-loads those URLs in a real headless Chromium (proper User-Agent + headers), which sails past most soft bot-blocks, and writes the result back into the `*-refs-checks.md`.

```bash
# Re-check every not-yet-`alive` URL in a refs-checks file (default):
node tools/refs-check/verify-urls.mjs PATH/TO/foo-refs-checks.md

# Preview without writing:
node tools/refs-check/verify-urls.mjs PATH/TO/foo-refs-checks.md --dry

#   --only-blocked   re-check only `blocked` (403) entries, skip `unreachable`
#   --all            re-check every URL block, even ones already `alive`
#   --timeout MS     per-page nav timeout (default 25000)
```

It reads cited titles from the sibling `.bib` (or `--bib PATH`), loads each target URL, records final HTTP status + page `<title>`, computes a token-overlap title match, and patches **only** the `**URL check**` sub-block, the `**Grumpy verdict:**` bullet, the `## [key]` header verdict, and the roll-up. It never touches the manual Claim/Assessment annotations.

**The one hard invariant — re-check only ever *upgrades*.** URL-liveness and academic-DB triangulation are independent axes of evidence. A reference bibsleuth already `confirmed` via the databases must **never** be downgraded to `escalate` just because a publisher bot-blocks the browser. So on a `403`/nav-error the script *preserves* the prior verdict (refreshing only the URL-check notes); a hard `404` is surfaced as `unreachable` but still won't clobber a DB-`confirmed`. Alive + title-match → `confirmed`; alive + title-mismatch → `title-mismatch` (chimeric smell), unless the ref was already DB-confirmed. (This invariant exists because the first cut got it wrong and downgraded four DB-confirmed refs on 2026-05-29; the fix is the reason the rule is written down.)

A residual `403` even from the real browser (typically a Cloudflare interstitial — `"Just a moment…"` / `"Access Denied"`) means the URL is genuinely behind a hard challenge: the verdict stays whatever it was, and a no-prior-evidence ref stays `escalate` for Marc to confirm by hand.

Setup is handled by `setup.sh` (step 6 — installs the `playwright` npm package locally + provisions Chromium). `node_modules/` is gitignored; the committed durable assets are `verify-urls.mjs`, `package.json`, and `.gitignore`.

## The strict anti-hallucination rule

**Never invent a URL or DOI to "fill in" a missing-metadata entry.** This is the failure mode the whole system exists to prevent. Marc 2026-05-28:

> *"What is CRITICAL and I mean CRITICAL is that we can't send a paper with a reference [not] fully verified... try'ing to publish with halucinated references is a loss of prestige I do not want to risk."*

If a `.bib` entry has no URL or DOI in the source material, leave the field empty. The ref will surface in the `❓ Refs Marc must confirm manually` section. Marc finds the right URL; Grumpy updates the .bib; re-run with `--force`.

Grumpy 2026-05-28 caught itself fabricating a plausible-looking EU Commission URL while extracting the RIED .bib. The auto-detection + revert was correct. The lesson: *the temptation to "fill in" a missing URL is exactly the failure mode.* Resist.

## The abstract-fetch fallback chain

Bibsleuth itself does not return abstracts. `check_refs.py` adds:

1. **Semantic Scholar** — cleanest abstract field, no API key, free tier rate-limited.
2. **OpenAlex** — inverted-index format, de-inverted into running text by the script.
3. **Crossref** — JATS XML in the `abstract` field, HTML-stripped.

Each ref triggers one to three GETs (whichever provider responds first wins). 0.4-second sleep between refs to keep us under free-tier rate limits.

If none of the three providers returns an abstract — common for books, theses, gray literature, conference posters — the entry shows *"Abstract: not retrievable"* and Grumpy notes this explicitly in the Assessment field.

## Idempotency rules

`check_refs.py` parses the existing markdown's `## [refkey]` sections before writing. For each ref in the .bib:

- **Key already in the file** → skip. Grumpy's manual fields (Cited-at, Claim, Assessment, manual Flags) are preserved.
- **New key not in the file** → run bibsleuth check + fetch abstract + append.

This means: as a paper's reference list grows during writing, you re-run the script and only the new refs get processed. The accumulated reviewing labour stays intact.

## What Grumpy does with this file

Grumpy's full workflow lives at [`../../skills/grumpy-check-refs.md`](../../skills/grumpy-check-refs.md). The short version:

1. Extract .bib from the document being reviewed (author-provided is ideal; GROBID-extracted for PDFs without source).
2. Run this script → get the `*-refs-checks.md`.
3. For each ref: locate the citing claim in the paper, paste it into *Claim made*, compare against the *Abstract*, write the *Assessment*.
4. Roll up the findings into Grumpy's main review document (per-engagement, in `academic-reviews/<engagement>/`). Citation issues map to the severity matrix: **Critical** for fabricated/chimeric refs, **Severe** for unsupported-claim citations, **Polish** for missing DOIs or metadata mismatches.

## Limitations

- **No PDF reference extractor yet.** Document-level intake assumes a `.bib` source. For PDFs without source: ask the author, or run GROBID separately (queued as a follow-up tool when the first PDF-only engagement arrives).
- **Bibsleuth's `--no-llm` mode is used by default** for determinism and cost. The LLM-assisted mode catches more semantic mis-citations but costs API calls and adds non-reproducibility. If a critical engagement warrants the deeper check, add `--llm-on` to the bibsleuth subprocess invocation (not currently surfaced as a `check_refs.py` flag; trivial to add).
- **Abstracts are not full-text.** Grumpy can verify generic-claim alignment from an abstract, but not specific-claim alignment (*"the paper says X about Y"* where X is a detail buried on page 14). For those, the citing paper's full-text or a manual check is needed.

## Related

- [Skill — when Grumpy invokes this tool](../../skills/grumpy-check-refs.md)
- [Grumpy's rules — reference verification is non-optional](../../characters/grumpy/rules.md)
- [Code-as-action operating mode](../../memory/feedback_browser_tasks_code_as_action.md) — same posture applied to browser tasks; reference verification follows the same pattern (small dedicated tool, persistent output file, idempotent re-runs).
- [bibsleuth upstream](https://github.com/yy/bibsleuth) — MIT, active dev as of March 2026.

---

*Created 2026-05-28 — Marc commissioned the tool for Grumpy's reference verification capability.*
