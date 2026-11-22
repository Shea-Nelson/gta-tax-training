import json
Q={}
def q(slug,*items): Q[slug]=[{'q':a,'options':b,'answer':c,'why':d} for a,b,c,d in items]
q('01-basics',
 ("Which of these is a communications service under Florida CST?",["Web hosting","A streaming video subscription","Selling a phone","A late payment fee"],1,"Video, including streaming, is a taxable communications service. Web hosting is an information service, and phones and late fees are excluded."),
 ("What are the three components of CST?",["State, county and city sales tax","State CST, gross receipts tax and local CST","Federal excise, state and local tax","Sales tax, surtax and use tax"],1,"CST has a state portion (s. 202.12), a gross receipts portion (s. 203.01) and a local portion (s. 202.19)."),
 ("How must the tax appear on the customer's bill?",["As one combined “taxes and fees” line","Separately, as Florida CST and local CST","It may be included in the price if the bill says so","Only on request"],1,"Dealers must separately state the Florida and local communications services taxes and may not absorb them."),
 ("A purchaser pays the tax to the dealer. Who is then liable if the dealer never remits it?",["The purchaser","The dealer, because paying the dealer relieves the purchaser","The local government","No one"],1,"The purchaser is liable until the tax is paid; payment to the dealer relieves the purchaser.") )
q('02-rates',
 ("What is the total Florida CST rate on most services, before local tax?",["5.07%","6%","7.44%","9.17%"],2,"4.92% + 0.15% + 2.37% = 7.44%."),
 ("What is the rate on direct-to-home satellite service?",["7.44% plus local","11.44% with no local tax","9.07% plus local","2.37% only"],1,"Satellite is taxed at 9.07% + 2.37% = 11.44%, and local tax does not apply."),
 ("A family's home landline is billed $40. Which parts of CST apply?",["All of them","Only the 2.37% gross receipts tax and the local tax","Only the local tax","None; residential service is exempt"],1,"The residential exemption removes only the 4.92% state tax and the 0.15% gross receipts tax."),
 ("Which service can get the residential partial exemption?",["A family's mobile plan","Cable TV at home","A home VoIP line","Satellite TV at home"],2,"Mobile, video and satellite service never get the exemption. A home VoIP line can.") )
q('03-local-tax-and-rounding',
 ("A jurisdiction's total local rate is made of:",["The state rate plus the county rate","Its adopted rate plus the county surtax conversion rate","The county surtax only","The 2.37% plus the adopted rate"],1,"The Department publishes the adopted rate plus the county surtax conversion rate as one total."),
 ("Tax computes to $2.534. What is charged?",["$2.53","$2.54","$2.50","$2.60"],0,"Carry to three decimals; round up only if the third decimal is 5 or more. 4 is less than 5."),
 ("Which must always be rounded separately?",["The 4.92% and the 0.15%","The local tax, apart from the Florida CST","Each customer's bills for the year","Nothing; rounding is optional"],1,"Local tax is always rounded separately; the Florida CST has three permitted rounding options."),
 ("Until when may a local CST rate in effect on January 1, 2023 not be increased?",["December 31, 2025","January 1, 2027","January 1, 2031","It can be increased any time"],2,"Section 202.19(2)(d) bars increases before January 1, 2031.") )
q('04-registration',
 ("A company with four store locations sells VoIP service. How many CST registrations does it need?",["Four","One per county","One, for the legal entity","None"],2,"One registration is required for each legal entity, regardless of the number of locations."),
 ("Which business does not need to register for CST?",["A cable TV provider","A web hosting company that sells only hosting","A satellite TV provider","A VoIP provider"],1,"Information services such as web hosting are not communications services."),
 ("What does a new dealer receive with its Certificate of Registration?",["A sales tax resale certificate","A CST Annual Resale Certificate (DR-700015)","A direct pay permit","Nothing else"],1,"New dealers receive DR-700014 and DR-700015."),
 ("A dealer changes from a sole proprietorship to a corporation. What is required?",["Update the name online","Nothing","A new registration","A letter to the Department"],2,"A change of legal entity or ownership requires a new registration.") )
