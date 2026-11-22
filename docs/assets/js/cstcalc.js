/* Florida communications services tax on one charge (unofficial teaching calculator).
   Rules used (cited on Module 3):
   - Florida CST = 4.92% state + 0.15% gross receipts (may be combined as 5.07%) + 2.37% gross receipts (s. 202.12,
     s. 203.01, s. 202.12001; DR-700016N). Direct-to-home satellite: 9.07% + 2.37% = 11.44%, no local tax.
   - Residential household service: exempt from the 4.92% and 0.15%; the 2.37% and the local tax still apply. The partial
     exemption never applies to mobile, video or direct-to-home satellite service (s. 202.125(1); Rule 12A-19.041).
   - Rounding (s. 202.16(3); TIP 11A19-01): carry to the third decimal place, round up to the next cent when the third
     decimal is greater than four. Local tax is rounded separately from the state and gross receipts taxes; this
     calculator uses the statute's third option (5.07% combined, 2.37% separately, local separately) and, for satellite,
     the first option (all 11.44% combined).
   Integer math only: money in cents, rates in thousandths of a percent (5.07% = 5070). */
(function (root) {
  const RATES = { state: 5070, grt: 2370, dths: 11440 };
  const KINDS = {
    business: { label: 'Voice, VoIP, private line or other non-residential service', state: true, local: true },
    residential: { label: 'Landline or VoIP sold to a residential household', state: false, local: true },
    mobile: { label: 'Mobile communications service', state: true, local: true },
    video: { label: 'Video service (cable or streaming)', state: true, local: true },
    dths: { label: 'Direct-to-home satellite service', dths: true, local: false }
  };
  function toCents(str) {
    const s = String(str).trim().replace(/[$,\s]/g, '');
    if (!/^\d+(\.\d{1,2})?$/.test(s)) return null;
    const [d, c = ''] = s.split('.');
    return Number(d) * 100 + Number((c + '00').slice(0, 2));
  }
  function toMilliPct(str) { // "5.22" or "5.220%" -> 5220
    const s = String(str).trim().replace('%', '');
    if (!/^\d+(\.\d{1,3})?$/.test(s)) return null;
    const [w, f = ''] = s.split('.');
    return Number(w) * 1000 + Number((f + '000').slice(0, 3));
  }
  // cents * milliPct is in units of 1e-7 dollars; mills = thousandths of a dollar, truncated after the third decimal
  function roundMills(mills) { return Math.floor(mills / 10) + (mills % 10 > 4 ? 1 : 0); }
  function part(cents, mpct) { const mills = Math.floor(cents * mpct / 10000); return { mills, cents: roundMills(mills) }; }
  function computeCst({ chargeCents, kind, localMpct = 0 }) {
    const k = KINDS[kind];
    if (!k) throw new Error('unknown kind ' + kind);
    const lines = [];
    if (k.dths) lines.push({ key: 'dths', label: 'Florida CST on satellite (9.07% + 2.37%)', rate: RATES.dths, ...part(chargeCents, RATES.dths) });
    else {
      if (k.state) lines.push({ key: 'state', label: 'State tax (4.92% + 0.15% gross receipts, billed as 5.07%)', rate: RATES.state, ...part(chargeCents, RATES.state) });
      lines.push({ key: 'grt', label: 'Gross receipts tax (2.37%)', rate: RATES.grt, ...part(chargeCents, RATES.grt) });
    }
    if (k.local && localMpct > 0) lines.push({ key: 'local', label: 'Local CST', rate: localMpct, ...part(chargeCents, localMpct) });
    const totalCents = lines.reduce((a, l) => a + l.cents, 0);
    return { lines, totalCents };
  }
  const fmt = c => '$' + Math.floor(c / 100).toLocaleString('en-US') + '.' + String(c % 100).padStart(2, '0');
  const fmtMills = m => '$' + Math.floor(m / 1000).toLocaleString('en-US') + '.' + String(m % 1000).padStart(3, '0');
  const pct = m => (m / 1000).toFixed(3).replace(/0+$/, '').replace(/\.$/, '') + '%';
  const api = { toCents, toMilliPct, roundMills, computeCst, fmt, fmtMills, pct, KINDS, RATES };
  if (typeof module !== 'undefined') { module.exports = api; return; }
  root.CstCalc = api;
  // Progressive enhancement: wire the form if this page has one.
  function wire() {
    const form = document.getElementById('cstcalc');
    if (!form) return;
    const out = document.getElementById('cstcalc-out');
    const errBox = document.getElementById('cstcalc-errors');
    const clear = el => { el.removeAttribute('aria-invalid'); };
    ['charge', 'local'].forEach(n => form[n].addEventListener('input', () => clear(form[n])));
    form.kind.addEventListener('change', () => { form.local.disabled = form.kind.value === 'dths'; });
    form.addEventListener('submit', e => {
      e.preventDefault();
      const charge = toCents(form.charge.value);
      const kind = form.kind.value;
      const local = kind === 'dths' ? 0 : toMilliPct(form.local.value || '0');
      const errs = [];
      if (charge === null) { errs.push(['charge', 'Enter the taxable charge in dollars and cents, for example 49.99.']); form.charge.setAttribute('aria-invalid', 'true'); }
      if (local === null || local > 15000) { errs.push(['local', 'Enter the total local CST rate as a percent between 0 and 15, for example 5.22.']); form.local.setAttribute('aria-invalid', 'true'); }
      if (errs.length) {
        errBox.hidden = false;
        errBox.innerHTML = '<p><strong>Please fix ' + errs.length + (errs.length > 1 ? ' fields' : ' field') + ':</strong></p><ul>' + errs.map(([id, m]) => '<li><a href="#cst-' + id + '">' + m + '</a></li>').join('') + '</ul>';
        out.textContent = '';
        errBox.focus();
        return;
      }
      errBox.hidden = true; errBox.textContent = '';
      const r = computeCst({ chargeCents: charge, kind, localMpct: local });
      out.innerHTML = '<p><strong>Total CST on this charge: ' + fmt(r.totalCents) + '</strong></p><ul>' +
        r.lines.map(l => '<li>' + l.label + ': ' + fmt(charge) + ' × ' + pct(l.rate) + ' = ' + fmtMills(l.mills) + ', rounded to <strong>' + fmt(l.cents) + '</strong></li>').join('') +
        '</ul><p class="small">Each part is carried to the third decimal place and rounded up only when the third decimal is greater than 4. ' +
        (kind === 'residential' ? 'The 5.07% state portion is not charged because of the residential partial exemption.' : kind === 'dths' ? 'Local CST never applies to direct-to-home satellite service.' : '') + '</p>';
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wire); else wire();
})(this);
