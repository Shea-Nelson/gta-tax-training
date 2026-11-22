#!/usr/bin/env python3
"""Build repo content/cst/sources.json: hand-listed CST pages, statute/rule deep links, and every harvested CST document
(keys: form number lowercase without dash, tip-<num>, faq-<id>). Shared keys in content/sources.json win at build time."""
import json, re, os
R = '/workspace/gta/cst-training/source'; OUT = '/workspace/gta/cst-training/repo/content/cst/sources.json'
FR = 'https://floridarevenue.com'
out = {}
def add(k, title, url, short, kind='page', date=''):
    out[k] = {'title': title, 'url': url, 'short': short, 'kind': kind, **({'date': date} if date else {})}
for k, t, u, s in [
    ('cst-page', 'Florida Communications Services Tax (DOR webpage)', '/taxes/taxesfees/Pages/cst.aspx', 'CST page'),
    ('cstlogin-page', 'eFile and Pay Communications Services Tax (DOR webpage)', '/taxes/eservices/Pages/cstlogin.aspx', 'CST eFile and Pay page'),
    ('cst-faq-page', 'Communications Services Tax Questions and Answers (DOR FAQ search)', '/faq/Pages/FAQSearch.aspx?Cat=4&Subcat=25', 'CST FAQ'),
    ('grt-utility-page', 'Gross Receipts Tax on Electrical Power and Gas (DOR webpage)', '/taxes/taxesfees/Pages/grt_utility.aspx', 'GRT page')]:
    add(k, t, FR + u, s)
add('pointmatch', 'Address/Jurisdiction Database (PointMatch)', 'https://pointmatch.floridarevenue.com/Default.aspx', 'Address/Jurisdiction Database')
add('cst-rate-page', 'Communications Services Tax Rate Table (PointMatch)', 'https://pointmatch.floridarevenue.com/General/CommunicationsServicesTaxRates.aspx', 'CST rate table')
add('pointmatch-files', 'Master Address List Downloads (PointMatch)', 'https://pointmatch.floridarevenue.com/General/AddressFiles.aspx', 'Address file downloads')
LS = 'https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0200-0299/'
add('ch202', 'Chapter 202, Florida Statutes (Online Sunshine)', LS + '0202/0202ContentsIndex.html', 'Ch. 202, F.S.', 'law')
for s in ['202.11', '202.18', '202.193', '202.12', '202.12001', '202.125', '202.14', '202.151', '202.155', '202.16', '202.17', '202.175', '202.177', '202.19', '202.20', '202.21', '202.22', '202.23', '202.24', '202.27', '202.28', '202.29', '202.30', '202.33', '202.34', '202.35', '202.37']:
    add('s' + s.replace('.', '-'), f'Section {s}, Florida Statutes (Online Sunshine)', LS + f'0202/Sections/0{s}.html', f's. {s}, F.S.', 'law')
add('s203-01', 'Section 203.01, Florida Statutes (Online Sunshine)', LS + '0203/Sections/0203.01.html', 's. 203.01, F.S.', 'law')
add('s203-001', 'Section 203.001, Florida Statutes (Online Sunshine)', LS + '0203/Sections/0203.001.html', 's. 203.001, F.S.', 'law')
add('s212-05', 'Section 212.05, Florida Statutes (Online Sunshine)', LS + '0212/Sections/0212.05.html', 's. 212.05, F.S.', 'law')
add('r12a19', 'Rule Chapter 12A-19, Florida Administrative Code (flrules.org)', 'https://www.flrules.org/gateway/ChapterHome.asp?Chapter=12A-19', 'Rule 12A-19, F.A.C.', 'law')
for n in ['010', '020', '030', '041', '042', '043', '050', '060', '070', '071', '072', '073', '080', '100']:
    add(f'r12a19-{n}', f'Rule 12A-19.{n}, Florida Administrative Code (flrules.org)', f'https://www.flrules.org/gateway/ruleNo.asp?id=12A-19.{n}', f'Rule 12A-19.{n}, F.A.C.', 'law')
man = json.load(open(f'{R}/manifest.json'))
for rec in man.values():
    if rec.get('status') != 200 or rec['kind'] == 'law': continue
    name = os.path.basename(rec['path']).rsplit('.', 1)[0].lower()
    date = rec.get('date', '')
    if date.startswith('server date'): date = ''
    if rec['kind'] == 'tip':
        num = rec['formNumber'][4:]; key = 'tip-' + num.lower().rstrip('r') if num.endswith('R') else 'tip-' + num.lower()
        add(key, rec['title'], rec['url'], 'TIP ' + num, 'tip', date)
    elif rec['kind'] == 'faq':
        fid = name.split('-')[-1]
        q = open(f'{R}/text/faq/faq-{fid}.html.txt').readline().strip()
        add(f'faq-{fid}', f'DOR Questions and Answers: “{q}”', rec['url'], 'DOR FAQ', 'faq')
    else:
        key = {'cst_rate_table': 'cst-rate-table', 'local_tax_distributions': 'cst-distributions', 'efilepayguide-cst': 'cst-efile-guide',
               'flcstdirfilespecs': 'cst-direct-file-specs', 'printcstresalecert': 'cst-print-cert-guide', 'efilepayguide-grt': 'grt-efile-guide',
               'fl_efilevendor': 'efile-vendor-list'}.get(name, name)
        if key == 'dr700033': continue
        if key == 'dr700033static': key = 'dr700033'
        fn = rec.get('formNumber') or ''
        short = fn if re.match(r'(DR|GT)-', fn) else {'cst-rate-table': 'CST rate workbook', 'cst-distributions': 'Local distribution data', 'cst-efile-guide': 'CST eFile guide',
                 'cst-direct-file-specs': 'Direct File specifications', 'cst-print-cert-guide': 'Printing guide', 'grt-efile-guide': 'GRT eFile guide', 'efile-vendor-list': 'eFile vendor list'}.get(key, key)
        title = rec['title']
        if key == 'cst-rate-table': title = 'Local Communications Services Tax Rate Table with Historical Data (workbook, “Rates with Hist Data Jan 2026”)'
        if key == 'gt800023': title = 'GT-800023: Sales and Use/Communications Services Tax Audit Timeline'
        add(key, title, rec['url'], short, rec['kind'], date)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, 'w'), indent=1, ensure_ascii=False)
shared = json.load(open('/workspace/gta/cst-training/repo/content/sources.json'))
coll = sorted(k for k in out if k in shared)
print(len(out), 'keys; collisions with shared (shared wins):', coll)
for k in coll:
    if shared[k]['url'] != out[k]['url']: print('  URL differs', k, shared[k]['url'], out[k]['url'])
