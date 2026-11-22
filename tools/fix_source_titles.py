#!/usr/bin/env python3
"""Replace vague titles ("PDF", "Fillable PDF", "DOC", "memorandum", bare form numbers) in content/sources.json
with real document titles. Order of evidence: the SUT forms catalog row for that exact URL, the CST sources.json
entry for that URL, the PDF's own Title metadata, then the document's first heading lines. Prints every change
(and every candidate in --dry-run) so a person can review; writes source/title-fixes.json as the audit trail."""
import json, re, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUT_SRC = os.environ.get('SUT_SOURCE', '/workspace/gta/sut-training/source')  # harvested SUT files (not in git)
DRY = '--dry-run' in sys.argv
VAGUE = {'pdf', 'fillable pdf', 'doc', 'docx', 'memorandum', 'untitled', ''}
def vague(t): t = (t or '').strip(); return t.lower() in VAGUE or bool(re.fullmatch(r'(DR|GT|RT)-?[0-9A-Z]+', t)) or t.lower().endswith(('.pdf', '.doc', '.docx')) or t.lower().startswith('microsoft word')
def form_no(url):
    b = re.sub(r'\.(pdf|docx?)$', '', url.rsplit('/', 1)[-1], flags=re.I).replace('%20', ' ')
    m = re.fullmatch(r'(dr|gt|rt)[- ]?(\d[\da-z]*?)(_fillable|_\d{4})?', b, re.I)
    return (m.group(1).upper() + '-' + m.group(2).upper(), m.group(3) or '') if m else (None, '')
src = json.load(open(f'{ROOT}/content/sources.json'))
cst = json.load(open(f'{ROOT}/content/cst/sources.json'))
cat = {}
for r in json.load(open(f'{ROOT}/source/forms-catalog.json')):
    for l in r['links']: cat.setdefault(l['href'].lower(), r)
man = {k.lower(): v for k, v in json.load(open(f'{ROOT}/source/manifest.json')).items()}
# Rows of the official forms-library tables in the harvested SUT pages: Form # | Description | links.
from html import unescape
rows = {}
for fn in sorted(os.listdir(f'{SUT_SRC}/pages')) if os.path.isdir(f'{SUT_SRC}/pages') else []:
    if not fn.endswith('.html'): continue
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', open(f'{SUT_SRC}/pages/{fn}', errors='ignore').read(), re.S | re.I):
        cells = [re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', c))).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S | re.I)]
        if len(cells) < 2 or not re.fullmatch(r'[A-Z]{1,4}-[\w-]+( \w+)?', cells[0]) or not cells[1]: continue
        for href in re.findall(r'href="([^"]+)"', tr):
            u = ('https://floridarevenue.com' + href if href.startswith('/') else href).lower()
            rows.setdefault(u, (cells[0], cells[1].replace('\ufffd', '-')))
cst_by_url = {v['url'].lower(): v['title'] for v in cst.values() if not vague(v['title'])}
def pdf_meta(path):
    try: out = subprocess.run(['pdfinfo', path], capture_output=True, text=True, timeout=30).stdout
    except Exception: return ''
    m = re.search(r'^Title:[ \t]*(\S.*)$', out, re.M); return m.group(1).strip() if m else ''
SMALL = {'a', 'an', 'and', 'as', 'at', 'by', 'for', 'from', 'in', 'into', 'of', 'on', 'or', 'the', 'to', 'with', 'without'}
def tidy(t):
    """Metadata titles are sometimes all capitals; set them in title case, keeping form numbers and acronyms."""
    letters = [c for c in t if c.isalpha()]
    if not letters or sum(c.isupper() for c in letters) / len(letters) < 0.8: return t
    out = []
    for i, w in enumerate(t.split(' ')):
        if re.search(r'\d', w) or w in ('VAB', 'TEAM', 'II', 'III', 'XXII', 'XIII'): out.append(w)
        elif i and w.lower() in SMALL: out.append(w.lower())
        else: out.append('-'.join(x[:1] + x[1:].lower() for x in w.split('-')))
    return ' '.join(out)
def clean(t):
    """Drop page boilerplate that the forms tables append to some descriptions."""
    t = re.split(r'\s+(?:This form is for|If you cannot print|The F-1120A can be|Links are provided)', t)[0]
    return re.sub(r'\s+PDF \(\d+KB\)$', '', t).rstrip(' .')
def first_lines(path):
    try: t = subprocess.run(['pdftotext', '-l', '1', '-layout', path, '-'], capture_output=True, text=True, timeout=30).stdout
    except Exception: return []
    return [re.sub(r'\s{2,}', ' | ', l.strip()) for l in t.splitlines() if l.strip()][:12]
MANUAL = json.load(open(f'{ROOT}/source/title-manual.json')) if os.path.exists(f'{ROOT}/source/title-manual.json') else {}
fixes, unresolved = {}, {}
for k, v in src.items():
    if not vague(v['title']): continue
    u = v['url'].lower(); no, suffix = form_no(v['url']); new, how = None, None
    if k in MANUAL:
        new, how = MANUAL[k], 'reviewed by hand'
    elif u in cat and cat[u]['number'] != 'Form #':
        new, how = f"{cat[u]['number']}: {cat[u]['title']}", 'forms catalog'
    elif u in rows:
        new, how = f"{rows[u][0]}: {rows[u][1]}", 'official forms page'
    elif u in cst_by_url:
        new, how = cst_by_url[u], 'CST sources'
    else:
        e = man.get(u); path = f"{SUT_SRC}/{e['path']}" if e and e.get('path') else None
        if path and os.path.exists(path) and path.lower().endswith('.pdf'):
            t = tidy(re.sub(r'\s+', ' ', pdf_meta(path)))
            if t and not vague(t) and len(t) > 8 and not re.search(r'\.(indd|docx?|pdf)$|^[\w-]+$', t, re.I):
                new, how = (f'{no}: {t}' if no and no.replace('-', '').lower() not in t.replace('-', '').lower() else t), 'PDF metadata'
            else:
                unresolved[k] = {'url': v['url'], 'path': path, 'meta': t, 'lines': first_lines(path)}
        else:
            unresolved[k] = {'url': v['url'], 'path': path, 'meta': '', 'lines': []}
    if new:
        new = clean(new)
        if suffix == '_fillable': new += ' (fillable)'
        fixes[k] = {'old': v['title'], 'new': new, 'how': how}
for k, f in fixes.items(): print(f"{f['how']:>32} | {k} | {f['old']} -> {f['new']}")
print(f'fixed {len(fixes)}, unresolved {len(unresolved)}')
if DRY:
    json.dump(unresolved, open('/tmp/title-unresolved.json', 'w'), indent=1); sys.exit()
for k, f in fixes.items(): src[k]['title'] = f['new']
json.dump(src, open(f'{ROOT}/content/sources.json', 'w'), indent=1, ensure_ascii=False)
json.dump({'fixes': fixes, 'unresolved': sorted(unresolved)}, open(f'{ROOT}/source/title-fixes.json', 'w'), indent=1, ensure_ascii=False)
