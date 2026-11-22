#!/usr/bin/env python3
"""Lint the citation registry for labels a learner sees: no raw file names, no line breaks in titles,
no placeholder TIP titles, form numbers hyphenated, and no two cited sources sharing one label within a guide."""
import json, re, os, glob, collections, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'content')
shared = json.load(open(f'{ROOT}/sources.json')); fails = []
for tax in ('sut', 'cst'):
    reg = {**shared, **(json.load(open(f'{ROOT}/{tax}/sources.json')) if os.path.exists(f'{ROOT}/{tax}/sources.json') else {})}
    used = set()
    for f in glob.glob(f'{ROOT}/{tax}/*.html'):
        for m in re.finditer(r'\{\{cite:([^}]+)\}\}', open(f).read()): used |= {k.strip() for k in m.group(1).split(',')}
    by_short = collections.defaultdict(list)
    for k in sorted(used):
        v = reg[k]; t, s = v.get('title', ''), v.get('short', '')
        if re.search(r'\s{2,}|\n', t): fails.append(f'{tax}:{k}: whitespace in title')
        if re.search(r'[a-z][A-Z]|_|\.pdf', s.replace('eFile', 'efile')): fails.append(f'{tax}:{k}: raw label {s!r}')
        if re.match(r'(DR|GT)\d', s): fails.append(f'{tax}:{k}: unhyphenated form number {s!r}')
        if re.search(r'Tax Information Publication #', t): fails.append(f'{tax}:{k}: placeholder TIP title')
        by_short[s].append(k)
    for s, ks in by_short.items():
        if len(ks) > 1: fails.append(f'{tax}: label {s!r} shared by {ks}')
print(f'source label check: {len(fails)} problems'); [print(' ', x) for x in fails]; sys.exit(1 if fails else 0)
