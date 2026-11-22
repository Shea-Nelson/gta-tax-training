import puppeteer from 'puppeteer-core';
const b = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });
const p = await b.newPage(); await p.setViewport({ width: 1280, height: 1000 });
for (const [page, name] of [['03-taxable-exempt', 'module03-flowchart-desktop'], ['06-rates-surtax', 'module06-surtax-desktop'], ['08-filing-paying', 'module08-timeline-desktop'], ['07-certificates', 'module07-resale-desktop']]) {
  await p.goto(`http://127.0.0.1:47123/sut/${page}.html`, { waitUntil: 'networkidle0' });
  const f = await p.$('main figure'); await f.scrollIntoView();
  await p.evaluate(() => window.scrollBy(0, -80));
  await p.screenshot({ path: `out/${name}-v3.png` });
}
await b.close();
