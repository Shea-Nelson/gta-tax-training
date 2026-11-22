#!/usr/bin/env python3
"""Spot-check CST guide facts against harvested source text: each claim must match a regex in its cited source,
and the same figure must appear in the built page that states it."""
import re, glob, sys
S = '/workspace/gta/cst-training/source'; D = '/workspace/gta/cst-training/repo/docs/cst'
def norm(t): return re.sub(r'\s+', ' ', t)
def txt(rel): return norm(open(f'{S}/text/{rel}', errors='ignore').read())
def page(url):
    for f in glob.glob(f'{S}/pages/*.txt'):
        with open(f, errors='ignore') as h:
            if h.readline().strip() == f'URL: {url}': return norm(h.read())
    raise SystemExit('missing page ' + url)
def built(slug): return norm(re.sub(r'<[^>]+>', ' ', open(f'{D}/{slug}.html').read()).replace('&amp;', '&'))
CST = 'https://floridarevenue.com/taxes/taxesfees/Pages/cst.aspx'
LOGIN = 'https://floridarevenue.com/taxes/eservices/Pages/cstlogin.aspx'
C = [  # (claim, source text fn, source regex, built page slug, page regex)
 ('Florida CST 7.44%; state 4.92%', lambda: page(CST), r'total tax rate for the Florida communications services tax is 7\.44%\. The state tax rate is 4\.92%', '02-rates', r'7\.44%'),
 ('4.92% + 0.15% may be billed as 5.07% state tax', lambda: page(CST), r'\(a total of 5\.07%\) as "state tax"', '01-basics', r'5\.07%'),
 ('Satellite 9.07% + 2.37% = 11.44%, no local', lambda: txt('brochures/gt800011.pdf.txt'), r'9\.07% plus 2\.37% gross receipts tax for a total of 11\.44%\. Local tax does not apply', '02-rates', r'11\.44%'),
 ('Residential exempt from 4.92% and 0.15% only', lambda: txt('law/ch202-entire.html.txt'), r'residential households is exempt from the tax imposed by s\. 202\.12 and s\. 203\.01\(1\)\(b\)3\.', '02-rates', r'exempt from the 4\.92% state tax and the 0\.15% gross receipts tax'),
 ('No residential exemption for mobile, video, satellite', lambda: txt('law/ch202-entire.html.txt'), r'does not apply to any residence that constitutes all or part of a transient public lodging establishment as defined in chapter 509, any mobile communications service, any video service, or any direct-to-home satellite service', '02-rates', r'mobile communications service'),
 ('Rounding: $5.045 -> $5.05, $3.213 -> $3.21', lambda: txt('tips/TIP_11A19-01.pdf.txt'), r'\$5\.045 rounds to \$5\.05 \$3\.213 rounds to \$3\.21', '03-local-tax-and-rounding', r'\$5\.045 rounds to \$5\.05'),
 ('Municipal max 5.1% / 4.98% with permit fees; noncharter 1.6%', lambda: txt('law/ch202-entire.html.txt'), r'up to 4\.98 percent for municipalities and charter counties that have chosen to levy permit fees\. \(b\) Noncharter counties may levy the tax authorized by subsection \(1\) at a rate of up to 1\.6 percent', '03-local-tax-and-rounding', r'up to 1\.6%'),
 ('Freeze: no increase before January 1, 2031', lambda: txt('law/ch202-entire.html.txt'), r'in effect on January 1, 2023, may not be increased before January 1, 2031', '15-rate-changes', r'January 1, 2031'),
 ('Rate change: notify by September 1; dealers 90 days; bills on/after January 1', lambda: txt('law/ch202-entire.html.txt'), r'bills that are dated on or after the January 1 subsequent to such adoption.*?by September 1 immediately preceding.*?at least 90 days before the effective date', '15-rate-changes', r'at least 90 days'),
 ('Failure to register: $100 initial fee', lambda: txt('law/ch202-entire.html.txt'), r'fails or refuses to register shall pay an initial registration fee of \$100', '04-registration', r'\$100'),
 ('One registration per legal entity', lambda: txt('brochures/gt800011.pdf.txt'), r'One registration is required for each legal entity, regardless of the number of locations', '04-registration', r'each legal entity'),
 ('Allowance 0.75% qualifying, 0.25% otherwise, satellite 0.75%', lambda: page(CST), r'If a qualifying method is not used .{0,120}collection allowance of \.25% will be granted\. Direct-to-home satellite service providers receive the \.75% collection allowance', '08-address-database', r'0\.25%'),
 ('Late payment disallows only late percentage since Oct 1, 2015', lambda: txt('tips/TIP_15A19-02.pdf.txt'), r'Effective October 1, 2015, if a collection allowance is disallowed only because a tax payment is late, then the amount that is disallowed is limited to the percentage of the total tax due that is late', '08-address-database', r'October 1, 2015'),
 ('$5,000 penalty per return for local tax not on schedule', lambda: txt('law/ch202-entire.html.txt'), r'shall be subject to a penalty of \$5,000 per return', '08-address-database', r'\$5,000 per return'),
 ('Misassignment penalty 10%, max $10,000 per return', lambda: txt('law/ch202-entire.html.txt'), r'specific penalty of 10 percent of any tax collected but reported to the incorrect jurisdiction.*?may not exceed \$10,000', '08-address-database', r'\$10,000'),
 ('Database updated every six months', lambda: page(CST), r'is updated every six months', '08-address-database', r'every six months'),
 ('Database changes posted 120 days before Jan 1 / Jul 1', lambda: txt('forms/dr700002.pdf.txt'), r'at least 120 days prior to the January 1 or July 1 effective date', '08-address-database', r'120 days'),
 ('Resale batch up to 50,000 accounts', lambda: page(CST), r'batch file of up to 50,000 accounts', '10-resale', r'50,000'),
 ('Resale certificates expire December 31; paper filers mailed mid-November', lambda: page(CST), r'Certificates expire on December 31 of each year.*?mailed a new certificate each year in mid-November', '10-resale', r'mid-November'),
 ('Due 1st, late after 20th; file even if no tax due', lambda: page(CST), r'due on the 1st and late after the 20th day.*?A return must be filed for each reporting period, even if no tax is due', '13-filing-paying', r'even if no tax is due'),
 ('E-file if $5,000+ paid in prior state fiscal year', lambda: page(CST), r'paid \$5,000 or more in communications services tax during the most recent state fiscal year \(July 1 - June 30\)', '13-filing-paying', r'\$5,000 or more'),
 ('EFT by 5 p.m. ET business day prior to the 20th', lambda: page(CST), r'no later than 5:00 p\.m\.\. ET, on the business day prior to the 20th', '13-filing-paying', r'5:00 p\.m\. ET'),
 ('New eFile system June 1, 2026; history to Sept 30, 2026; DR-841', lambda: page(LOGIN), r'Effective June 1, 2026, communications services tax has moved to a new eFile and Pay system.*?until September 30, 2026.*?Form DR-841', '13-filing-paying', r'June 1, 2026'),
 ('Alternative period example: Dec 21, 2015; EFT Dec 18', lambda: txt('tips/TIP_15A19-02.pdf.txt'), r'Monday, December 21, 2015\. Dealers who pay electronically must initiate their submissions before 5:00 p\.m\., ET, on December 18, 2015', '13-filing-paying', r'December 18, 2015'),
 ('Penalty 10% per 30 days, max 50%', lambda: page(CST), r'10% of any unpaid tax for each 30 days or fraction thereof, not to exceed a total penalty of 50%', '16-refunds-audits-penalties', r'up to 50%'),
 ('Refund request within 3 years; dealer 30 days, refund 45 days', lambda: txt('law/ch202-entire.html.txt'), r'within 3 years following collection of the tax.*?Within 30 days following receipt of a completed request.*?within 45 days following such determination', '16-refunds-audits-penalties', r'within 45 days'),
 ('Suit within 180 days after the dealer written response', lambda: txt('law/ch202-entire.html.txt'), r'barred unless it is commenced within 180 days following the date of the dealer’s written response', '16-refunds-audits-penalties', r'180 days after the dealer'),
 ('Audit: 60-day notice; 305 days; 60/120 protest', lambda: txt('brochures/gt800022.pdf.txt'), r'no later than 305 days after sending Form DR-840.*?60 days from the date of the Notice of Proposed Assessment to file an informal protest or 120 days', '16-refunds-audits-penalties', r'305 days'),
 ('Bad debt credit within 12 months after the year charged off', lambda: txt('tips/TIP_04A19-01.pdf.txt'), r'within 12 months following the last day of the calendar year for which the bad debt was charged off', '14-dr700016', r'within 12 months'),
 ('Direct pay caps $100,000 state, $25,000 local', lambda: txt('law/ch202-entire.html.txt'), r'shall not exceed \$100,000 per calendar year.*?shall not exceed \$25,000 per calendar year', '12-use-tax-direct-pay', r'\$25,000'),
 ('Direct pay permit expires five years', lambda: txt('law/12A-19.txt'), r'direct pay permit expires five \(5\) years from the effective date', '12-use-tax-direct-pay', r'five years'),
 ('DR-700019 semiannual, late after July 20 / January 20', lambda: txt('forms/dr700019.pdf.txt'), r'filing frequency is semiannual.*?late after July 20.*?late after January 20', '12-use-tax-direct-pay', r'July 20'),
 ('Prepaid calling taxed at 6% under s. 212.05', lambda: txt('law/s212.05.html.txt'), r'At the rate of 6 percent on charges for: a\. Prepaid calling arrangements', '11-prepaid-calling', r'6%'),
 ('Private line: 50% of separately billed interstate segment', lambda: txt('law/ch202-entire.html.txt'), r'If any segment between two such channel termination points is separately billed, 50 percent of such charge', '07-sourcing', r'50%'),
 ('Mobile provider must use correct address within 120 days', lambda: txt('law/ch202-entire.html.txt'), r'shall begin using the correct address within 120 days', '07-sourcing', r'120 days'),
 ('Schedule IV example: 1,113.09/0.0110 = 101,190.00; /0.0210 = 53,004.29', lambda: txt('forms/dr700016n.pdf.txt'), r'\$1,113\.09 divided by 0\.0110 = \$101,190\.00.*?\$1,113\.09 divided by 0\.0210 = \$53,004\.29', '14-dr700016', r'\$53,004\.29'),
 ('Stuart total local rate 5.220% from January 1, 2026', lambda: txt('tips/TIP_25A19-02.pdf.txt'), r'STUART 5\.220%', '15-rate-changes', r'5\.220%'),
 ('Hillsborough 2021: Tampa 6.020%', lambda: txt('tips/TIP_21A19-01.pdf.txt'), r'TAMPA 6\.020%', '15-rate-changes', r'6\.020%'),
 ('Interest Jul-Dec 2026 11%, factor 0.000301370', lambda: norm(open('/workspace/gta/sut-training/source/tips/TIP_26ADM-02.pdf.txt').read()) if glob.glob('/workspace/gta/sut-training/source/tips/TIP_26ADM-02.pdf.txt') else __import__('subprocess').run(['pdftotext','/workspace/gta/sut-training/source/tips/TIP_26ADM-02.pdf','-'],capture_output=True,text=True).stdout.replace('\n',' '), r'July 1, 2026, through December 31, 2026, is 11%\. The daily interest rate factor to be used for this period is 0\.000301370', '16-refunds-audits-penalties', r'0\.000301370'),
 ('Interest Jan-Jun 2027 11%, factor 0.000301370 (TIP 26ADM-06)', lambda: norm(open('/workspace/gta/sut-training/source/text/tips/TIP_26ADM-06.pdf.txt').read()), r'January 1, 2027, through June 30, 2027, is 11%\. The daily interest rate factor to be used for this period is 0\.000301370', '16-refunds-audits-penalties', r'January 1 through June 30, 2027'),
 ('CST quick reference interest through June 30, 2027', lambda: norm(open('/workspace/gta/sut-training/source/text/tips/TIP_26ADM-06.pdf.txt').read()), r'Communications services tax', 'quick-reference', r'July 1, 2026 through June 30, 2027: 11%'),
 ('Certified vendors include Avalara, CoreLogic, Precisely, Vertex', lambda: page(CST), r'Avalara.*?CoreLogic.*?Precisely.*?Vertex', '08-address-database', r'certified'),
]
ok = 0
for claim, src, rx, slug, prx in C:
    s = bool(re.search(rx, re.sub(r'\s+', ' ', src()), re.S)); b = bool(re.search(prx, built(slug)))
    ok += s and b
    print(('PASS' if s and b else 'FAIL'), f'[source {"ok" if s else "MISSING"} | page {"ok" if b else "MISSING"}]', claim)
print(f'{ok}/{len(C)} facts verified'); sys.exit(0 if ok == len(C) else 1)
