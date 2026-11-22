#!/usr/bin/env python3
"""Polite external link check for the built site: HEAD (fallback GET), 1.2 s apart, robots honored for floridarevenue.com."""
import json, sys, time, re
sys.path.insert(0, '/workspace/gta/sut-training/tools')
import harvest as H
from urllib.parse import urlparse
H.RULES = H.load_robots()
links = sorted(set(json.load(open('/workspace/gta/sut-training/tests/out/report.json'))['links']))
res = {}
for u in links:
    host = urlparse(u).netloc.lower()
    if u.startswith('mailto:') or u.startswith('tel:'): continue
    if 'floridarevenue.com' in host and host in ('floridarevenue.com', 'www.floridarevenue.com') and not H.allowed(u):
        res[u] = 'robots-disallowed (not checked)'; continue
    time.sleep(H.DELAY)
    try:
        r = H.S.head(u, timeout=20, allow_redirects=True)
        if r.status_code in (403, 405, 400, 501) or r.status_code >= 500:
            time.sleep(H.DELAY); r = H.S.get(u, timeout=20, allow_redirects=True, stream=True); r.close()
        res[u] = r.status_code
    except Exception as e:
        res[u] = 'error: ' + str(e)[:120]
    print(res[u], u, flush=True)
json.dump(res, open('/workspace/gta/sut-training/tests/out/external-links.json', 'w'), indent=1)
bad = {k: v for k, v in res.items() if v != 200}
print('checked', len(res), 'non-200', len(bad)); [print(' ', v, k) for k, v in bad.items()]
