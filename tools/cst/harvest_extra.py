#!/usr/bin/env python3
"""Supplemental CST fetches via the same polite core (harvest_cst.get): full Ch. 202 and s. 203.001 F.S. (Online Sunshine),
Rule 12A-19 Word file (flrules), the 10 CST FAQ answers visible on the public FAQ page (GET FAQDetails only; paging is a POST
postback and is not used), local tax distribution workbook, and the forms-index CST section. Idempotent."""
import sys, os, json, hashlib, datetime as dt, re
sys.path.insert(0, os.path.dirname(__file__))
import harvest_cst as H
from bs4 import BeautifulSoup
R = H.ROOT
man = json.load(open(f'{R}/manifest.json'))
def save(url, kind, sub, name, title, fn=''):
    k = url.lower()
    if k in man and man[k].get('status') == 200: return
    r, st = H.get(url)
    rec = {'url': url, 'kind': kind, 'title': title, 'formNumber': fn, 'status': st, 'fetched': dt.datetime.now().isoformat(timespec='seconds')}
    if r is not None and st == 200:
        os.makedirs(f'{R}/{sub}', exist_ok=True); p = f'{R}/{sub}/{name}'; open(p, 'wb').write(r.content)
        rec.update(path=f'{sub}/{name}', bytes=len(r.content), sha256=hashlib.sha256(r.content).hexdigest(), contentType=r.headers.get('content-type', ''),
                   finalUrl=r.url, lastModified=r.headers.get('last-modified', ''))
    man[k] = rec; print(st, url, flush=True)
LS = 'https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0200-0299/'
save(LS + '0202/0202.html', 'law', 'law', 'ch202-entire.html', 'Chapter 202, Florida Statutes (2026), Communications Services Tax Simplification Law: entire chapter', 'Ch. 202 F.S.')
save(LS + '0203/Sections/0203.001.html', 'law', 'law', 's203.001.html', 'Section 203.001, Florida Statutes: Communications services gross receipts tax', 's. 203.001 F.S.')
save('https://flrules.org/gateway/readFile.asp?sid=0&tid=0&cno=12A-19&caid=1701009&type=4&file=12A-19.doc', 'law', 'law', '12A-19.doc', 'Rule Chapter 12A-19, Florida Administrative Code: Communications Services Tax (Word file)', 'Rule 12A-19 F.A.C.')
for fid in '1270 1271 1276 1281 1316 1319 1356 1284 1294 1369'.split():
    save(f'https://floridarevenue.com/faq/Pages/FAQDetails.aspx?FAQID={fid}', 'faq', 'faq', f'faq-{fid}.html', f'DOR Questions and Answers FAQ #{fid}')
save('https://floridarevenue.com/taxes/Documents/local_tax_distributions.xlsx', 'document', 'documents', 'local_tax_distributions.xlsx', 'Local Tax Distribution Data (workbook linked from the CST page)')
json.dump(man, open(f'{R}/manifest.json', 'w'), indent=1)
