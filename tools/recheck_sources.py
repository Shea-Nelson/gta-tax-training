#!/usr/bin/env python3
"""Polite one-off re-check of specific public floridarevenue.com URLs (honest UA, robots.txt honored, 1.5 s apart, GET only, stops on 403).
Usage: python3 tools/recheck_sources.py URL [URL ...]  -> prints status and writes tests/out/recheck-<epoch>.json"""
import requests, time, urllib.robotparser, json, re, sys, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests', 'out'); FETCHED = '/tmp/gta-recheck'; os.makedirs(FETCHED, exist_ok=True)
UA='Mozilla/5.0 (X11; Linux x86_64) Chrome/140 Safari/537.36 (FDOR-GTA unofficial training-guide polish re-check for Shea Nelson; polite, low-rate)'
S=requests.Session(); S.headers['User-Agent']=UA
rp=urllib.robotparser.RobotFileParser(); r=S.get('https://floridarevenue.com/robots.txt',timeout=30); rp.parse(r.text.splitlines())
out={}
for u in sys.argv[1:]:
    if not rp.can_fetch(UA,u): out[u]='robots-disallowed'; print(u,'robots'); continue
    time.sleep(1.5)
    try:
        x=S.get(u,timeout=40); out[u]={'status':x.status_code,'len':len(x.content),'lm':x.headers.get('Last-Modified')}
        fn=re.sub(r'[^A-Za-z0-9._-]','_',u)[-120:]; open(f'{FETCHED}/'+fn,'wb').write(x.content)
        if x.status_code==403: print('403 STOP',u); break
    except Exception as e: out[u]=str(e)
    print(u,out[u])
json.dump(out,open(f'{OUT}/recheck-%d.json'%int(time.time()),'w'),indent=1)
