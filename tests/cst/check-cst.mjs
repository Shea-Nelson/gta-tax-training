// CST section checks (copy of tests/check.mjs pointed at cst/): every page at 1280 and 320 px, axe (WCAG 2.0/2.1/2.2 A+AA),
// overflow, keyboard focus visibility, internal links/anchors, quiz, calculator (valid, residential, satellite, invalid) and filters.
// Usage (from tests/): node cst/check-cst.mjs http://127.0.0.1:47123 [sut]   -- pass "sut" to re-check the SUT pages with the same harness
import puppeteer from 'puppeteer-core';
import fs from 'node:fs'; import path from 'node:path';
const BASE = process.argv[2]; const SECTION = process.argv[3] || 'cst'; const SITE = path.resolve('../docs'); const OUT = SECTION === 'cst' ? 'out/cst' : 'out/sut-recheck';
fs.mkdirSync(`${OUT}/shots`, { recursive: true });
const axeSrc = fs.readFileSync('node_modules/axe-core/axe.min.js', 'utf8');
const pages = ['index.html', ...fs.readdirSync(`${SITE}/${SECTION}`).filter(f => f.endsWith('.html')).sort().map(f => `${SECTION}/${f}`)];
const browser = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });
const report = { pages: {}, links: new Set(), internalBroken: [], consoleErrors: [] };
for (const p of pages) {
  const r = report.pages[p] = {};
  for (const width of [1280, 320]) {
    const page = await browser.newPage();
    page.on('console', m => { if (m.type() === 'error') report.consoleErrors.push(`${p}: ${m.text()}`); });
    page.on('pageerror', e => report.consoleErrors.push(`${p}: ${e.message}`));
    await page.setViewport({ width, height: 900 });
    const resp = await page.goto(`${BASE}/${p}`, { waitUntil: 'networkidle0' });
    const key = width === 1280 ? 'desktop' : 'mobile';
    r[`${key}Status`] = resp.status();
    await page.addScriptTag({ content: axeSrc });
    r[`${key}Axe`] = await page.evaluate(async () => (await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] } })).violations.map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length, sample: v.nodes.slice(0, 3).map(n => n.target.join(' ')) })));
    r[`${key}Overflow`] = await page.evaluate(() => {
      const docW = document.documentElement.clientWidth; const bad = [];
      document.querySelectorAll('body *').forEach(el => { const b = el.getBoundingClientRect(); if (b.right > docW + 1 && !el.closest('.table-wrap,.figure-scroll') && getComputedStyle(el).position !== 'absolute') bad.push(el.tagName + (el.className && typeof el.className === 'string' ? '.' + el.className : '')); });
      return { scrollW: document.documentElement.scrollWidth, docW, offenders: [...new Set(bad)].slice(0, 8) };
    });
    await page.screenshot({ path: `${OUT}/shots/${p.replace(/[\/.]/g, '_')}-${width}.png` });
    if (width === 1280) {
      (await page.evaluate(() => [...document.querySelectorAll('a[href]')].map(a => a.href))).forEach(l => report.links.add(l));
      const foc = [];
      for (let i = 0; i < 40; i++) {
        await page.keyboard.press('Tab');
        foc.push(await page.evaluate(() => { const e = document.activeElement; if (!e || e === document.body) return null; const s = getComputedStyle(e); return { tag: e.tagName, txt: (e.textContent || e.id || '').trim().slice(0, 30), outline: s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) >= 2 }; }));
      }
      r.keyboard = { stops: foc.filter(Boolean).length, noVisibleFocus: foc.filter(f => f && !f.outline).map(f => f.tag + ':' + f.txt) };
      r.firstTab = foc[0];
    }
    await page.close();
  }
}
for (const l of report.links) {
  if (!l.startsWith(BASE)) continue;
  const u = new URL(l); let f = path.join(SITE, decodeURIComponent(u.pathname)); if (f.endsWith('/')) f += 'index.html';
  if (!fs.existsSync(f)) { report.internalBroken.push(l); continue; }
  if (u.hash && u.hash.length > 1) { const h = fs.readFileSync(f, 'utf8'); if (!h.includes(`id="${decodeURIComponent(u.hash.slice(1))}"`)) report.internalBroken.push(l); }
}
const page = await browser.newPage(); await page.setViewport({ width: 1280, height: 900 });
if (SECTION === 'cst') {
  await page.goto(`${BASE}/cst/03-local-tax-and-rounding.html`, { waitUntil: 'networkidle0' });
  const calc = async (charge, kind, local) => {
    await page.$eval('#cst-charge', e => e.value = ''); await page.type('#cst-charge', charge);
    await page.select('#cst-kind', kind);
    await page.$eval('#cst-local', e => e.value = ''); if (local) await page.type('#cst-local', local);
    // keyboard submit: focus the button and press Enter
    await page.focus('#cstcalc button'); await page.keyboard.press('Enter');
    await new Promise(r => setTimeout(r, 250));
    return { out: await page.$eval('#cstcalc-out', e => e.textContent.replace(/\s+/g, ' ').trim()), active: await page.evaluate(() => document.activeElement.id), errors: await page.$eval('#cstcalc-errors', e => e.hidden ? '' : e.textContent.replace(/\s+/g, ' ').trim()), chargeInvalid: await page.$eval('#cst-charge', e => e.getAttribute('aria-invalid')) };
  };
  report.calc = { business: await calc('49.99', 'business', '5.22'), residential: await calc('100', 'residential', '5.22'), satellite: await calc('100', 'dths', ''), invalid: await calc('abc', 'business', '5.22') };
  await page.goto(`${BASE}/cst/01-basics.html`, { waitUntil: 'networkidle0' });
} else {
  await page.goto(`${BASE}/sut/01-basics.html`, { waitUntil: 'networkidle0' });
}
report.quiz = await page.evaluate(async () => {
  const fs_ = [...document.querySelectorAll('.quiz fieldset')];
  fs_.forEach(f => { const c = f.querySelector('input[data-correct]') || f.querySelector('input'); c.click(); });
  const btn = document.querySelector('.quiz button'); btn && btn.click();
  await new Promise(r => setTimeout(r, 200));
  return { questions: fs_.length, feedback: [...document.querySelectorAll('.quiz [aria-live], .quiz [role=status]')].map(e => e.textContent.trim().slice(0, 80)) };
});
await page.goto(`${BASE}/${SECTION}/glossary.html`, { waitUntil: 'networkidle0' });
await page.type('#gloss-q', SECTION === 'cst' ? 'resale' : 'surtax'); await new Promise(r => setTimeout(r, 200));
report.glossFilter = await page.$eval('#gloss-status', e => e.textContent);
await page.goto(`${BASE}/${SECTION}/forms.html`, { waitUntil: 'networkidle0' });
await page.type('#forms-q', '700016'); await new Promise(r => setTimeout(r, 200));
report.formsFilter = await page.$eval('#forms-status', e => e.textContent);
await browser.close();
report.links = [...report.links].filter(l => !l.startsWith(BASE));
fs.writeFileSync(`${OUT}/report.json`, JSON.stringify(report, null, 1));
let fails = 0;
const sum = Object.entries(report.pages).map(([p, r]) => { const bad = r.desktopAxe.length + r.mobileAxe.length + (r.mobileOverflow.scrollW > r.mobileOverflow.docW ? 1 : 0) + r.keyboard.noVisibleFocus.length + (r.desktopStatus !== 200) + (r.mobileStatus !== 200); fails += bad; return `${p}: status ${r.desktopStatus} axe ${r.desktopAxe.length}/${r.mobileAxe.length} overflow320 ${r.mobileOverflow.scrollW > r.mobileOverflow.docW ? 'YES ' + r.mobileOverflow.offenders.join(',') : 'no'} kbd-stops ${r.keyboard.stops} kbd-nofocus ${r.keyboard.noVisibleFocus.length} first-tab ${r.firstTab && r.firstTab.txt}`; });
console.log(sum.join('\n'));
console.log('pages', pages.length, 'problems', fails);
console.log('internal broken', report.internalBroken.length, report.internalBroken.slice(0, 10));
console.log('external links', report.links.length, 'console errors', report.consoleErrors.length, report.consoleErrors.slice(0, 5));
console.log('calc', JSON.stringify(report.calc || null));
console.log('quiz', JSON.stringify(report.quiz), '| gloss', report.glossFilter, '| forms', report.formsFilter);
