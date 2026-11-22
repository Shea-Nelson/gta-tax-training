#!/usr/bin/env python3
"""Spot-check guide facts against the harvested source text: each claim must match a regex in its cited source."""
import re, glob, sys
S = '/workspace/gta/sut-training/source'
def txt(rel):
    p = rel if rel.startswith('/') else f'{S}/{rel}'
    if p.endswith('.pdf') and not glob.glob(p + '.txt'):
        import subprocess; return re.sub(r'\s+', ' ', subprocess.run(['pdftotext', p, '-'], capture_output=True, text=True).stdout)
    return re.sub(r'\s+', ' ', open(glob.glob(p + '.txt')[0] if glob.glob(p + '.txt') else p, errors='ignore').read())
def page(url):
    for f in glob.glob(f'{S}/pages/*.txt'):
        with open(f, errors='ignore') as h:
            if h.readline().strip() == f'URL: {url}': return re.sub(r'\s+', ' ', h.read())
    raise SystemExit('missing page ' + url)
SUT = 'https://floridarevenue.com/taxes/taxesfees/Pages/sales_tax.aspx'
checks = [
 ('State rate 6%; mobile homes 3%; amusement 4%; electricity 6.95%', lambda: page(SUT), r"general state sales tax rate is 6% with the following exceptions: Retail sales of new mobile homes – 3% Amusement machine receipts – 4% Electricity – 6.95%"),
 ('$5,000 example: $420 + $50 = $470', lambda: txt('forms/gt300015.pdf'), r"\$470"),
 ('Rounding: third decimal > 4 rounds up', lambda: txt('tips/TIP_21A01-02.pdf'), r"greater than 4"),
 ('Remote seller threshold over $100,000', lambda: txt('tips/TIP_21A01-03.pdf'), r"exceeds \$100,000"),
 ('Commercial rent repeal Oct 1, 2025', lambda: txt('tips/TIP_25A01-04.pdf'), r"Effective October 1, 2025, the state sales tax imposed on rent"),
 ('Collection allowance 2.5% of first $1,200', lambda: txt('text/forms/dr15n.pdf'), r"2\.5% \(\.025\) of the .{0,40}first \$1,200 of the Amount Due \(Line 10\), not to exceed \$30"),
 ('Penalty 10% of Line 10, $50 minimum', lambda: txt('text/forms/dr15n.pdf'), r"minimum of \$50 if 10% of Line 10 is less than \$50"),
 ('E-payment by 5 p.m. ET business day before the 20th', lambda: txt('text/forms/dr15n.pdf'), r"5 p\.m\. ET on the business day prior to the 20th"),
 ('Filing frequency over $1,000 monthly', lambda: page(SUT), r"More than \$1,000 Monthly \$501 - \$1,000 Quarterly \$101 - \$500 Semiannual \$100 or less Annual"),
 ('Telefile 800-550-6713', lambda: txt('text/forms/dr15n.pdf'), r"800-550-6713"),
 ('Records three years (DR-15EZN; DR-15N has the same sentence split by columns)', lambda: txt('text/forms/dr15ezn.pdf'), r"three years from the date you file your return or the date it is required to be filed"),
 ('Final return within 15 days', lambda: txt('forms/gt300015.pdf'), r"within 15 days after closing or selling"),
 ('Resale certificates expire Dec 31', lambda: page(SUT), r"Certificates expire on December 31"),
 ('Interest 11% Jul-Dec 2026, factor 0.000301370', lambda: txt('tips/TIP_26ADM-02.pdf'), r"July 1, 2026, through December 31, 2026, is 11%\. The daily interest rate factor to be used for this period is 0\.000301370"),
 ('Interest 11% Jan-Jun 2027', lambda: txt('tips/TIP_26ADM-06.pdf'), r"January 1, 2027, through June 30, 2027, is 11%"),
 ('Interest example $2,000 x 21 days = $12.66', lambda: txt('tips/TIP_26ADM-06.pdf'), r"\$12\.66"),
 ('Audit: 60-day notice, 30 days DR-1215, 60/120 day protest', lambda: txt('brochures/gt800022.pdf'), r"60 days from the date of the Notice of Proposed Assessment to file an informal protest or 120 days"),
 ('Certified audit: first $25,000 of interest abated', lambda: txt('brochures/gt800065.pdf'), r"abatement of the first \$25,000 of interest"),
 ('Voluntary disclosure 5% penalty if collected not remitted', lambda: page('https://floridarevenue.com/taxes/compliance/Pages/voluntary_disclosure.aspx'), r"a 5% penalty will be imposed"),
 ('Refund within three years', lambda: page('https://floridarevenue.com/taxes/compliance/Pages/refunds.aspx'), r"within three years of the date the tax was paid"),
 ('Concession divisor 7% = 1.0751; $6.99 tax', lambda: txt('brochures/gt800003.pdf'), r"\$100 ÷ 1\.0751 = \$93\.01"),
 ('Amusement certificate $30 per machine, expires June 30', lambda: txt('brochures/gt800020.pdf'), r"\$30 per machine at each location\. Certificates expire on June 30"),
 ('Bakery: five or fewer presumed on premises', lambda: txt('tips/TIP_10A01-22.pdf'), r"five \(5\) or less are assumed to be sold for consumption on the premises"),
 ('Boat + trailer example $3,375', lambda: txt('tips/TIP_24A01-11.pdf'), r"\$3,375"),
 ('New mobile homes 3% from July 1, 2022', lambda: txt('tips/TIP_22A01-12.pdf'), r"Beginning July 1, 2022, the state sales tax rate imposed on the retail sale of a new mobile home is reduced from 6% to 3%"),
 ('Asphalt indexed tax $1.19/ton', lambda: txt('tips/TIP_26A01-02.pdf'), r"\$1\.16 per ton to \$1\.19 per ton"),
 ('Tents $200 or less in 2026 HFC holiday', lambda: txt('tips/TIP_26A01-06.pdf'), r"\$200 or less: o Tents"),
 ('BTS 2026: no opt-out', lambda: txt('tips/TIP_26A01-11.pdf'), r"no option for dealers to opt-out"),
 ('Parking reported on Line A', lambda: txt('tips/TIP_25A01-11.pdf'), r"report these charges on Line A"),
 ('DR-14 personal reimbursed payment not accepted', lambda: txt('brochures/gt800054.pdf'), r"personal payment that will be reimbursed"),
 ('Transient rentals six months or less', lambda: page(SUT), r"timeshare resorts for a term of six months or less"),
 ('Home hardening refund max $500', lambda: txt('tips/TIP_26A01-09.pdf'), r"may not exceed \$500"),
]
ok = 0
for name, src, rx in checks:
    hit = re.search(rx, src())
    print(('PASS' if hit else 'FAIL'), name); ok += bool(hit)
print(f'{ok}/{len(checks)} facts confirmed in source text'); sys.exit(0 if ok == len(checks) else 1)
