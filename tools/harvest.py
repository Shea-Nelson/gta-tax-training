#!/usr/bin/env python3
"""Polite SUT harvest of public floridarevenue.com. GET only, robots.txt honored (with wildcards),
one request at a time, ~1.2 s between requests, 20 s timeout, one retry on network error/429/503.
Phase A: scoped page crawl from seeds. Phase B: download SUT-related files. Idempotent: skips files already in manifest."""
import re, json, time, hashlib, sys, os, datetime as dt
from urllib.parse import urljoin, urlparse, urldefrag
import requests
from bs4 import BeautifulSoup

ROOT = '/workspace/gta/sut-training/source'
UA = 'Mozilla/5.0 (X11; Linux x86_64) Chrome/140 Safari/537.36 (FDOR-GTA unofficial SUT training-guide research for Shea Nelson; polite, low-rate)'
DELAY = 1.2
S = requests.Session(); S.headers['User-Agent'] = UA
LOG = open(f'{ROOT}/harvest-log.jsonl', 'a')
def log(**k): k['t'] = dt.datetime.now().isoformat(timespec='seconds'); LOG.write(json.dumps(k) + '\n'); LOG.flush()

# ---- robots (User-agent: * group, wildcard aware, longest match wins, Allow wins ties)
def load_robots():
    txt = S.get('https://floridarevenue.com/robots.txt', timeout=20).text
    open(f'{ROOT}/robots.txt', 'w').write(txt)
    rules, cur = [], False
    for line in txt.splitlines():
        line = line.split('#')[0].strip()
        if not line or ':' not in line: continue
        k, v = [x.strip() for x in line.split(':', 1)]
        if k.lower() == 'user-agent': cur = (v == '*')
        elif cur and k.lower() in ('allow', 'disallow') and v:
            rx = '^' + re.escape(v).replace(r'\*', '.*')
            if rx.endswith(r'\$'): rx = rx[:-2] + '$'
            rules.append((k.lower() == 'allow', len(v), re.compile(rx, re.I)))
    return rules
RULES = None
def allowed(url):
    p = urlparse(url); path = p.path + (('?' + p.query) if p.query else '')
    best = None
    for allow, ln, rx in RULES:
        if rx.match(path) and (best is None or ln > best[1] or (ln == best[1] and allow)): best = (allow, ln)
    return True if best is None else best[0]

last = [0.0]
def get(url, stream=False):
    if not allowed(url): log(url=url, status='robots-disallowed'); return None, 'robots-disallowed'
    for attempt in (1, 2):
        wait = DELAY - (time.time() - last[0])
        if wait > 0: time.sleep(wait)
        last[0] = time.time()
        try:
            r = S.get(url, timeout=20, allow_redirects=True)
            if r.status_code in (429, 503) and attempt == 1: time.sleep(5); continue
            if r.status_code == 403: log(url=url, status=403); print('!! 403 (blocked) at', url, file=sys.stderr)
            return r, r.status_code
        except requests.RequestException as e:
            if attempt == 2: log(url=url, status='neterr', err=str(e)[:200]); return None, 'neterr'
            time.sleep(3)

def norm(u, base=None):
    u = urldefrag(urljoin(base or '', u.strip()))[0]
    p = urlparse(u)
    if p.scheme not in ('http', 'https'): return None
    host = p.netloc.lower().replace('www.', '')
    if host != 'floridarevenue.com': return None
    return 'https://floridarevenue.com' + p.path + (('?' + p.query) if p.query else '')

FILE_RX = re.compile(r'\.(pdf|docx?|xlsx?|pptx?|rtf|csv|txt)$', re.I)
PAGE_SCOPE = re.compile(r'^/(taxes|faq|forms_library/pages|pages)/', re.I)
KW = re.compile(r'sales|use tax|surtax|discretionary|resale|exempt|dealer|tutorial|rent|hotel|transient|motor.?vehicle|holiday|nonprofit|remote|marketplace|out.?of.?state|registration|register|efile|filepay|enroll|audit|refund|penalt|interest|forms|faq|consumer|education|restaurant|contractor|manufactur|admission|incentive|agricultur|boat|aircraft|vessel|seller|schools?|tax_rates|tax_interest', re.I)
SKIP_PAGE = re.compile(r'login\.aspx|/childsupport|/property|reemployment|rt_|fuel|corporate|cit|doc_stamp|estate|severance|pollutant|insurance|ipt|grt_|cst\.aspx|communications|/tips/pages/', re.I)