q('05-taxable-services',
 ("Which is excluded from the definition of communications services?",["VoIP","Mobile service","Internet access","Pager service"],2,"Internet access, email and similar online services are excluded."),
 ("A hotel charges a guest for a pay-per-view movie. Is it subject to CST?",["Yes","No, it is entertainment","Only the local tax","Only if over $10"],0,"The Department's FAQ says hotel pay-per-view movies are subject to CST."),
 ("A law firm faxes documents for a client as part of its legal services. Is CST due on the fax?",["Yes, fax is always taxable","No, fax in the course of professional services is not taxable","Only local tax","Only the 2.37%"],1,"Fax is taxable except when provided in the course of professional or advertising services."),
 ("A condominium association includes cable in its monthly fee without stating a separate charge. Does it collect CST from owners?",["Yes","No","Only from renters","Only local tax"],1,"Per the Department's FAQ, it does not collect CST when the cable charge is not separately stated.") )
q('06-sales-price-bundling',
 ("Which charge is taxable even if separately stated on the bill?",["A separately stated 911 fee","Voice mail","Internet access","A late fee"],1,"Voice mail is one of the charges always included in the sales price."),
 ("A dealer lists its universal service fund fee as a separate line. May it exclude that amount from the sales price?",["Yes","No","Only for residential customers","Only for mobile service"],1,"Dealer expenses such as USF fees do not reduce the sales price."),
 ("A bundle of TV and Internet access is sold for one price with no breakdown. When can the Internet portion be left out of the tax?",["Never","Always","When the dealer can reasonably identify it from books and records kept in the regular course of business","When the customer asks"],2,"That is the books-and-records rule in s. 202.11(13)(b)8."),
 ("Which is not part of the CST sales price?",["Connection charges","Detailed billing","The sale or recharge of a prepaid calling arrangement","Directory assistance"],2,"Prepaid calling arrangement sales are excluded from the CST sales price.") )
q('07-sourcing',
 ("What is the service address for mobile service?",["Where the phone is used most this month","The customer's place of primary use","The billing address, wherever it is","The cell tower location"],1,"Mobile service is sourced to the place of primary use: the residential or primary business street address in the licensed service area."),
 ("Satellite TV is received at a Florida home but billed to an Ohio address. Where is it sourced?",["Ohio","The Florida location where it is received","Tallahassee","The provider's headquarters"],1,"Video and satellite service are sourced to where they are received in Florida."),
 ("A calling-card call's service address is:",["The caller's home","The central office for the area code and first three digits of the originating number","The card issuer's address","The called number"],1,"That is the rule in s. 202.11(14)(a)2."),
 ("A private line circuit has 3 termination points in Florida and 1 out of state, $1,000 a month, not billed by segment. What is the Florida taxable amount?",["$500","$750","$1,000","$250"],1,"$1,000 × 3/4 = $750.") )
q('08-address-database',
 ("How often is the Department's Address/Jurisdiction Database updated?",["Monthly","Every six months","Once a year","Only on request"],1,"It is updated every six months, with changes effective January 1 and July 1."),
 ("Which method does NOT earn the 0.75% collection allowance?",["The Department's database","A certified vendor database","ZIP+4 with a reasonable methodology","An uncertified in-house list"],3,"Methods other than the Department's database, a certified database or ZIP+4 earn 0.25%."),
 ("A dealer files on time but pays 20% of the tax late. What happens to the allowance?",["It is lost entirely","Only 20% of it is disallowed","Nothing","It doubles"],1,"Since October 1, 2015, a late payment disallows only the late percentage. A late return loses it entirely."),
 ("What is the penalty for failing to report local tax on Schedule I?",["$100","$5,000 per return","10% of tax","None"],1,"Section 202.28 imposes $5,000 per return.") )
