// Render every page at 1280 and 320 px, run axe (WCAG 2.0/2.1/2.2 A+AA), check overflow, focus visibility,
// internal links/anchors, and exercise the quiz + calculator. Usage: node check.mjs http://127.0.0.1:47123
import puppeteer from 'puppeteer-core';
import fs from 'node:fs'; import path from 'node:path';
const BASE = process.argv[2]; const SITE = path.resolve('../docs'); const OUT = 'out';
const axeSrc = fs.readFileSync('node_modules/axe-core/axe.min.js', 'utf8');
const pages = ['index.html', ...fs.readdirSync(`${SITE}/sut`).filter(f => f.endsWith('.html')).map(f => `sut/${f}`)];
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
    const ax = await page.evaluate(async () => (await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] } })).violations.map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length, sample: v.nodes.slice(0, 3).map(n => n.target.join(' ')) })));
    r[`${key}Axe`] = ax;
    r[`${key}Overflow`] = await page.evaluate(() => {
      const docW = document.documentElement.clientWidth; const bad = [];
      document.querySelectorAll('body *').forEach(el => { const b = el.getBoundingClientRect(); if (b.right > docW + 1 && !el.closest('.table-wrap,.figure-scroll') && getComputedStyle(el).position !== 'absolute') bad.push(el.tagName + (el.className ? '.' + el.className : '')); });
      return { scrollW: document.documentElement.scrollWidth, docW, offenders: [...new Set(bad)].slice(0, 8) };
    });
    const safe = p.replace(/[\/.]/g, '_');
    await page.screenshot({ path: `${OUT}/shots/${safe}-${width}.png`, fullPage: width === 320 ? false : false });
    if (width === 1280) {
      // links
      const links = await page.evaluate(() => [...document.querySelectorAll('a[href]')].map(a => a.href));
      links.forEach(l => report.links.add(l));
      // keyboard: tab 25 times, record focus visibility
      const foc = [];
      for (let i = 0; i < 25; i++) {
        await page.keyboard.press('Tab');
        foc.push(await page.evaluate(() => { const e = document.activeElement; if (!e || e === document.body) return null; const s = getComputedStyle(e); return { tag: e.tagName, txt: (e.textContent || '').trim().slice(0, 30), outline: s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) >= 2 }; }));
      }
      r.keyboard = { stops: foc.filter(Boolean).length, noVisibleFocus: foc.filter(f => f && !f.outline).map(f => f.tag + ':' + f.txt) };
      // first focusable is skip link?
      r.firstTab = foc[0];
    }
    await page.close();
  }
}
// internal links + anchors
for (const l of report.links) {
  if (!l.startsWith(BASE)) continue;
  const u = new URL(l); let f = path.join(SITE, decodeURIComponent(u.pathname)); if (f.endsWith('/')) f += 'index.html';
  if (!fs.existsSync(f)) { report.internalBroken.push(l); continue; }
  if (u.hash && u.hash.length > 1) { const h = fs.readFileSync(f, 'utf8'); if (!h.includes(`id="${decodeURIComponent(u.hash.slice(1))}"`)) report.internalBroken.push(l); }
}
// interactions
const page = await browser.newPage(); await page.setViewport({ width: 1280, height: 900 });
await page.goto(`${BASE}/sut/06-rates-surtax.html`, { waitUntil: 'networkidle0' });
await page.$eval('#price', e => e.value = ''); await page.type('#price', '7000');
await page.$eval('#surtax', e => e.value = ''); await page.type('#surtax', '1');
await page.select('#kind', 'tpp');
await page.click('#taxcalc button[type=submit], #taxcalc button');
await new Promise(r => setTimeout(r, 300));
report.calc7000 = await page.$eval('#taxcalc-out', e => e.textContent.replace(/\s+/g, ' ').trim());
await page.$eval('#price', e => e.value = ''); await page.type('#price', 'abc'); await page.click('#taxcalc button');
await new Promise(r => setTimeout(r, 300));
report.calcInvalid = { out: await page.$eval('#taxcalc-out', e => e.textContent.trim()), ariaInvalid: await page.$eval('#price', e => e.getAttribute('aria-invalid')) };
await page.goto(`${BASE}/sut/01-basics.html`, { waitUntil: 'networkidle0' });
report.quiz = await page.evaluate(async () => {
  const fs_ = [...document.querySelectorAll('.quiz fieldset')];
  fs_.forEach(f => { const c = f.querySelector('input[data-correct]') || f.querySelector('input'); c.click(); });
  const btn = document.querySelector('.quiz button'); btn && btn.click();
  await new Promise(r => setTimeout(r, 200));
  return { questions: fs_.length, feedback: [...document.querySelectorAll('.quiz [aria-live], .quiz [role=status]')].map(e => e.textContent.trim().slice(0, 80)) };
});
await page.goto(`${BASE}/sut/glossary.html`, { waitUntil: 'networkidle0' });
await page.type('#gloss-q', 'surtax'); await new Promise(r => setTimeout(r, 200));
report.glossFilter = await page.$eval('#gloss-status', e => e.textContent);
// featured screenshots
await page.goto(`${BASE}/index.html`, { waitUntil: 'networkidle0' }); await page.screenshot({ path: `${OUT}/home-desktop.png` });
await page.goto(`${BASE}/sut/06-rates-surtax.html#surtax-figure`, { waitUntil: 'networkidle0' });
const fig = await page.$('figure svg'); if (fig) { await fig.scrollIntoView(); await page.screenshot({ path: `${OUT}/module06-figure-desktop.png` }); }
await page.setViewport({ width: 320, height: 800, deviceScaleFactor: 2 }); await page.goto(`${BASE}/sut/03-taxable-exempt.html`, { waitUntil: 'networkidle0' }); await page.screenshot({ path: `${OUT}/module03-mobile-320.png` });
await page.emulateMediaType('print'); await page.pdf({ path: `${OUT}/quick-reference-print.pdf`, format: 'Letter' }).catch(() => {});
await browser.close();
report.links = [...report.links].filter(l => !l.startsWith(BASE));
fs.writeFileSync(`${OUT}/report.json`, JSON.stringify(report, null, 1));
const sum = Object.entries(report.pages).map(([p, r]) => `${p}: axe ${r.desktopAxe.length}/${r.mobileAxe.length} overflow320 ${r.mobileOverflow.scrollW > r.mobileOverflow.docW ? 'YES ' + r.mobileOverflow.offenders.join(',') : 'no'} kbd-nofocus ${r.keyboard.noVisibleFocus.length}`);
console.log(sum.join('\n'));
console.log('internal broken', report.internalBroken.length, report.internalBroken.slice(0, 10));
console.log('external links', report.links.length, 'console errors', report.consoleErrors.length, report.consoleErrors.slice(0, 5));
console.log('calc', report.calc7000, '| invalid', JSON.stringify(report.calcInvalid), '| quiz', JSON.stringify(report.quiz), '| gloss', report.glossFilter);
