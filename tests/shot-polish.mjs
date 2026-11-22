// Before/after screenshots for the polish pass. Usage: node shot-polish.mjs before|after  (serves ../docs on :47139)
import puppeteer from 'puppeteer-core';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const tag = process.argv[2] || 'after'; const root = path.resolve('../docs');
const srv = http.createServer((q, r) => { let f = path.join(root, decodeURIComponent(q.url.split('?')[0])); if (f.endsWith('/')) f += 'index.html'; if (process.env.CSS_OVERRIDE && f.endsWith('site.css')) f = process.env.CSS_OVERRIDE;
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': f.endsWith('.css') ? 'text/css' : f.endsWith('.js') ? 'text/javascript' : f.endsWith('.svg') ? 'image/svg+xml' : 'text/html' }); r.end(d); }); }).listen(47139);
const b = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });
const p = await b.newPage();
async function shot(url, sel, name, width = 1280, prep) {
  await p.setViewport({ width, height: width < 600 ? 900 : 1000 });
  await p.goto(`http://127.0.0.1:47139/${url}`, { waitUntil: 'networkidle0' });
  if (prep) await prep();
  const el = await p.evaluateHandle(s => s.startsWith('css:') ? document.querySelector(s.slice(4)) : [...document.querySelectorAll('h2,h3,.box-title')].find(e => e.textContent.trim().startsWith(s)), sel);
  const top = await el.evaluate(e => e.getBoundingClientRect().top + window.scrollY - 60);
  const vh = width < 600 ? 900 : 1000;
  await p.screenshot({ path: `out/polish/${name}-${tag}.png`, clip: { x: 0, y: Math.max(0, top), width, height: vh }, captureBeyondViewport: true });
}
await shot('cst/16-refunds-audits-penalties.html', 'Interest', 'cst16-interest-desktop');
await shot('cst/02-rates.html', 'The residential household exemption', 'cst02-residential-exemption-desktop');
await shot('cst/10-resale.html', 'css:fieldset[data-question]', 'cst10-quiz-feedback-mobile-320', 320, async () => {
  await p.evaluate(() => { const fs = document.querySelector('fieldset[data-question]'); fs.querySelector('input[data-correct]').click(); fs.querySelector('[data-check]').click(); });
});
async function top(url, name) { await p.setViewport({ width: 320, height: 900 }); await p.goto(`http://127.0.0.1:47139/${url}`, { waitUntil: 'networkidle0' }); await p.screenshot({ path: `out/polish/${name}-${tag}.png` }); }
await top('cst/10-resale.html', 'cst10-page-top-mobile-320');
await b.close(); srv.close();
