#!/usr/bin/env python3
"""Polite external link check for the CST pages: HEAD (GET fallback), 1.5 s apart, robots.txt honored per host, same UA as the harvest."""
import json, sys, time
sys.path.insert(0, '/workspace/gta/cst-training/tools')
import harvest_cst as H
R = '/workspace/gta/cst-training/repo/tests/out/' + (sys.argv[1] if len(sys.argv) > 1 else 'cst')  # or sut-recheck
links = sorted(set(json.load(open(f'{R}/report.json'))['links']))
res = {}
for u in links:
    if not u.startswith('http'): continue
    try:
        if not H.allowed(u): res[u] = 'robots-disallowed (not checked)'; continue
    except Exception: pass
    time.sleep(H.DELAY)
    try:
        r = H.S.head(u, timeout=20, allow_redirects=True)
        if r.status_code in (403, 404, 405, 400, 501) or r.status_code >= 500:
            time.sleep(H.DELAY); r = H.S.get(u, timeout=20, allow_redirects=True, stream=True); r.close()
        res[u] = r.status_code
    except Exception as e:
        res[u] = 'error: ' + str(e)[:120]
    print(res[u], u, flush=True)
json.dump(res, open(f'{R}/external-links.json', 'w'), indent=1)
bad = {k: v for k, v in res.items() if v != 200}
print('checked', len(res), 'non-200', len(bad)); [print(' ', v, k) for k, v in bad.items()]
