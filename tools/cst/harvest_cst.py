#!/usr/bin/env python3
"""Polite CST harvest of public floridarevenue.com (+ pointmatch subdomain, Online Sunshine ch.202, flrules 12A-19).
GET only; robots.txt honored per host; one request at a time, 1.5 s apart; 20 s timeout; one retry on neterr/429/503.
Never signs in. Stops (exit 3) on the first 403 so a block is reported, not worked around. Idempotent: skips files already
in manifest with status 200.  Usage: harvest_cst.py crawl | download | all"""
import re, json, time, hashlib, sys, os, datetime as dt
from urllib.parse import urljoin, urlparse, urldefrag
import requests
from bs4 import BeautifulSoup

ROOT = '/workspace/gta/cst-training/source'
UA = 'Mozilla/5.0 (X11; Linux x86_64) Chrome/140 Safari/537.36 (FDOR-GTA unofficial CST training-guide research for Shea Nelson; polite, low-rate)'
DELAY = 1.5
S = requests.Session(); S.headers['User-Agent'] = UA
os.makedirs(ROOT, exist_ok=True)
LOG = open(f'{ROOT}/harvest-log.jsonl', 'a')
def log(**k): k['t'] = dt.datetime.now().isoformat(timespec='seconds'); LOG.write(json.dumps(k) + '\n'); LOG.flush()

HOSTS = {'floridarevenue.com', 'pointmatch.floridarevenue.com', 'www.leg.state.fl.us', 'www.flrules.org', 'flrules.org'}
ROBOTS = {}
def robots(host):
    if host in ROBOTS: return ROBOTS[host]
    rules = []
    try:
        r = S.get(f'https://{host}/robots.txt', timeout=20)
        txt = r.text if r.status_code == 200 and 'html' not in r.headers.get('content-type', '') else ''
    except requests.RequestException: txt = ''
    open(f'{ROOT}/robots-{host}.txt', 'w').write(txt or '(none / not served)')
    cur = False
    for line in txt.splitlines():
        line = line.split('#')[0].strip()
        if not line or ':' not in line: continue
        k, v = [x.strip() for x in line.split(':', 1)]
        if k.lower() == 'user-agent': cur = (v == '*')
        elif cur and k.lower() in ('allow', 'disallow') and v:
            rx = '^' + re.escape(v).replace(r'\*', '.*')
            if rx.endswith(r'\$'): rx = rx[:-2] + '$'
            rules.append((k.lower() == 'allow', len(v), re.compile(rx, re.I)))
    ROBOTS[host] = rules; return rules

def allowed(url):
    p = urlparse(url); path = p.path + (('?' + p.query) if p.query else '')
    best = None
    for allow, ln, rx in robots(p.netloc.lower()):
        if rx.match(path) and (best is None or ln > best[1] or (ln == best[1] and allow)): best = (allow, ln)
    return True if best is None else best[0]

last = [0.0]
def get(url):
    if urlparse(url).netloc.lower() not in HOSTS: return None, 'out-of-scope'
    if not allowed(url): log(url=url, status='robots-disallowed'); return None, 'robots-disallowed'
    for attempt in (1, 2):
        wait = DELAY - (time.time() - last[0])
        if wait > 0: time.sleep(wait)
        last[0] = time.time()
        try:
            r = S.get(url, timeout=20, allow_redirects=True)
            if r.status_code in (429, 503) and attempt == 1: time.sleep(6); continue
            if r.status_code == 403:
                log(url=url, status=403); print('!! 403 (blocked) at', url, '- stopping per policy', file=sys.stderr); sys.exit(3)
            if 'login' in r.url.lower() and 'login' not in url.lower(): log(url=url, status='login-wall'); return None, 'login-wall'
            return r, r.status_code
        except requests.RequestException as e:
            if attempt == 2: log(url=url, status='neterr', err=str(e)[:200]); return None, 'neterr'
            time.sleep(3)

def norm(u, base=None):
    u = urldefrag(urljoin(base or '', u.strip()))[0]
    p = urlparse(u)
    if p.scheme not in ('http', 'https'): return None
    host = p.netloc.lower()
    if host == 'www.floridarevenue.com': host = 'floridarevenue.com'
    if host not in HOSTS: return None
    return f'https://{host}' + p.path + (('?' + p.query) if p.query else '')

FILE_RX = re.compile(r'\.(pdf|docx?|xlsx?|pptx?|rtf|csv|txt|zip)$', re.I)
CST_RX = re.compile(r'communications? services?|\bcst\b|cst[_-]|a19-|dr-?7000\d\d|gt-?800011|gt-?800022|direct.to.home|prepaid calling|situs|pointmatch|address/jurisdiction|jurisdiction database|chapter 202|12a-19|gross receipts', re.I)
FOLLOW_RX = re.compile(r'cst|communication|faqsearch\.aspx\?cat=4|filepay|tax_interest|refund|audit|print_resale|resale|education|registration|tutorial|pointmatch|forms_index|/tips/pages/(default|20\d\d)', re.I)
SKIP_RX = re.compile(r'login|logon|/childsupport|/property|account|signin', re.I)