SEEDS = ['https://floridarevenue.com/taxes/taxesfees/Pages/' + x for x in (
    'sales_tax.aspx', 'discretionary.aspx', 'annual_resale_certificate_sut.aspx', 'dealers_resellers.aspx',
    'sales_tax_incent.aspx', 'tax_interest_rates.aspx', 'local_option.aspx', 'exporter.aspx', 'default.aspx', 'tax_incentives.aspx')] + \
    ['https://floridarevenue.com/taxes/businesses/Pages/' + x for x in ('nonprofit_sales_tax.aspx', 'nonprofit.aspx', 'outstate.aspx', 'seata.aspx', 'sales_schools.aspx', 'newbusiness_startup.aspx', 'fl_gold_seal.aspx')] + \
    ['https://floridarevenue.com/taxes/compliance/Pages/' + x for x in ('audit.aspx', 'refunds.aspx', 'voluntary_disclosure.aspx', 'tax_collection_process.aspx', 'idr.aspx', 'tax_clearance.aspx', 'delinquent_taxpayer.aspx')] + \
    ['https://floridarevenue.com/taxes/eservices/Pages/' + x for x in ('default.aspx', 'filepay.aspx', 'print_resale.aspx', 'registration.aspx', 'enrollment.aspx', 'sutlogin.aspx', 'ooslogin.aspx', 'paymentonly.aspx', 'importinfo.aspx')] + \
    ['https://floridarevenue.com/taxes/Pages/' + x for x in ('default.aspx', 'education.aspx', 'consumer.aspx')] + \
    ['https://floridarevenue.com/taxes/filepayinfo/Pages/' + x for x in ('dash.aspx', 'faq.aspx', 'resources.aspx')] + \
    ['https://floridarevenue.com/taxes/tips/Pages/default.aspx'] + [f'https://floridarevenue.com/taxes/tips/Pages/{y}.aspx' for y in range(1998, 2026)] + \
    ['https://floridarevenue.com/forms_library/Pages/default.aspx', 'https://floridarevenue.com/faq/Pages/default.aspx']

def crawl(max_pages=260):
    pages, files, seen = {}, {}, set()
    queue = [(s, 0, 'seed') for s in SEEDS]
    while queue and len(pages) < max_pages:
        url, depth, via = queue.pop(0)
        key = url.lower()
        if key in seen: continue
        seen.add(key)
        r, st = get(url)
        rec = {'url': url, 'status': st, 'depth': depth, 'via': via}
        if r is None or st != 200 or 'html' not in r.headers.get('content-type', ''):
            pages[url] = rec; log(kind='page', **rec); continue
        soup = BeautifulSoup(r.text, 'lxml')
        rec['finalUrl'] = r.url
        rec['title'] = (soup.title.get_text(' ', strip=True) if soup.title else '')
        h1 = soup.find('h1'); rec['h1'] = h1.get_text(' ', strip=True) if h1 else ''
        main = soup.select_one('#DeltaPlaceHolderMain') or soup.body or soup
        rec['links'] = 0
        for a in main.find_all('a', href=True):
            n = norm(a['href'], r.url)
            if not n: continue
            text = a.get_text(' ', strip=True)[:200]
            rec['links'] += 1
            path = urlparse(n).path
            if FILE_RX.search(path):
                f = files.setdefault(n.lower(), {'url': n, 'texts': [], 'referrers': []})
                if text and text not in f['texts']: f['texts'].append(text)
                if url not in f['referrers']: f['referrers'].append(url)
            elif depth < 2 and PAGE_SCOPE.match(path) and not SKIP_PAGE.search(path) and path.lower().endswith('.aspx') and (KW.search(path) or KW.search(text)):
                queue.append((n, depth + 1, url))
        # keep page text for research
        txt = main.get_text('\n', strip=True)
        h = hashlib.sha256(r.url.lower().encode()).hexdigest()[:16]
        os.makedirs(f'{ROOT}/pages', exist_ok=True)
        open(f'{ROOT}/pages/{h}.txt', 'w').write(f'URL: {r.url}\nTITLE: {rec["title"]}\nFETCHED: {dt.datetime.now().isoformat(timespec="seconds")}\n\n{txt}')
        open(f'{ROOT}/pages/{h}.html', 'w').write(r.text)
        rec['textFile'] = f'pages/{h}.txt'; rec['sha256'] = hashlib.sha256(r.content).hexdigest()
        rec['fetched'] = dt.datetime.now().isoformat(timespec='seconds')
        pages[url] = rec; log(kind='page', url=url, status=st, links=rec['links'])
        print(f'[{len(pages)}] {st} d{depth} {url}', flush=True)
    json.dump(pages, open(f'{ROOT}/pages.json', 'w'), indent=1)
    json.dump(files, open(f'{ROOT}/file-candidates.json', 'w'), indent=1)
    return pages, files

if __name__ == '__main__':
    RULES = load_robots()
    if sys.argv[1:2] == ['crawl']: crawl()

# ---------------- Phase B: classify and download ----------------
BASELINE = '/workspace/gta/se-upgrade-crawl/runs/2026-11-10-120208-broken-links/links.json'
SALES_RX = re.compile(r'sales|use tax|surtax|resale|exempt|dr-?15|dr-?1\b|dr-?13|dr-?5\b|dr-?14|rent|lodging|transient|dealer|admission|holiday|motor vehicle|boat|vessel|aircraft|consumer|refund|audit|penalt|interest|power of attorney|taxpayer|dss|sut|dr15|dr1\b|new dealer|remote|marketplace|out-of-state', re.I)
OTHER_RX = re.compile(r'reemployment|\brt-?\d|rtpart|corporate|income tax|f-?1120|f-?7004|documentary stamp|docstamp|doc stamp|fuel|pollutant|severance|insurance premium|communications services|gross receipts|estate tax|child support|property tax|prepaid wireless|lead-acid|tire fee|dry-cleaning|lake belt|oil production|gas and sulfur|solid mineral|scholarship|tax credit|intangible|ifta|motor fuel|aviation fuel|blender|terminal|wholesaler', re.I)

