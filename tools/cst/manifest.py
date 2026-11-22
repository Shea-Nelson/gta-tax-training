#!/usr/bin/env python3
"""Enrich source/manifest.json with official titles (TIP year pages, forms index rows) and revision/issue dates read from
the documents, then write source/manifest.csv. Idempotent."""
import json, re, os, glob, csv
from bs4 import BeautifulSoup
R = '/workspace/gta/cst-training/source'
man = json.load(open(f'{R}/manifest.json'))
tips, rows = {}, {}
for f in glob.glob(f'{R}/pages/*.html'):
    s = BeautifulSoup(open(f, errors='ignore').read(), 'lxml')
    for a in s.find_all('a', href=re.compile(r'TIP_\d\d', re.I)):
        tr = a.find_parent('tr')
        if not tr: continue
        cells = [' '.join(td.get_text(' ', strip=True).split()) for td in tr.find_all('td')]
        m = re.search(r'TIP_(\w+-\d+R?)', a['href'], re.I)
        if m: tips[m.group(1).upper()] = cells
    for tr in s.find_all('tr'):
        a = tr.find('a', href=re.compile(r'forms_library/current/.*\.pdf', re.I))
        if not a: continue
        cells = [' '.join(td.get_text(' ', strip=True).split()) for td in tr.find_all(['td', 'th'])]
        rows.setdefault(os.path.basename(a['href']).lower(), cells)
def text_of(rec):
    p = rec.get('path') or ''
    for c in (f'{R}/text/{p.split("/")[0]}/{os.path.basename(p)}.txt', f'{R}/text/law/' + os.path.basename(p).rsplit('.', 1)[0] + '.txt'):
        if os.path.exists(c): return open(c, errors='ignore').read()
    return ''
for rec in man.values():
    if rec.get('status') != 200: continue
    name = os.path.basename(rec['path'])
    m = re.match(r'TIP_(\w+-\d+R?)', name, re.I)
    txt = text_of(rec); date = ''
    if m:
        num = m.group(1).upper(); rec['formNumber'] = 'TIP ' + num
        c = tips.get(num) or tips.get(num.rstrip('R'))
        if c:
            rec['title'] = f'TIP {num}: ' + (c[1] if len(c) > 1 else c[0])
            dm = re.search(r'Issued\s*:?\s*([\d/]+)', c[0]); date = ('issued ' + dm.group(1)) if dm else ''
        if not date:
            dm = re.search(r'(?:Date Issued|DATE ISSUED)\s*:?\s*([A-Za-z]+ \d{1,2}, \d{4}|[\d/]+)', txt); date = ('issued ' + dm.group(1)) if dm else ''
    elif rec['kind'] in ('form', 'brochure'):
        c = rows.get(name.lower())
        if c and len(c) >= 2: rec['formNumber'] = c[0] or rec.get('formNumber', ''); rec['title'] = f'{c[0]}: {c[1]}'
        dm = re.search(r'\b([RN])\.\s?(\d{1,2}/\d{2})\b', txt[:8000])
        if dm: date = ('rev. ' if dm.group(1) == 'R' else 'new ') + dm.group(2)
    elif name.endswith('.pdf'):
        dm = re.search(r'\b(?:Rev(?:ised)?\.?|Updated)\s*:?\s*([A-Za-z]+ \d{4}|\d{1,2}/\d{2,4})', txt[:6000])
        if dm: date = 'rev. ' + dm.group(1)
    if not date and rec.get('lastModified'): date = 'server date ' + rec['lastModified'][5:16]
    rec['date'] = date
    rec['title'] = re.sub(r'^(PDF|Fillable PDF) \(\d+KB\)$', '', rec.get('title', '')) or name
json.dump(man, open(f'{R}/manifest.json', 'w'), indent=1)
with open(f'{R}/manifest.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['url', 'kind', 'formNumber', 'title', 'date', 'status', 'bytes', 'sha256', 'path', 'fetched'])
    for r in sorted(man.values(), key=lambda r: (r['kind'], r['url'])):
        w.writerow([r['url'], r['kind'], r.get('formNumber', ''), r.get('title', ''), r.get('date', ''), r['status'], r.get('bytes', ''), r.get('sha256', ''), r.get('path', ''), r.get('fetched', '')])
from collections import Counter
print(Counter(r['kind'] for r in man.values() if r['status'] == 200), sum(r.get('bytes', 0) for r in man.values()) // 1024, 'KB')
