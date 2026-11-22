#!/usr/bin/env python3
"""Build content/sources.json: hand-listed pages + every downloaded document in the manifest (keyed by form/TIP number)."""
import json, re, os
ROOT='/workspace/gta/sut-training'
FR='https://floridarevenue.com'
pages = {
 'sut-page': ('Florida Sales and Use Tax (DOR webpage)', '/taxes/taxesfees/Pages/sales_tax.aspx', 'SUT page'),
 'dss-page': ('Discretionary Sales Surtax (DOR webpage)', '/taxes/taxesfees/Pages/discretionary.aspx', 'Surtax page'),
 'arc-page': ('Annual Resale Certificate for Sales Tax (DOR webpage)', '/taxes/taxesfees/Pages/annual_resale_certificate_sut.aspx', 'Resale certificate page'),
 'rates-page': ('Florida Tax and Interest Rates (DOR webpage)', '/taxes/taxesfees/Pages/tax_interest_rates.aspx', 'Tax and interest rates page'),
 'local-option-page': ('Local Option Taxes (DOR webpage)', '/taxes/taxesfees/Pages/local_option.aspx', 'Local option taxes page'),
 'incentives-page': ('Sales Tax Incentives (DOR webpage)', '/taxes/taxesfees/Pages/sales_tax_incent.aspx', 'Sales tax incentives page'),
 'dealers-page': ('Retail Dealers and Resellers (DOR webpage)', '/taxes/taxesfees/Pages/dealers_resellers.aspx', 'Dealers page'),
 'nonprofit-page': ('Nonprofit Organizations and Sales and Use Tax (DOR webpage)', '/taxes/businesses/Pages/nonprofit_sales_tax.aspx', 'Nonprofit page'),
 'outstate-page': ('Information for Out-of-State Businesses (DOR webpage)', '/taxes/businesses/Pages/outstate.aspx', 'Out-of-state page'),
 'schools-page': ('Sales Tax Information for Schools (DOR webpage)', '/taxes/businesses/Pages/sales_schools.aspx', 'Schools page'),
 'startup-page': ('New Business Start-up Kit (DOR webpage)', '/taxes/businesses/Pages/newbusiness_startup.aspx', 'Start-up kit page'),
 'audit-page': ('What to Expect from a Florida Tax Audit (DOR webpage)', '/taxes/compliance/Pages/audit.aspx', 'Audit page'),
 'refunds-page': ('Tax Refunds Information (DOR webpage)', '/taxes/compliance/Pages/refunds.aspx', 'Refunds page'),
 'vd-page': ('Voluntary Disclosure of Tax Liabilities (DOR webpage)', '/taxes/compliance/Pages/voluntary_disclosure.aspx', 'Voluntary disclosure page'),
 'collection-page': ('Tax Collection Process (DOR webpage)', '/taxes/compliance/Pages/tax_collection_process.aspx', 'Collection process page'),
 'idr-page': ('Informal Dispute Resolution (DOR webpage)', '/taxes/compliance/Pages/idr.aspx', 'Informal dispute page'),
 'registration-page': ('Account Management and Registration (DOR webpage)', '/taxes/eservices/Pages/registration.aspx', 'Registration page'),
 'filepay-page': ('eFile and Pay Taxes, Fees, and Remittances (DOR webpage)', '/taxes/eservices/Pages/filepay.aspx', 'eFile and Pay page'),
 'enroll-page': ('Enroll to eFile and Pay (DOR webpage)', '/taxes/eservices/Pages/enrollment.aspx', 'Enrollment page'),
 'print-resale-page': ('Print Annual Resale Certificates (DOR webpage)', '/taxes/eservices/Pages/print_resale.aspx', 'Print certificate page'),
 'education-page': ('Taxpayer Education (DOR webpage)', '/taxes/Pages/education.aspx', 'Taxpayer Education page'),
 'tips-page': ('Tax Information Publications (DOR webpage)', '/taxes/tips/Pages/default.aspx', 'TIPs page'),
 'forms-page': ('Forms and Publications (DOR webpage)', '/Pages/forms_index.aspx', 'Forms page'),
 'faq-page': ('Questions and Answers search (DOR webpage)', '/faq/Pages/faqsearch.aspx', 'DOR FAQ'),
 'gta-home': ('General Tax Administration (DOR webpage)', '/taxes/Pages/default.aspx', 'GTA home'),
 'consumer-page': ('Information for Consumers: Use Tax (DOR webpage)', '/taxes/Pages/consumer.aspx', 'Consumer page'),
 'filepayinfo-dash': ('eFile and Pay Information Center (DOR webpage)', '/taxes/filepayinfo/Pages/dash.aspx', 'eFile Information Center'),
 'filepayinfo-resources': ('eFile and Pay Information Center - User Guides and Videos (DOR webpage)', '/taxes/filepayinfo/Pages/resources.aspx', 'eFile user guides page'),
 'sutlogin-page': ('eFile and Pay Sales and Use Tax, Prepaid Wireless Fee, and Solid Waste Fees and Surcharges (DOR webpage)', '/taxes/eservices/Pages/sutlogin.aspx', 'SUT eFile and Pay login page'),
 'paymentonly-page': ('ePay Taxes, Fees, and Remittances (DOR webpage)', '/taxes/eservices/Pages/paymentonly.aspx', 'Payment-only page'),
 'importinfo-page': ('Import File Information for Taxpayers (DOR webpage)', '/taxes/eservices/Pages/importinfo.aspx', 'Import file page'),
 'eservices-page': ('eServices for Taxes, Fees and Other State Remittances (DOR webpage)', '/taxes/eservices/Pages/default.aspx', 'eServices page'),
 'vendor-page': ('Florida Alternative Tax Forms Vendor Information (DOR webpage)', '/taxes/eservices/Pages/vendor.aspx', 'Vendor information page'),
 'filepayinfo-faq': ('eFile and Pay FAQ (DOR webpage)', '/taxes/filepayinfo/Pages/faq.aspx', 'eFile FAQ'),
}
out = {}
for k, (t, u, s) in pages.items(): out[k] = {'title': t, 'url': FR + u, 'short': s, 'kind': 'page'}
# statutes and rules: link only (external, authoritative)
out['ch212'] = {'title': 'Chapter 212, Florida Statutes (Online Sunshine)', 'url': 'https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0200-0299/0212/0212ContentsIndex.html', 'short': 'Ch. 212, F.S.', 'kind': 'law'}
out['r12a1'] = {'title': 'Rule Chapter 12A-1, Florida Administrative Code (flrules.org)', 'url': 'https://www.flrules.org/gateway/ChapterHome.asp?Chapter=12A-1', 'short': 'Rule 12A-1, F.A.C.', 'kind': 'law'}
man = json.load(open(f'{ROOT}/source/manifest.json'))
cat = {}
for r in json.load(open(f'{ROOT}/source/forms-catalog.json')):
    n = re.sub(r'[^a-z0-9]', '', (r.get('number') or '').lower())
    if n and n != 'form': cat.setdefault(n, r)
