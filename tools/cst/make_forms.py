#!/usr/bin/env python3
"""Generate content/cst/forms.html from content/cst/sources.json (harvested forms, brochures and documents)."""
import json, html, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = json.load(open(f'{ROOT}/content/cst/sources.json'))
esc = html.escape
GROUPS = [
 ('Registration, returns and payments', [('dr1', 4), ('dr700016', 14), ('dr700016n', 14), ('dr700019', 12), ('dr700033', 13), ('cst-efile-guide', 13), ('cst-direct-file-specs', 13), ('efile-vendor-list', 13)]),
 ('Address assignment and local rates', [('dr700020', 8), ('dr700012', 8), ('dr700002', 8), ('dr700022', 8), ('dr700025', 8), ('dr700026', 8), ('dr700021', 15), ('cst-rate-table', 3), ('cst-distributions', 1)]),
 ('Exemptions, resale and direct pay', [('cst-print-cert-guide', 10), ('dr700030', 12), ('dr700032', 12)]),
 ('Brochures and audit', [('gt800011', 1), ('gt800022', 16), ('gt800023', 16)]),
 ('Related, not specific to CST', [('dr700001', None), ('dr700023', None), ('grt-efile-guide', None), ('dr133', None), ('dr15sw', None), ('dr15swn', None)]),
]
SITE = {p.get('module'): p for p in json.load(open(f'{ROOT}/content/cst/site.json'))['pages'] if p.get('module')}
n = sum(1 for _, g in GROUPS for k, _m in g if k in S)
out = [f'<p>The communications services tax forms, instructions, guides and brochures collected for this guide ({n} items, retrieved November 2026). Links go to the official copy on floridarevenue.com. Always download forms from there, because the Department revises them. {{{{cite:forms-page}}}}</p>',
       '<div class="filter"><label for="forms-q">Filter by form number or keyword</label>',
       '<input id="forms-q" type="search" data-filter="forms-list" aria-describedby="forms-status" autocomplete="off">',
       f'<p id="forms-status" class="meta" role="status">{n} of {n} shown</p></div>', '<div id="forms-list">']
for i, (title, items) in enumerate(GROUPS):
    out.append(f'<h2 id="fsec-{i}">{esc(title)}</h2>')
    out.append(f'<div class="table-wrap" role="region" aria-labelledby="fsec-{i}" tabindex="0"><table><thead><tr><th scope="col">Number</th><th scope="col">Title</th><th scope="col">Revision</th><th scope="col">In this guide</th></tr></thead><tbody>')
    for k, m in items:
        if k not in S: continue
        s = S[k]; t = s['title'].split(': ', 1)[-1] if ': ' in s['title'] else s['title']
        mod = f'<a href="{SITE[m]["slug"]}.html">Module {m}</a>' if m else '—'
        out.append(f'<tr data-item><th scope="row">{esc(s["short"])}</th><td><a href="{esc(s["url"])}">{esc(t)}</a></td><td>{esc(s.get("date","") or "—")}</td><td>{mod}</td></tr>')
    out.append('</tbody></table></div>')
out.append('</div>')
out.append('<p class="small">DR-700014 (Certificate of Registration) and DR-700015 (Annual Resale Certificate) are issued by the Department to each dealer and are not blank forms in the index. {{cite:cst-page}}</p>')
open(f'{ROOT}/content/cst/forms.html', 'w').write('\n'.join(out) + '\n')
print('forms', n)
