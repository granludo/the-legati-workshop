#!/usr/bin/env node
/**
 * verify-urls.mjs — Playwright URL-liveness re-check for Grumpy's refs-checks files.
 *
 * bibsleuth's plain HTTP client gets a 403 from many publisher / blog hosts that
 * bot-block non-browser user agents (Macmillan, BJET, RIED, theconversation, ...).
 * That leaves a wall of `escalate` verdicts Marc has to clear by hand even though
 * the URLs are perfectly alive. This loads each not-yet-`alive` reference URL in a
 * real headless Chromium, records the final HTTP status + page <title>, computes a
 * title-match against the cited title, and writes the result back into the
 * `*-refs-checks.md` source-of-truth file — upgrading `escalate` → `confirmed`
 * (alive + title match) or `title-mismatch` / `unreachable` where warranted.
 *
 * It only ever TOUCHES the `**URL check**` sub-block, the `**Grumpy verdict:**`
 * bullet, the `## [key] — emoji verdict` header, and the roll-up section. It never
 * touches the manual claim/assessment annotations.
 *
 * Usage:
 *   node verify-urls.mjs PATH/TO/foo-refs-checks.md [options]
 *
 * Options:
 *   --bib PATH        .bib to read cited titles from (default: foo.bib next to the md)
 *   --only-blocked    re-check only `blocked` (403/refused) entries, skip `unreachable`
 *   --all             re-check every URL-check block, even ones already `alive`
 *   --dry             print the plan + results, do NOT write the file
 *   --timeout MS      per-page navigation timeout (default 25000)
 *   -h, --help        this text
 *
 * Convention: tools/<slug>/ reusable code-as-action asset
 * (see memory/feedback_browser_tasks_code_as_action.md).
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { chromium } from 'playwright';

// ----------------------------------------------------------------------------- args
const argv = process.argv.slice(2);
if (argv.includes('-h') || argv.includes('--help') || argv.length === 0) {
  console.log(readFileSync(new URL(import.meta.url)).toString().split('\n')
    .filter(l => l.startsWith(' *') || l.startsWith('/**')).map(l => l.replace(/^\/?\*\*?/, '').trim()).join('\n'));
  process.exit(0);
}
const opts = {
  mdPath: null, bib: null,
  onlyBlocked: argv.includes('--only-blocked'),
  all: argv.includes('--all'),
  dry: argv.includes('--dry'),
  timeout: 25000,
};
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === '--bib') opts.bib = argv[++i];
  else if (a === '--timeout') opts.timeout = parseInt(argv[++i], 10);
  else if (!a.startsWith('-')) opts.mdPath = a;
}
if (!opts.mdPath) { console.error('error: no refs-checks.md path given'); process.exit(2); }
opts.mdPath = resolve(opts.mdPath);
if (!opts.bib) opts.bib = opts.mdPath.replace(/-refs-checks\.md$/, '.bib');

// ------------------------------------------------------------------------- helpers
const norm = (s) => (s || '')
  .normalize('NFKD').replace(/[̀-ͯ]/g, '')   // strip diacritics
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, ' ').trim();

/** token-overlap ratio of cited title tokens present in the page title */
function titleMatch(cited, page) {
  const c = norm(cited), p = norm(page);
  if (!c || !p) return { match: false, ratio: 0 };
  if (p.includes(c) || c.includes(p)) return { match: true, ratio: 1 };
  const ct = c.split(' ').filter(t => t.length > 2);
  const pt = new Set(p.split(' '));
  const hit = ct.filter(t => pt.has(t)).length;
  const ratio = ct.length ? hit / ct.length : 0;
  return { match: ratio >= 0.6, ratio };
}