tips = json.load(open(f'{ROOT}/source/tip-titles.json'))
def text_of(rec):
    sub = rec['path'].split('/')[-2]; base = os.path.basename(rec['path'])
    for cand in (f'{ROOT}/source/text/{sub}/{base}.txt',):
        if os.path.exists(cand): return open(cand, errors='ignore').read()
    return ''
for rec in man.values():
    if rec.get('status') != 200: continue
    name = os.path.basename(rec['path']).rsplit('.', 1)[0]
    key = name.lower()
    fn = rec.get('formNumber') or ''
    title = rec.get('title') or ''
    date = ''
    m = re.match(r'tip_(\w+-\d+)', key)
    txt = text_of(rec)
    if m:
        num = m.group(1).upper(); key = 'tip-' + num.lower(); fn = 'TIP ' + num
        t = tips.get(num)
        if t:
            cells = [' '.join(c.split()) for c in t['cells']]
            title = f'TIP {num}: ' + (cells[1] if len(cells) > 1 else cells[0])
            dm = re.search(r'Issued\s*:?\s*([\d/]+)', cells[0]); date = ('issued ' + dm.group(1)) if dm else ''
            rm = re.search(r'Revised\s*:?\s*([\d/]+)', ' '.join(cells))
            if rm: date += ', revised ' + rm.group(1)
    else:
        n = re.sub(r'[^a-z0-9]', '', key.replace('_fillable', '').replace('_static', ''))
        c = cat.get(n) or cat.get(re.sub(r'_?\d\d$', '', n))
        if c:
            fn = c['number']; title = f"{c['number']}: " + ' '.join(c['title'].split())[:140]
        dm = re.search(r'\b([RN])\.\s?(\d{1,2}/\d{2})\b', txt[:6000])
        if dm: date = ('rev. ' if dm.group(1) == 'R' else 'new ') + dm.group(2)
    sut = bool(re.search(r'sales and use tax|sales tax|discretionary sales surtax|chapter 212|s\. 212|section 212', txt, re.I)) if txt else None
    out[key] = {'title': title or fn or name, 'url': rec['url'], 'short': fn or name, 'kind': rec['kind'], 'date': date, 'path': rec['path'], 'sutRelated': sut}
over = {'dr15dss_26': 'DR-15DSS: Discretionary Sales Surtax Information for Calendar Year 2026', 'dr15dss': 'DR-15DSS: Discretionary Sales Surtax Information for Calendar Year 2025 (file at /current/ path)'}
for k, t in over.items():
    if k in out: out[k]['title'] = t
json.dump(out, open(f'{ROOT}/content/sources.json', 'w'), indent=1)
print(len(out))
