# /playwright — give an agent a real browser

The workshop's standing pattern for any browser task that goes beyond a single read-only fetch. Read this when you (any agent — Mycroft, Agatha, Grumpy, Dick, Bilby) need to load a JS-rendered page, get past a bot-block, drive a multi-step flow, or capture a screenshot/PDF — and `WebFetch` isn't enough.

This skill is the **how-to-get-a-browser** layer. The governing operating rule is [`memory/feedback_browser_tasks_code_as_action.md`](../memory/feedback_browser_tasks_code_as_action.md) (code-as-action — write a script, keep it); the tool reference is [`memory/reference_playwright_cli.md`](../memory/reference_playwright_cli.md). This skill ties them together and records the gotchas learned in practice.

## First decision — do you even need Playwright?

| Task shape | Reach for | Why |
|---|---|---|
| Read a public, static page; extract one thing | **`WebFetch`** | Cheapest, in-context. The default. |
| GitHub (issues, PRs, releases) | **`gh` CLI** | Never `WebFetch` github.com. |
| Gmail / Calendar / Drive | **`gws`** (Bilby's lane) | OAuth-scoped, not a browser. |
| LAMB / Moodle / Atenea | **`moodle-cli`** | Use the WS endpoint, not a browser. |
| **JS-rendered / multi-step / stateful / bot-blocked / screenshot-as-deliverable** | **Playwright** (this skill) | When the above can't reach it. |

If `WebFetch` returns an empty shell, a login wall, or a `403`, that's the signal to escalate to Playwright.

## Two ways to use Playwright here — pick by repeatability

**Mode A — library script (code-as-action). This is the default for anything that will recur.**
Write a small `.mjs` (or Python) script using the `playwright` library, commit it under `tools/<task-slug>/`, and re-run/fork it next time. The browser is disposable; **the script is the durable asset**. This is the canonical mode per the code-as-action rule.

- Fork the seed scaffold: `cp -r tools/_template tools/<task-slug>/` (ships with `--dry-run`, event log, screenshot helpers, a rename-guard).
- Or fork a working example:
  - [`tools/refs-check/verify-urls.mjs`](../tools/refs-check/verify-urls.mjs) — Node/`.mjs`, loads a list of URLs, records HTTP status + page title, patches a markdown file. Good template for "load N URLs, extract a field each, write results back."
  - [`tools/papers-import/scrape_futur.sh`](../tools/papers-import/scrape_futur.sh) — shell-driven Playwright for a portfolio scrape.
- Commit the script + a short README; **gitignore `node_modules/` and any `outputs/`**. The script and `package.json` are the portable layer.

**Mode B — `@playwright/cli` for one-off interactive exploration.**
When you just need to poke at one page once (snapshot it, read a value, take a screenshot) and there's nothing worth keeping, the CLI is faster than authoring a script. Full reference (commands, token discipline, session flags): [`memory/reference_playwright_cli.md`](../memory/reference_playwright_cli.md). Token rule: prefer `snapshot` over dumping the DOM with `eval`.

Do **not** drive the browser turn-by-turn from chat ("now click that, now scroll"). If the task has more than ~2 steps, it's Mode A — write the script.

## One-time host setup

For **Mode A in `tools/refs-check/`** (and the pattern for any tool dir): `setup.sh` already provisions it —
```bash
bash tools/refs-check/setup.sh          # installs the playwright npm pkg + Chromium, idempotent
```
For a **new tool dir** of your own:
```bash
cd tools/<task-slug>/
npm install playwright                  # local dep; add node_modules/ to .gitignore
npx playwright install chromium         # ~150 MB, one-time per host, reused after
```
For **Mode B**: `npx --yes @playwright/cli@latest <command>` — no install, caches on first call.

**Front-load Marc on the download.** The first browser provision on a fresh host pulls ~150 MB (Chromium only) to ~500 MB (all engines). Tell him before kicking it off — same as any long-running install. Record the install in [`memory/reference_hosts.md`](../memory/reference_hosts.md) under the host's toolchain.

## Gotchas learned in practice

- **A real browser still gets bot-blocked sometimes.** Cloudflare-fronted hosts return a `403` interstitial (`"Just a moment…"` / `"Access Denied"`) even to headless Chromium with a proper User-Agent. When that happens the URL is behind a hard challenge — don't treat it as proof the resource is fake; escalate to a human click. (Surfaced 2026-05-29 on the RIED refs pass: BJET, RIED, and a few others stayed `403`.)
- **Set a realistic User-Agent + `Accept-Language`.** The default Playwright UA gets refused more often. See the `newContext({ userAgent, extraHTTPHeaders })` block in `verify-urls.mjs`.
- **`waitUntil: 'domcontentloaded'`** is usually enough and far faster than `networkidle` for "did this page load and what's its title" checks.
- **Verification scripts should only ever *upgrade* evidence, never clobber a prior positive.** Generalised from the refs work: a browser check that fails (block/timeout) is *indeterminate*, not negative — preserve whatever verdict you already had. Only positive new evidence (page loaded, content matched) should change a verdict in the confirming direction.
- **Auth stays out of git.** Log in only with credentials Marc provides for that script (env / `.env`). Never persist cookies/sessions to the repo. 2FA flows hand back to Marc.

## Portability note

This skill is plain markdown and invocable in natural language (*"use Playwright to load…"*) — no scaffolding-specific mechanism. The durable layer is: this skill + the committed scripts + `package.json`. `node_modules/` and browser binaries are host-local and reprovisioned by `setup.sh` / `npm install`. Any agent scaffolding that can shell out to `node`/`npx` runs these unchanged. See [`feedback_scaffolding_portability.md`](../memory/feedback_scaffolding_portability.md).

## Related

- [`feedback_browser_tasks_code_as_action.md`](../memory/feedback_browser_tasks_code_as_action.md) — the governing rule (write the script, keep it).
- [`reference_playwright_cli.md`](../memory/reference_playwright_cli.md) — Mode B command reference + token discipline.
- [`tools/refs-check/verify-urls.mjs`](../tools/refs-check/verify-urls.mjs) + [its README section](../tools/refs-check/README.md) — the worked Mode-A example.
- [`project_peekaboo_evaluation.md`](../memory/project_peekaboo_evaluation.md) — the fallback for auth-gated GUIs scripts can't reach.

---

*Created 2026-05-29 by Mycroft, after the RIED refs URL re-check (`verify-urls.mjs`) established the first reusable library-mode Playwright asset. Canonical invocation is natural language; `/playwright` is the terse shortcut.*