q('09-exemptions',
 ("A county pays its phone bill directly and has given the dealer a customer application identifying it as a county. Is CST due?",["Yes","No, it is exempt","Only the 2.37%","Only local tax"],1,"Sales to the state and its political subdivisions are exempt when paid directly and documented."),
 ("What may a dealer keep to document a government P-Card purchase?",["Nothing","A copy of the card's face, or the tax-exempt number, account number and cardholder name","The government's DR-14 only","A signed letter from the employee"],1,"Rule 12A-19.042 allows either."),
 ("What does a 501(c)(3) religious institution give the dealer?",["Its IRS determination letter","A signed certificate stating the purchases are for a qualifying religious institution","Nothing","A sales tax DR-14 only"],1,"The rule requires a signed certificate; the IRS letter is not required."),
 ("If the dealer documented an exemption properly and the Department later finds tax due, who pays?",["The dealer","The customer","Nobody","The local government"],1,"The Department looks to the customer when the dealer met the documentation requirements.") )
q('10-resale',
 ("When does the CST Annual Resale Certificate expire?",["June 30","December 31","After five years","Never"],1,"It expires every December 31."),
 ("A Transaction Resale Authorization Number is valid for:",["The calendar year","That one transaction","Five years","All of the buyer's purchases"],1,"It covers the single transaction."),
 ("May a buyer use its sales and use tax resale certificate to buy communications services tax-free for resale?",["Yes","No, the CST certificate is separate","Only for mobile service","Only once"],1,"The CST Annual Resale Certificate is separate from the sales tax certificate."),
 ("A dealer sells for resale without proper documentation. Who owes the tax?",["The buyer only","The selling dealer","No one","The Department waives it"],1,"A sale for resale is excluded only in strict compliance; otherwise the seller is liable.") )
q('11-prepaid-calling',
 ("How is the sale of a prepaid phone card taxed in Florida?",["CST at 7.44% plus local","Sales tax at 6% plus any surtax","Not taxed","Gross receipts tax only"],1,"Prepaid calling arrangements are excluded from CST and taxed under s. 212.05."),
 ("A prepaid refill is bought online and nothing is shipped. Where is the sale sourced?",["The seller's headquarters","The customer's address or the location associated with the mobile number","Tallahassee","Nowhere"],1,"That is the rule in s. 212.05(1)(e)."),
 ("Is more tax due when the buyer uses the prepaid units to make calls?",["Yes, CST","Yes, sales tax again","No","Only local CST"],2,"No additional sales tax or CST is due on use of the units."),
 ("What is the status of TIP 12ADM-02 on prepaid communications services?",["Current","Retracted","Replaced by a rule","Expired in 2030"],1,"It was retracted on July 29, 2013.") )
q('12-use-tax-direct-pay',
 ("A consumer buys taxable service from a seller that does not collect Florida CST. What should the consumer file?",["DR-700016","DR-700019","DR-15","Nothing"],1,"Consumers report use tax on DR-700019; registered dealers use DR-700016."),
 ("When is a DR-700019 for the period ending June 30 late?",["After June 30","After July 20","After August 1","After December 31"],1,"It is due July 1 and late after July 20."),
 ("Which situation can qualify for a CST direct pay permit?",["Any large business","Most services bought originate outside Florida and terminate in Florida","Any government","Any reseller"],1,"The other basis is when taxability is known only on use."),
 ("How long does a direct pay permit last?",["One year","Five years","Until revoked","Ten years"],1,"Rule 12A-19.030 sets a five-year term with renewal on DR-700032.") )
q('13-filing-paying',
 ("When is a CST return late?",["After the 1st","After the 20th of the month after the period","After the 30th","After the quarter ends"],1,"Due on the 1st and late after the 20th, with weekend and holiday rollover."),
 ("Who must file and pay electronically?",["Everyone","Dealers that paid $5,000 or more in the prior state fiscal year","Only mobile providers","Only dealers with over 100 customers"],1,"The threshold is $5,000 paid during the prior July-to-June fiscal year."),
 ("By when must an electronic payment be initiated?",["Midnight on the 20th","5:00 p.m. ET on the business day before the 20th","Noon on the 20th","The 1st"],1,"A confirmation number must be received by 5:00 p.m. ET on the business day before the 20th."),
 ("A dealer had no taxable sales this month. Must it file?",["No","Yes, a return is required for each period","Only if requested","Only quarterly"],1,"A return must be filed for each reporting period, even if no tax is due.") )
