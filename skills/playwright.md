# /playwright — give an agent a real browser

The standing pattern for any browser task that goes beyond a single read-only fetch. Read this when you (any agent) need to load a JS-rendered page, get past a bot-block, drive a multi-step flow, or capture a screenshot/PDF — and `WebFetch` isn't enough.

This skill is the **how-to-get-a-browser** layer. The governing rule is *code-as-action*: write a script and keep it — the browser is disposable, the script is the durable asset.

## First decision — do you even need Playwright?

| Task shape | Reach for | Why |
|---|---|---|
| Read a public, static page; extract one thing | **`WebFetch`** | Cheapest, in-context. The default. |
| GitHub (issues, PRs, releases) | **`gh` CLI** | Never `WebFetch` github.com. |
| Gmail / Calendar / Drive | **a Workspace CLI** (comms agent's lane) | OAuth-scoped, not a browser. |
| Moodle / LMS | **the LMS web-services API** | Use the WS endpoint, not a browser. |
| **JS-rendered / multi-step / stateful / bot-blocked / screenshot-as-deliverable** | **Playwright** (this skill) | When the above can't reach it. |

If `WebFetch` returns an empty shell, a login wall, or a `403`, that's the signal to escalate to Playwright.

## Two ways to use Playwright here — pick by repeatability

**Mode A — library script (code-as-action). This is the default for anything that will recur.**
Write a small `.mjs` (or Python) script using the `playwright` library, commit it under `tools/<task-slug>/`, and re-run/fork it next time. The browser is disposable; **the script is the durable asset**.

- Create a `tools/<task-slug>/` dir with the script, a `package.json`, and a short README; gitignore `node_modules/` and any `outputs/`.
- Fork a working example: [`tools/refs-check/verify-urls.mjs`](../tools/refs-check/verify-urls.mjs) — Node/`.mjs`, loads a list of URLs, records HTTP status + page title, patches a markdown file. A good template for "load N URLs, extract a field each, write results back."

**Mode B — `@playwright/cli` for one-off interactive exploration.**
When you just need to poke at one page once (snapshot it, read a value, take a screenshot) and there's nothing worth keeping, the CLI is faster than authoring a script: `npx --yes @playwright/cli@latest <command>`. Token rule: prefer `snapshot` over dumping the DOM with `eval`.

Do **not** drive the browser turn-by-turn from chat ("now click that, now scroll"). If the task has more than ~2 steps, it's Mode A — write the script.

## One-time host setup

For a new tool dir:
```bash
cd tools/<task-slug>/
npm install playwright                  # local dep; add node_modules/ to .gitignore
npx playwright install chromium         # ~150 MB, one-time per host, reused after
```
For Mode B: `npx --yes @playwright/cli@latest <command>` — no install, caches on first call.

**Front-load the user on the download.** The first browser provision on a fresh host pulls ~150 MB (Chromium only) to ~500 MB (all engines). Tell the user before kicking it off — same as any long-running install.

## Gotchas learned in practice

- **A real browser still gets bot-blocked sometimes.** Cloudflare-fronted hosts return a `403` interstitial (`"Just a moment…"` / `"Access Denied"`) even to headless Chromium with a proper User-Agent. When that happens the URL is behind a hard challenge — don't treat it as proof the resource is fake; escalate to a human click.
- **Set a realistic User-Agent + `Accept-Language`.** The default Playwright UA gets refused more often. Use a `newContext({ userAgent, extraHTTPHeaders })` block.
- **`waitUntil: 'domcontentloaded'`** is usually enough and far faster than `networkidle` for "did this page load and what's its title" checks.
- **Verification scripts should only ever *upgrade* evidence, never clobber a prior positive.** A browser check that fails (block/timeout) is *indeterminate*, not negative — preserve whatever verdict you already had. Only positive new evidence (page loaded, content matched) should change a verdict.
- **Auth stays out of git.** Log in only with credentials the user provides for that script (env / `.env`). Never persist cookies/sessions to the repo. 2FA flows hand back to the user.

## Portability note

This skill is plain markdown and invocable in natural language (*"use Playwright to load…"*) — no scaffolding-specific mechanism. The durable layer is: this skill + the committed scripts + `package.json`. `node_modules/` and browser binaries are host-local and reprovisioned by `npm install`. Any agent scaffolding that can shell out to `node`/`npx` runs these unchanged.

## Related

- [`tools/refs-check/verify-urls.mjs`](../tools/refs-check/verify-urls.mjs) — the worked Mode-A example.

---

*Canonical invocation is natural language; `/playwright` is the terse shortcut.*
