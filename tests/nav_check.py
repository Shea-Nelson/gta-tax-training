#!/usr/bin/env python3
"""Static check of the main navigation on every built page: each page lists Home and both guides, exactly one
tab carries aria-current="page" when the page is a tab target, and module pages mark their guide with section-current."""
import glob, os, re, sys
DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
TOOLS = {'learning-path', 'glossary', 'forms', 'quick-reference', 'sources'}
fails, n = [], 0
for f in sorted(glob.glob(f'{DOCS}/index.html') + glob.glob(f'{DOCS}/*/*.html')):
    rel = os.path.relpath(f, DOCS); sec, name = (rel.split('/') + [''])[:2] if '/' in rel else ('', rel)
    m = re.search(r'<nav class="primary" aria-label="Main"><ul>(.*?)</ul></nav>', open(f).read())
    if not m: fails.append(f'{rel}: no main nav'); continue
    n += 1
    items = re.findall(r'<a href="([^"]+)"([^>]*)>([^<]+)</a>', m.group(1))
    labels = [t for _, _, t in items]
    if labels[:3] != ['Home', 'Sales &amp; Use Tax', 'Communications Services Tax']: fails.append(f'{rel}: tabs {labels[:3]}')
    cur = [(h, t) for h, a, t in items if 'aria-current="page"' in a]
    sc = [(h, t) for h, a, t in items if 'section-current' in a]
    slug = name[:-5] if name else 'index'
    if rel == 'index.html': want = ('index.html', 'Home')
    elif slug == 'index': want = (f'../{sec}/index.html', None)
    elif slug in TOOLS: want = (f'../{sec}/{slug}.html', None)
    else: want = None
    if want:
        if len(cur) != 1 or cur[0][0] != want[0]: fails.append(f'{rel}: aria-current {cur}')
        if sc: fails.append(f'{rel}: unexpected section-current {sc}')
    else:
        if cur: fails.append(f'{rel}: module page has aria-current {cur}')
        if sc != [(f'../{sec}/index.html', sc[0][1] if sc else '')]: fails.append(f'{rel}: section-current {sc}')
    if sec and any(h.startswith(f'../{o}/') for h, _, t in items[3:] for o in ('sut', 'cst') if o != sec): fails.append(f'{rel}: tool tabs point at the other guide')
print(f'nav check: {n} pages, {len(fails)} problems'); [print(' ', x) for x in fails]
sys.exit(1 if fails else 0)
