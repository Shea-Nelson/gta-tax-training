#!/usr/bin/env python3
"""Generate content/sut/forms.html (filterable form finder) from source/forms-catalog.json."""
import json, html, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cat = json.load(open(f'{ROOT}/source/forms-catalog.json'))
label = {p['slug']: str(p['module']) for p in json.load(open(f'{ROOT}/content/sut/site.json'))['pages'] if p.get('module')}
mods = {  # form number -> module slug where it is taught
 'DR-1': '02-registration', 'DR-1N': '02-registration', 'DR-1A': '02-registration', 'DR-1C': '09-rentals', 'DR-1 TEAM': '12-contractors-manufacturing',
 'DR-5': '07-certificates', 'DR-13': '07-certificates', 'DR-15': '08-filing-paying', 'DR-15N': '08-filing-paying', 'DR-15EZ': '08-filing-paying',
 'DR-15EZN': '08-filing-paying', 'DR-15MO': '05-use-tax', 'DR-15DSS': '06-rates-surtax', 'DR-15TDT': '09-rentals', 'DR-15AIR': '10-vehicles-boats-aircraft',
 'DR-18': '13-admissions', 'DR-18CIN': '13-admissions', 'DR-46NT': '03-taxable-exempt', 'DR-99A': '10-vehicles-boats-aircraft', 'DR-123': '10-vehicles-boats-aircraft',
 'DR-600013': '07-certificates', 'DR-700002': '06-rates-surtax', 'GT-300015': '01-basics', 'GT-800003': '11-food-restaurants', 'GT-800020': '13-admissions',
 'GT-800041': '11-food-restaurants', 'GT-800046': '11-food-restaurants', 'GT-800054': '02-registration', 'GT-800057': '12-contractors-manufacturing',
 'DR-26S': '17-penalties-interest-refunds', 'DR-26SN': '17-penalties-interest-refunds', 'DR-835': '16-records-audits', 'GT-800022': '16-records-audits',
 'DR-600': '08a-efile-pay', 'DR-600TP': '08a-efile-pay', 'DR-654': '08a-efile-pay', 'DR-655': '08a-efile-pay', 'DR-659': '08a-efile-pay',
 'DR-7': '08a-efile-pay', 'DR-841': '08a-efile-pay',
 'GT-800065': '16-records-audits', 'GT-800059': '16-records-audits', 'GT-800061': '16-records-audits', 'GT-800039': '16-records-audits', 'DR-16A': '12-contractors-manufacturing',
}
skip_sub = {'Specific Fuel Tax Forms', 'All Taxes, Except Sales and Use Tax'}
skip_num = re.compile(r'^(RTS?-|F-\d|GT-400401$|DR-156T$|DR-7000(12|20)$|DR-26N?$)')
BROKEN = set()  # links to leave out; verify-taxcerts was 404 on Nov 21, 2026 and 200 again on Nov 22 (issue SUT-B05)
TITLE_FIX = {'ExemptAgricultural': 'Exempt Agricultural'}  # typos copied from the DOR forms index
def fix(h):
    h = h.strip().rstrip('/') if 'verify-taxcerts' in h else h.strip()
    if h.startswith('https://mailto:'): return 'mailto:' + h[len('https://mailto:'):].replace('%20', '').strip().strip('/')
    if h.rstrip('/') == 'http://flrules.org': return 'https://www.flrules.org/'
    return h
groups = {}
for r in cat:
    if r['number'] in ('Form #', '') or r.get('sub') in skip_sub or skip_num.match(r['number']): continue
    sec = r['section'] + (f" — {r['sub']}" if r.get('sub') else '')
    groups.setdefault(sec, []).append(r)
n = sum(len(v) for v in groups.values())
out = [f'''<p>Every form, instruction and brochure listed in the Department's Forms and Publications index under the sections that apply to sales and use tax ({n} entries, retrieved November 2026). Links go to the official copy on floridarevenue.com. Always download forms from there, because the Department revises them. {{{{cite:forms-page}}}}</p>
<p class="small">Not included: reemployment tax, corporate income tax, fuel tax and communications services tax forms that the index lists in the same sections, and refund forms for taxes other than sales and use tax. Where a form is taught in this guide, the last column links to the module.</p>
<div class="filter"><label for="forms-q">Filter by form number or keyword</label>
<input id="forms-q" type="search" data-filter="forms-list" aria-describedby="forms-status" autocomplete="off">
<p id="forms-status" class="meta" role="status">{n} of {n} shown</p></div>
<div id="forms-list">''']
for i, (sec, rows) in enumerate(groups.items()):
    hid = f'fsec-{i}'
    out.append(f'<h2 id="{hid}">{html.escape(sec)}</h2>\n<div class="table-wrap" role="region" aria-labelledby="{hid}" tabindex="0"><table><thead><tr><th scope="col">Number</th><th scope="col">Title</th><th scope="col">Official links</th><th scope="col">In this guide</th></tr></thead><tbody>')
    for r in rows:
        title = ' '.join(r['title'].replace('\ufffd', '–').split())
        for a, b in TITLE_FIX.items(): title = title.replace(a, b)
        links = ' · '.join(f'<a href="{html.escape(l["href"])}">{html.escape(l["label"] or "Link")}<span class="visually-hidden"> for {html.escape(r["number"])}</span></a>' for l in [dict(x, href=fix(x['href'])) for x in r.get('links', []) if x.get('href')] if l['href'] not in BROKEN)
        m = mods.get(r['number'])
        mod = f'<a href="{m}.html">Module {label[m]}</a>' if m else ''
        out.append(f'<tr data-item><th scope="row">{html.escape(r["number"])}</th><td>{html.escape(title)}</td><td>{links}</td><td>{mod}</td></tr>')
    out.append('</tbody></table></div>')
out.append('</div>')
open(f'{ROOT}/content/sut/forms.html', 'w').write('\n'.join(out) + '\n')
print(n, len(groups))