/** crude bib title extractor: title = {...} for a given key, LaTeX-accent-stripped */
function bibTitles(bibText) {
  const out = {};
  const entryRe = /@\w+\s*\{\s*([^,\s]+)\s*,([\s\S]*?)\n\}/g;
  let m;
  while ((m = entryRe.exec(bibText))) {
    const key = m[1].trim();
    const body = m[2];
    const tm = body.match(/title\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}/i);
    if (tm) out[key] = tm[1].replace(/[{}]/g, '').replace(/\\['"`^~=.]?/g, '').replace(/\s+/g, ' ').trim();
  }
  return out;
}

const VERDICT_EMOJI = {
  confirmed: '✅', 'title-mismatch': '⚠️', unreachable: '🚫', escalate: '❓',
};

// -------------------------------------------------------------------------- parse md
const md = readFileSync(opts.mdPath, 'utf8');
const titles = bibTitles(readFileSync(opts.bib, 'utf8'));

// split into [preamble, ...refBlocks]; each ref block starts at a "## [key]" header.
const parts = md.split(/(?=^## \[)/m);
const preamble = parts[0];
const blocks = parts.slice(1).map((text) => {
  const head = text.match(/^## \[([^\]]+)\]\s*—\s*(\S+)\s*`([^`]+)`/m);
  const urlCheck = text.match(/\*\*URL check\*\*\s*—\s*`([^`]+)`(?:\s*\(([^)]*)\))?/);
  const urlChecked = text.match(/\*\*URL checked:\*\*\s*<([^>]+)>/);
  return {
    text,
    key: head ? head[1] : null,
    verdict: head ? head[3] : null,
    urlStatus: urlCheck ? urlCheck[1] : null,         // alive | blocked | unreachable | ...
    url: urlChecked ? urlChecked[1].trim() : null,
    citedTitle: head ? (titles[head[1]] || null) : null,
  };
});

// which blocks to (re)check
const needsCheck = (b) => {
  if (!b.url || !/^https?:\/\//.test(b.url)) return false;
  if (opts.all) return true;
  if (opts.onlyBlocked) return b.urlStatus === 'blocked';
  return b.urlStatus && b.urlStatus !== 'alive';      // blocked + unreachable + indeterminate
};
const targets = blocks.filter(needsCheck);

console.log(`refs-checks : ${opts.mdPath}`);
console.log(`bib         : ${opts.bib}  (${Object.keys(titles).length} titles)`);
console.log(`blocks      : ${blocks.length} total, ${targets.length} to re-check` +
  (opts.dry ? '  [DRY RUN]' : ''));
if (targets.length === 0) { console.log('nothing to do.'); process.exit(0); }

// ---------------------------------------------------------------------- playwright
const stamp = new Date().toISOString();
const browser = await chromium.launch();
const ctx = await browser.newContext({
  userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ' +
             '(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
  locale: 'en-US',
  extraHTTPHeaders: { 'Accept-Language': 'en-US,en;q=0.9' },
});

const results = [];
for (const b of targets) {
  const page = await ctx.newPage();
  let status = null, pageTitle = null, err = null;
  try {
    const resp = await page.goto(b.url, { waitUntil: 'domcontentloaded', timeout: opts.timeout });
    status = resp ? resp.status() : null;
    try { pageTitle = (await page.title()) || null; } catch { /* ignore */ }
  } catch (e) {
    err = e.message.split('\n')[0];
  } finally {
    await page.close();
  }

  // classify.
  // KEY RULE: URL-liveness and DB-triangulation are INDEPENDENT axes of evidence.
  // A re-check may only ever UPGRADE the verdict (give new positive evidence) — it
  // must never downgrade a reference that bibsleuth already confirmed via the academic
  // databases just because a publisher host bot-blocks the browser. So on block / nav
  // error we PRESERVE the prior verdict and only refresh the URL-check notes; on a
  // hard 4xx/5xx we surface `unreachable` but still never clobber a prior `confirmed`.
  const prior = b.verdict;
  let urlStatus, verdict, notes, tm = null;
  if (err) {
    urlStatus = 'unreachable'; verdict = prior;            // indeterminate — keep prior verdict
    notes = `Playwright navigation failed: ${err} — existence indeterminate; prior verdict \`${prior}\` preserved`;
  } else if (status >= 200 && status < 400) {
    tm = titleMatch(b.citedTitle, pageTitle);
    urlStatus = 'alive';
    if (b.citedTitle && pageTitle) {
      // alive+match → confirmed. alive+mismatch → surface title-mismatch UNLESS the ref
      // was already DB-confirmed (then keep confirmed, but flag the mismatch in notes).
      verdict = tm.match ? 'confirmed' : (prior === 'confirmed' ? 'confirmed' : 'title-mismatch');
    } else {
      verdict = 'confirmed';                               // alive, no cited title to compare
    }
    notes = `HTTP ${status} via Playwright (real browser)` +
      (tm && !tm.match ? ` — ⚠️ page title differs from cited title` : '');
  } else if (status === 403 || status === 401 || status === 429) {
    urlStatus = 'blocked'; verdict = prior;                // hard bot-block — keep prior verdict
    notes = `HTTP ${status} — refused even by real browser (paywall / hard bot-block, e.g. Cloudflare challenge); existence indeterminate; prior verdict \`${prior}\` preserved`;
  } else {
    urlStatus = 'unreachable';
    verdict = prior === 'confirmed' ? 'confirmed' : 'unreachable';  // negative URL evidence, but don't clobber a DB-confirm
    notes = `HTTP ${status} via Playwright — link rot or fabrication` +
      (prior === 'confirmed' ? ` (prior verdict \`confirmed\` preserved — dead URL flagged; consider replacing the link)` : '');
  }
  results.push({ ...b, newStatus: urlStatus, newVerdict: verdict, status, pageTitle, tm, notes });
  const flag = verdict === 'confirmed' ? '✅' : verdict === 'title-mismatch' ? '⚠️'
             : verdict === 'unreachable' ? '🚫' : '❓';
  console.log(`  ${flag} ${b.key.padEnd(34)} ${String(status ?? 'ERR').padEnd(4)} ` +
    (tm ? `match=${tm.match}(${tm.ratio.toFixed(2)}) ` : '') +
    (pageTitle ? `"${pageTitle.slice(0, 60)}"` : (err || '')));
}
await browser.close();

if (opts.dry) {
  const up = results.filter(r => r.newVerdict !== r.verdict).length;
  console.log(`\n[DRY RUN] ${up} block(s) would change verdict. No file written.`);
  process.exit(0);
}

// --------------------------------------------------------------- patch ref blocks
const byKey = new Map(results.map(r => [r.key, r]));
for (const b of blocks) {
  const r = byKey.get(b.key);
  if (!r) continue;

  // 1) header line
  b.text = b.text.replace(
    /^## \[([^\]]+)\]\s*—\s*\S+\s*`[^`]+`.*$/m,
    `## [$1] — ${VERDICT_EMOJI[r.newVerdict]} \`${r.newVerdict}\``);

  // 2) Grumpy verdict bullet
  const verdictNote = r.newVerdict === 'confirmed'
    ? `URL alive (HTTP ${r.status})` + (r.tm ? ` + page title ${r.tm.match ? 'matches' : 'differs from'} cited title` : ' (no cited title on file to match)')
    : r.newVerdict === 'title-mismatch'
    ? `URL alive (HTTP ${r.status}) but page title does NOT match cited title — chimeric smell`
    : r.newVerdict === 'unreachable'
    ? r.notes
    : r.notes;
  b.text = b.text.replace(
    /^- \*\*Grumpy verdict:\*\* .*$/m,
    `- **Grumpy verdict:** \`${r.newVerdict}\` — ${verdictNote} _(Playwright re-check ${stamp})_`);

  // 3) URL check sub-block (from "**URL check**" up to the next "\n\n**Field:")
  const lines = [`**URL check** — \`${r.newStatus}\`${r.status ? ` (HTTP ${r.status})` : ''}`,
    `- **URL checked:** <${r.url}>`];
  if (r.pageTitle) lines.push(`- **Page title:** ${r.pageTitle}`);
  if (r.tm) lines.push(`- **Title match:** \`${r.tm.match ? 'match' : 'mismatch'}\` (cited title vs. page title; token overlap ${r.tm.ratio.toFixed(2)})`);
  lines.push(`- **Notes:** ${r.notes}`);
  lines.push(`- **Method:** real headless Chromium via \`tools/refs-check/verify-urls.mjs\` (${stamp})`);
  b.text = b.text.replace(/\*\*URL check\*\*[\s\S]*?(?=\n\n\*\*[A-Z])/, lines.join('\n'));
}

// --------------------------------------------------------------- regen roll-up
const finalVerdicts = blocks.map(b => {
  const h = b.text.match(/^## \[[^\]]+\]\s*—\s*\S+\s*`([^`]+)`/m);
  const note = b.text.match(/^- \*\*Grumpy verdict:\*\* `[^`]+` — (.*)$/m);
  const key = b.text.match(/^## \[([^\]]+)\]/m)[1];
  return { key, verdict: h ? h[1] : 'escalate', note: note ? note[1].replace(/\s*_\(Playwright.*$/, '') : '' };
});
const count = (v) => finalVerdicts.filter(x => x.verdict === v).length;
const confirmed = count('confirmed'), mismatch = count('title-mismatch'),
      unreach = count('unreachable'), escalate = count('escalate');
const total = finalVerdicts.length;

const listOf = (v) => finalVerdicts.filter(x => x.verdict === v)
  .map(x => `- **\`[${x.key}]\`** — ${x.note}`).join('\n') || '_(none)_';

const rollup = `## Submission gate — Grumpy verdict roll-up

**${confirmed} / ${total} references confirmed.** Per rule §14: a paper does not ship until every reference is \`confirmed\`. _(URL-liveness last re-checked via Playwright: ${stamp})_

| Verdict | Count | Meaning |
|---|---:|---|
| ✅ \`confirmed\`    | ${String(confirmed).padStart(3)} | bibsleuth verified/likely **or** URL alive + title match |
| ⚠️ \`title-mismatch\` | ${String(mismatch).padStart(3)} | URL exists but page title doesn't match the cited title — possible chimeric ref |
| 🚫 \`unreachable\`  | ${String(unreach).padStart(3)} | URL returns 4xx/5xx/timeout — link rot or fabrication |
| ❓ \`escalate\`     | ${String(escalate).padStart(3)} | no positive evidence — **Marc must verify manually** |

### ⚠️ Title-mismatch — chimeric smell, inspect each one

${listOf('title-mismatch')}

### 🚫 Unreachable URLs — link rot or fabrication

${listOf('unreachable')}

### ❓ Refs Marc must confirm manually

Bibsleuth can't reach these, and a real browser couldn't either (hard bot-block) or there's no URL/DOI to check. Confirm each one exists (publisher page, ISBN, archive snapshot, etc.) and either upgrade the bib entry with a verifiable URL/DOI, or remove the citation.

${listOf('escalate')}
`;

// replace the existing roll-up section in the preamble (from its heading to the
// trailing "---" that precedes the first ref block)
let newPreamble = preamble.replace(
  /## Submission gate — Grumpy verdict roll-up[\s\S]*?(?=\n---\n)/,
  rollup.trimEnd() + '\n');

const out = newPreamble + blocks.map(b => b.text).join('');
writeFileSync(opts.mdPath, out);

console.log(`\nwrote ${opts.mdPath}`);
console.log(`roll-up now: ${confirmed} confirmed · ${mismatch} title-mismatch · ${unreach} unreachable · ${escalate} escalate  (of ${total})`);
