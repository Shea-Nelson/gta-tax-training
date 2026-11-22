// Featured screenshots for the CST section. Usage (from tests/): node cst/shots-cst.mjs http://127.0.0.1:47124
import puppeteer from 'puppeteer-core';
const BASE = process.argv[2]; const OUT = 'out/cst';
const b = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });
const p = await b.newPage(); await p.setViewport({ width: 1280, height: 900 });
await p.goto(`${BASE}/index.html`, { waitUntil: 'networkidle0' }); await p.screenshot({ path: `${OUT}/home-desktop.png` });
await p.goto(`${BASE}/cst/02-rates.html`, { waitUntil: 'networkidle0' });
let el = await p.$('figure'); await el.screenshot({ path: `${OUT}/module02-rate-stack-desktop.png` });
await p.goto(`${BASE}/cst/03-local-tax-and-rounding.html`, { waitUntil: 'networkidle0' });
await p.type('#cst-charge', '49.99'); await p.select('#cst-kind', 'business'); await p.type('#cst-local', '5.22'); await p.click('#cstcalc button');
await new Promise(r => setTimeout(r, 300)); el = await p.$('#cstcalc'); await el.screenshot({ path: `${OUT}/module03-calculator-desktop.png` });
await p.goto(`${BASE}/cst/14-dr700016.html`, { waitUntil: 'networkidle0' });
el = await p.$('figure'); await el.screenshot({ path: `${OUT}/module14-return-flow-desktop.png` });
await p.setViewport({ width: 320, height: 800, deviceScaleFactor: 2 });
await p.goto(`${BASE}/cst/07-sourcing.html`, { waitUntil: 'networkidle0' }); await p.screenshot({ path: `${OUT}/module07-mobile-320.png` });
await b.close(); console.log('shots ok');