SEEDS = ['https://floridarevenue.com/taxes/taxesfees/Pages/cst.aspx',
         'https://floridarevenue.com/taxes/eservices/Pages/cstlogin.aspx',
         'https://floridarevenue.com/taxes/eservices/Pages/filepay.aspx',
         'https://floridarevenue.com/taxes/eservices/Pages/print_resale.aspx',
         'https://floridarevenue.com/taxes/eservices/Pages/registration.aspx',
         'https://floridarevenue.com/Pages/forms_index.aspx',
         'https://floridarevenue.com/faq/Pages/FAQSearch.aspx?Cat=4&Subcat=25',
         'https://floridarevenue.com/taxes/taxesfees/Pages/tax_interest_rates.aspx',
         'https://floridarevenue.com/taxes/compliance/Pages/refunds.aspx',
         'https://floridarevenue.com/taxes/compliance/Pages/audit.aspx',
         'https://floridarevenue.com/taxes/Pages/education.aspx',
         'https://floridarevenue.com/taxes/taxesfees/Pages/default.aspx',
         'https://pointmatch.floridarevenue.com/Default.aspx',
         'https://pointmatch.floridarevenue.com/General/CommunicationsServicesTaxRates.aspx',
         'https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0200-0299/0202/0202ContentsIndex.html',
         'https://www.flrules.org/gateway/ChapterHome.asp?Chapter=12A-19',
         'https://floridarevenue.com/taxes/tips/Pages/default.aspx'] + \
        [f'https://floridarevenue.com/taxes/tips/Pages/{y}.aspx' for y in range(2001, 2027)]

def save_page(url, r, soup):
    main = soup.select_one('#DeltaPlaceHolderMain') or soup.body or soup
    txt = main.get_text('\n', strip=True)
    h = hashlib.sha256(r.url.lower().encode()).hexdigest()[:16]
    os.makedirs(f'{ROOT}/pages', exist_ok=True)
    open(f'{ROOT}/pages/{h}.txt', 'w').write(f'URL: {r.url}\nTITLE: {soup.title.get_text(" ", strip=True) if soup.title else ""}\nFETCHED: {dt.datetime.now().isoformat(timespec="seconds")}\n\n{txt}')
    open(f'{ROOT}/pages/{h}.html', 'w').write(r.text)
    return main, f'pages/{h}.txt', txt

def crawl(max_pages=220):
    pp = f'{ROOT}/pages.json'
    pages = json.load(open(pp)) if os.path.exists(pp) else {}
    files = {}
    queue = [(s, 0, 'seed') for s in SEEDS]; seen = set()
    while queue and len(pages) < max_pages:
        url, depth, via = queue.pop(0)
        if url.lower() in seen: continue
        seen.add(url.lower())
        if url in pages and pages[url].get('status') == 200 and os.path.exists(f"{ROOT}/{pages[url].get('textFile','x')}"):
            soup = BeautifulSoup(open(f"{ROOT}/{pages[url]['textFile'].replace('.txt','.html')}").read(), 'lxml'); final = pages[url].get('finalUrl', url)
        else:
            r, st = get(url)
            rec = {'url': url, 'status': st, 'depth': depth, 'via': via}
            if r is None or st != 200 or 'html' not in r.headers.get('content-type', ''):
                pages[url] = rec; log(kind='page', **rec); print(f'[{len(pages)}] {st} {url}', flush=True); continue
            soup = BeautifulSoup(r.text, 'lxml'); final = r.url
            main, tf, txt = save_page(url, r, soup)
            h1 = soup.find('h1')
            rec.update(finalUrl=r.url, title=soup.title.get_text(' ', strip=True) if soup.title else '', h1=h1.get_text(' ', strip=True) if h1 else '',
                       textFile=tf, sha256=hashlib.sha256(r.content).hexdigest(), fetched=dt.datetime.now().isoformat(timespec='seconds'),
                       lastModified=r.headers.get('last-modified', ''), cst=bool(CST_RX.search(txt)))
            pages[url] = rec; log(kind='page', url=url, status=st)
            print(f'[{len(pages)}] {st} d{depth} {url}', flush=True)
        main = soup.select_one('#DeltaPlaceHolderMain') or soup.body or soup
        for a in main.find_all('a', href=True):
            n = norm(a['href'], final)
            if not n: continue
            text = a.get_text(' ', strip=True)[:200]
            ctx = a.find_parent(['tr', 'li', 'p'])
            ctxt = ctx.get_text(' ', strip=True)[:300] if ctx else text
            if FILE_RX.search(urlparse(n).path):
                f = files.setdefault(n.lower(), {'url': n, 'texts': [], 'context': [], 'referrers': []})
                if text and text not in f['texts']: f['texts'].append(text)
                if ctxt and ctxt not in f['context']: f['context'].append(ctxt)
                if url not in f['referrers']: f['referrers'].append(url)
            elif depth < 2 and not SKIP_RX.search(n) and (FOLLOW_RX.search(n) or CST_RX.search(text)) and \
                    ('floridarevenue.com' in n and ('.aspx' in n.lower()) or 'leg.state.fl.us' in n and '0202/' in n or 'flrules' in n and '12A-19' in n):
                if not re.search(r'/tips/pages/(19|20)\d\d', n, re.I) or depth == 0 and via == 'seed' and False:
                    queue.append((n, depth + 1, url))
    json.dump(pages, open(pp, 'w'), indent=1)
    json.dump(files, open(f'{ROOT}/file-candidates.json', 'w'), indent=1)
    print('pages', len(pages), 'file candidates', len(files))

