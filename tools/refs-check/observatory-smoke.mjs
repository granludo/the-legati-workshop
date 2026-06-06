// Smoke test for the Legati Observatory HTML dashboard.
// Loads the file:// page in headless Chromium, captures JS errors, exercises the
// interactive controls (zoom + session drill), checks Mermaid rendered, screenshots.
// Co-located in tools/refs-check/ only to reuse its Playwright install.
// Usage: node tools/refs-check/observatory-smoke.mjs <path-to-dashboard.html>
import { chromium } from 'playwright';
import { resolve } from 'node:path';

const htmlPath = process.argv[2];
if (!htmlPath) { console.error('usage: observatory-smoke.mjs <dashboard.html>'); process.exit(2); }
const url = 'file://' + resolve(htmlPath);
const shot = '/tmp/observatory-smoke.png';

const errors = [];
const browser = await chromium.launch();
const page = await browser.newPage();
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push('console.error: ' + m.text()); });

await page.goto(url, { waitUntil: 'load' });
await page.waitForTimeout(400); // let JS render

const count = async sel => page.locator(sel).count();
const res = {};
res.liveRows   = await count('#live table tr');
res.countCards = await count('#counts .card');
res.feedRows   = await count('#feed table tr');
res.sessRows   = await count('#sessions tr.clk');
res.zoomBtns   = await count('#controls button');

// Mermaid: is the lib loaded, and did it turn <pre class="mermaid"> into an <svg>?
const mermaidLoaded = await page.evaluate(() => typeof window.mermaid);
let mermaidSvg = 0;
try { await page.waitForSelector('.mermaid svg', { timeout: 5000 }); } catch {}
mermaidSvg = await count('.mermaid svg');

// Exercise zoom: click "all", confirm summary updates
const sumBefore = await page.locator('#summary').textContent();
await page.locator('#controls button[data-w="all"]').click();
await page.waitForTimeout(150);
const sumAfter = await page.locator('#summary').textContent();

// Exercise drill: click first session row, confirm panel opens
let drillOpened = false;
if (res.sessRows > 0) {
  await page.locator('#sessions tr.clk').first().click();
  await page.waitForTimeout(150);
  drillOpened = await page.locator('#drill.open').count() > 0;
}

await page.screenshot({ path: shot, fullPage: true });
await browser.close();

const pass =
  res.countCards === 4 && res.feedRows > 1 && res.zoomBtns >= 5 &&
  sumBefore !== null && sumAfter !== null && sumBefore !== sumAfter &&
  (res.sessRows === 0 || drillOpened) && errors.length === 0;

console.log('— Observatory HTML smoke —');
console.log('  url        :', url);
console.log('  counts     :', JSON.stringify(res));
console.log('  mermaid    :', 'lib=' + mermaidLoaded, 'svg=' + mermaidSvg, mermaidSvg ? '(graph rendered)' : '(no svg)');
console.log('  zoom click :', JSON.stringify({ sumBefore, sumAfter }), sumBefore !== sumAfter ? 'OK (updated)' : 'NO CHANGE');
console.log('  drill open :', drillOpened);
console.log('  JS errors  :', errors.length ? errors : 'none');
console.log('  screenshot :', shot);
console.log(pass ? '\nRESULT: ✅ PASS' : '\nRESULT: ❌ FAIL');
process.exit(pass ? 0 : 1);
