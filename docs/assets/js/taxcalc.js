/* Florida sales tax + discretionary sales surtax on ONE taxable item (unofficial teaching calculator).
   Rules used (cited on the rates page):
   - total tax = sale x state rate + (surtax base) x surtax rate, where the surtax base is the first $5,000
     of a single item of tangible personal property; the $5,000 cap does not apply to services, admissions,
     transient rentals or prepaid calling arrangements (Discretionary Sales Surtax page; DR-15DSS).
   - the computation is carried to the third decimal place and rounded up to the next whole cent when the
     third decimal place is greater than 4 (DR-15N; TIP 21A01-02).
   Integer math only: money in cents, rates in basis points (6% = 600). */
(function (root) {
  function toCents(str) {
    const s = String(str).trim().replace(/[$,\s]/g, '');
    if (!/^\d+(\.\d{1,2})?$/.test(s)) return null;
    const [d, c = ''] = s.split('.');
    return Number(d) * 100 + Number((c + '00').slice(0, 2));
  }
  function toBp(str) {
    const s = String(str).trim().replace('%', '');
    if (!/^\d+(\.\d{1,2})?$/.test(s)) return null;
    const [w, f = ''] = s.split('.');
    return Number(w) * 100 + Number((f + '00').slice(0, 2));
  }
  // mills = thousandths of a dollar, truncated past the third decimal; round up when 3rd decimal > 4
  function roundMills(numerator) { // numerator = cents * bp (units of 1e-6 dollars)
    const mills = Math.floor(numerator / 1000);
    return Math.floor(mills / 10) + (mills % 10 > 4 ? 1 : 0);
  }
  function computeTax({ priceCents, surtaxBp, capApplies, stateBp = 600 }) {
    const surtaxBase = capApplies ? Math.min(priceCents, 500000) : priceCents;
    const numerator = priceCents * stateBp + surtaxBase * surtaxBp;
    const totalCents = roundMills(numerator);
    return { surtaxBaseCents: surtaxBase, totalCents, exactMillionths: numerator };
  }
  const fmt = c => '$' + (Math.floor(c / 100)).toLocaleString('en-US') + '.' + String(c % 100).padStart(2, '0');
  const api = { toCents, toBp, computeTax, fmt, roundMills };
  if (typeof module !== 'undefined') module.exports = api; else root.TaxCalc = api;
})(this);