def classify(url, texts):
    path = urlparse(url).path; low = path.lower(); txt = ' '.join(texts)
    m = re.search(r'tip_(\d\d)([a-z]+\d*)-(\d+)', low)
    if m:
        series = m.group(2).upper()
        return ('tip', series in ('A01', 'A1', 'A15', 'ADM', 'A00'))
    if '/tutorial/' in low:
        return ('tutorial-transcript', not OTHER_RX.search(low + ' ' + txt) and bool(re.search(r'sut|dss|dr15|dr1|voluntary|audit|enroll|estimated|mvd|completing', low + txt, re.I)))
    kind = 'brochure' if '/brochure/' in low else ('form' if '/forms_library/' in low else 'document')
    hay = path + ' ' + txt
    if SALES_RX.search(hay): return (kind, True)
    if OTHER_RX.search(hay): return (kind, False)
    return (kind, True)

def form_number(url, texts):
    t = ' '.join(texts) + ' ' + urlparse(url).path
    m = re.search(r'\b(DR-?\s?\d+[A-Z]*|GT-?\d{6}|TIP\s?#?\s?\d\d[A-Z]+\d*-\d+)\b', t, re.I)
    if m: return m.group(1).upper().replace(' ', '')
    m = re.search(r'/(dr\d+[a-z]*|gt\d{6})\.', urlparse(url).path, re.I)
    if m:
        s = m.group(1).upper(); return re.sub(r'^(DR|GT)', r'\1-', s)
    return ''

def tip_titles():
    out = {}
    for f in os.listdir(f'{ROOT}/pages'):
        if not f.endswith('.html'): continue
        soup = BeautifulSoup(open(f'{ROOT}/pages/{f}').read(), 'lxml')
        for a in soup.find_all('a', href=re.compile(r'TIP_', re.I)):
            tr = a.find_parent('tr')
            row = tr.get_text(' | ', strip=True) if tr else a.get_text(' ', strip=True)
            out[norm(a['href'], 'https://floridarevenue.com/taxes/tips/Pages/') .lower()] = row[:300]
    return out

def download():
    cands = json.load(open(f'{ROOT}/file-candidates.json'))
    for l in json.load(open(BASELINE)):
        n = norm(l['url'])
        if n and FILE_RX.search(urlparse(n).path):
            c = cands.setdefault(n.lower(), {'url': n, 'texts': [], 'referrers': []})
            for t in l.get('linkTexts', []):
                if t and t not in c['texts']: c['texts'].append(t)
            c.setdefault('fromBaseline', True)
    titles = tip_titles()
    mpath = f'{ROOT}/manifest.json'
    manifest = json.load(open(mpath)) if os.path.exists(mpath) else {}
    todo = []
    for k, c in sorted(cands.items()):
        kind, keep = classify(c['url'], c['texts'])
        c['kind'], c['sut'] = kind, keep
        if keep: todo.append(c)
    json.dump(cands, open(f'{ROOT}/file-candidates.json', 'w'), indent=1)
    print('candidates', len(cands), 'sut-related', len(todo), flush=True)
    for i, c in enumerate(todo):
        k = c['url'].lower()
        if k in manifest and manifest[k].get('status') == 200: continue
        r, st = get(c['url'])
        rec = {'url': c['url'], 'kind': c['kind'], 'title': titles.get(k) or (c['texts'][0] if c['texts'] else ''),
               'formNumber': form_number(c['url'], c['texts'] + [titles.get(k, '')]), 'referrers': c['referrers'][:5],
               'status': st, 'fetched': dt.datetime.now().isoformat(timespec='seconds')}
        if r is not None and st == 200:
            sub = {'tip': 'tips', 'form': 'forms', 'brochure': 'brochures', 'tutorial-transcript': 'tutorials'}.get(c['kind'], 'documents')
            os.makedirs(f'{ROOT}/{sub}', exist_ok=True)
            name = os.path.basename(urlparse(r.url).path) or 'file'
            p = f'{ROOT}/{sub}/{name}'
            open(p, 'wb').write(r.content)
            rec.update(path=p.replace(ROOT + '/', ''), bytes=len(r.content), sha256=hashlib.sha256(r.content).hexdigest(),
                       contentType=r.headers.get('content-type', ''), finalUrl=r.url, lastModified=r.headers.get('last-modified', ''))
        manifest[k] = rec; log(kind='file', url=c['url'], status=st)
        print(f'[{i+1}/{len(todo)}] {st} {c["url"]}', flush=True)
        if i % 20 == 0: json.dump(manifest, open(mpath, 'w'), indent=1)
    json.dump(manifest, open(mpath, 'w'), indent=1)

if __name__ == '__main__' and sys.argv[1:2] == ['download']:
    download()