def kind_of(url):
    low = url.lower()
    if '/tips/' in low: return 'tip'
    if '/brochure/' in low: return 'brochure'
    if '/forms_library/' in low: return 'form'
    if '/tutorial' in low: return 'tutorial'
    if 'leg.state.fl.us' in low or 'flrules' in low: return 'law'
    return 'document'

def is_cst(c):
    hay = urlparse(c['url']).path + ' ' + ' '.join(c['texts']) + ' ' + ' '.join(c['context'])
    if re.search(r'tip_\d\d[a-z]+\d*-', c['url'], re.I):
        return bool(re.search(r'a19-', c['url'], re.I)) or bool(re.search(r'communications? services', ' '.join(c['context']), re.I))
    return bool(CST_RX.search(hay))

def form_number(url, texts):
    t = ' '.join(texts) + ' ' + urlparse(url).path
    m = re.search(r'\b(DR-?\s?\d{3,6}[A-Z]*|GT-?\d{6}|TIP\s?#?\s?\d\d[A-Z]+\d*-\d+R?)\b', t, re.I)
    if m: return m.group(1).upper().replace(' ', '')
    m = re.search(r'/(dr\d+[a-z]*|gt\d{6})\.', urlparse(url).path, re.I)
    if m: return re.sub(r'^(DR|GT)', r'\1-', m.group(1).upper())
    m = re.search(r'TIP_(\d\d[A-Z]+\d*-\d+R?)', url, re.I)
    return ('TIP #' + m.group(1).upper()) if m else ''

def download():
    cands = json.load(open(f'{ROOT}/file-candidates.json'))
    base = '/workspace/gta/se-upgrade-crawl/runs/2026-11-10-120208-broken-links/links.json'
    if os.path.exists(base):
        for l in json.load(open(base)):
            n = norm(l['url'])
            if n and FILE_RX.search(urlparse(n).path):
                c = cands.setdefault(n.lower(), {'url': n, 'texts': [], 'context': [], 'referrers': []})
                for t in l.get('linkTexts', []):
                    if t and t not in c['texts']: c['texts'].append(t)
    mpath = f'{ROOT}/manifest.json'
    manifest = json.load(open(mpath)) if os.path.exists(mpath) else {}
    todo = [c for c in cands.values() if is_cst(c)]
    print('candidates', len(cands), 'cst-related', len(todo), flush=True)
    for i, c in enumerate(sorted(todo, key=lambda c: c['url'])):
        k = c['url'].lower()
        if k in manifest and manifest[k].get('status') == 200: continue
        r, st = get(c['url'])
        kind = kind_of(c['url'])
        title = next((x for x in c['context'] if len(x) > 8), '') or (c['texts'][0] if c['texts'] else '')
        rec = {'url': c['url'], 'kind': kind, 'title': re.sub(r'\s+', ' ', title)[:300], 'formNumber': form_number(c['url'], c['texts']),
               'referrers': c['referrers'][:5], 'status': st, 'fetched': dt.datetime.now().isoformat(timespec='seconds')}
        if r is not None and st == 200:
            sub = {'tip': 'tips', 'form': 'forms', 'brochure': 'brochures', 'tutorial': 'tutorials'}.get(kind, 'documents')
            os.makedirs(f'{ROOT}/{sub}', exist_ok=True)
            name = os.path.basename(urlparse(r.url).path) or 'file'
            p = f'{ROOT}/{sub}/{name}'
            open(p, 'wb').write(r.content)
            rec.update(path=p.replace(ROOT + '/', ''), bytes=len(r.content), sha256=hashlib.sha256(r.content).hexdigest(),
                       contentType=r.headers.get('content-type', ''), finalUrl=r.url, lastModified=r.headers.get('last-modified', ''))
        manifest[k] = rec; log(kind='file', url=c['url'], status=st)
        print(f'[{i+1}/{len(todo)}] {st} {c["url"]}', flush=True)
        if i % 15 == 0: json.dump(manifest, open(mpath, 'w'), indent=1)
    json.dump(manifest, open(mpath, 'w'), indent=1)

if __name__ == '__main__':
    a = sys.argv[1:2]
    if a in (['crawl'], ['all']): crawl()
    if a in (['download'], ['all']): download()