q('14-dr700016',
 ("Where do residential landline sales go on Schedule I?",["Column B only","Column C only","Both B and C","Neither"],1,"Residential sales are exempt from the 5.07%, so they go in Column C (2.37% and local) but not Column B."),
 ("Page 1, Line 1 comes from:",["Schedule II, Column C","Summary of Schedule I, Column F, Line 3","Schedule IV, Column U","Line 5"],1,"Line 1 is the tax at 4.92% + 0.15% from the Schedule I summary."),
 ("Where is direct-to-home satellite tax reported?",["Schedule I","Schedule II","Schedule V","Line 3"],1,"Schedule II, with the total in Column C going to Line 4."),
 ("Can Line 12 be negative?",["Yes","No","Only with Schedule V credits","Only for satellite"],1,"The instructions say Line 12 cannot be a negative number.") )
q('15-rate-changes',
 ("A city adopts a new local CST rate in June. When is it effective (outside the freeze)?",["Immediately","July 1","Bills dated on or after the next January 1","After 90 days"],2,"Changes apply to bills dated on or after the January 1 after adoption."),
 ("By when must the city notify the Department?",["September 1","October 1","December 31","June 30"],0,"Notice is due by September 1 before the January 1 effective date."),
 ("How much notice must the Department give dealers?",["30 days","60 days","At least 90 days","One year"],2,"Section 202.21 requires at least 90 days."),
 ("Service was provided in December 2025 but billed on January 5, 2026. Which rate applies under the January 2026 TIP?",["The 2025 rate","The new rate, because the bill was issued on or after January 1, 2026","An average","The lower one"],1,"The rates apply to all bills issued on or after January 1, 2026, regardless of when service was rendered.") )
q('16-refunds-audits-penalties',
 ("How long does a customer have to request a refund of CST from the dealer?",["1 year","3 years after collection","5 years","90 days"],1,"The written request must be submitted within 3 years after the tax was collected."),
 ("A return is filed and paid 45 days late. What is the late penalty rate?",["10%","20%","30%","50%"],1,"10% for each 30 days or fraction: 45 days is two periods, so 20%."),
 ("What starts the 60-day pre-audit period?",["A phone call","A Notice of Intent to Audit Books and Records (DR-840)","The entrance interview","A DR-1215"],1,"The DR-840 starts the 60-day period, which the taxpayer may waive."),
 ("What is the usual audit lookback period?",["One year","Three years","Seven years","Unlimited"],1,"Typically three years, longer for non-filers or substantially incorrect returns.") )
q('17-capstone',
 ("In the capstone, why does the Orlando mobile plan revenue go in Column B?",["Mobile service is exempt","Mobile service never gets the residential exemption","It is sold for resale","It is prepaid"],1,"Mobile service is fully taxable, including the 5.07%."),
 ("Why are the prepaid refill cards left off the CST return?",["They are exempt from all tax","They are taxed under the sales tax law instead","They are below a threshold","They are resold"],1,"The sale of prepaid calling arrangements is taxed under s. 212.05, not CST."),
 ("Mangrove's Line 5 is $8,716.80. What is its collection allowance if on time?",["$21.79","$65.38","$87.17","$0"],1,"0.0075 × $8,716.80 = $65.376, rounded to $65.38."),
 ("Mangrove reported $552.00 of local tax to Orlando (5.52%) that belonged elsewhere. What is the decrease in Orlando's taxable sales on Schedule IV?",["$552.00","$10,000.00","$10,454.55","$5,520.00"],1,"$552.00 ÷ 0.0552 = $10,000.00, shown in parentheses.") )
json.dump(Q,open('quizzes.json','w'),indent=1,ensure_ascii=False)
print(len(Q), sum(len(v) for v in Q.values()))
