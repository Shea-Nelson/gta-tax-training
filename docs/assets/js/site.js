/* GTA Tax Training: progressive enhancement only. Pages work without script. */
(function () {
  // Self-check quizzes
  document.querySelectorAll('[data-quiz]').forEach(quiz => {
    const qs = [...quiz.querySelectorAll('[data-question]')];
    const answered = new Map();
    quiz.querySelectorAll('.answer-key').forEach(d => d.hidden = true);
    qs.forEach(fs => {
      const fb = fs.querySelector('[data-feedback]');
      const why = fs.querySelector('template[data-why]').innerHTML;
      fs.querySelector('[data-check]').addEventListener('click', () => {
        const picked = fs.querySelector('input:checked');
        fb.className = 'feedback';
        if (!picked) { fb.textContent = 'Choose an answer first.'; return; }
        const correctInput = fs.querySelector('input[data-correct]');
        const ok = picked.hasAttribute('data-correct');
        const correctText = correctInput.closest('label').textContent.trim();
        fb.classList.add(ok ? 'ok' : 'bad');
        fb.innerHTML = (ok ? '<span aria-hidden="true">✔ </span>Correct.' : '<span aria-hidden="true">✘ </span>Not quite. The answer is: ' + correctText.replace(/</g, '&lt;') + '.') + '<span class="why">' + why + '</span>';
        answered.set(fs.id, ok);
        if (answered.size === qs.length) {
          const n = [...answered.values()].filter(Boolean).length;
          quiz.querySelector('[data-score]').textContent = 'You answered ' + n + ' of ' + qs.length + ' correctly on your latest tries.';
        }
      });
    });
  });
  // Glossary / form filter
  document.querySelectorAll('[data-filter]').forEach(input => {
    const target = document.getElementById(input.getAttribute('data-filter'));
    const status = document.getElementById(input.getAttribute('aria-describedby'));
    const items = [...target.querySelectorAll('[data-item]')];
    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      let shown = 0;
      items.forEach(el => { const hit = !q || el.textContent.toLowerCase().includes(q); el.hidden = !hit; if (hit) shown++; });
      status.textContent = shown + ' of ' + items.length + ' shown';
    });
  });
  // Tax calculator (taxcalc.js is a later deferred script, so wait for DOMContentLoaded)
  document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('taxcalc');
  if (form && window.TaxCalc) {
    const out = document.getElementById('taxcalc-out');
    form.addEventListener('submit', e => {
      e.preventDefault();
      const price = TaxCalc.toCents(form.price.value);
      const sur = TaxCalc.toBp(form.surtax.value);
      const err = [];
      if (price === null) err.push('Enter the taxable price in dollars and cents, for example 1250.00.');
      if (sur === null || sur > 300) err.push('Enter the county surtax rate as a percent between 0 and 3, for example 1 or 1.5.');
      form.price.setAttribute('aria-invalid', price === null);
      form.surtax.setAttribute('aria-invalid', sur === null || sur > 300);
      if (err.length) { out.innerHTML = '<strong>Please fix:</strong> ' + err.join(' '); return; }
      const cap = form.kind.value === 'tpp';
      const r = TaxCalc.computeTax({ priceCents: price, surtaxBp: sur, capApplies: cap });
      const exact = (r.exactMillionths / 1e6).toFixed(6).replace(/0+$/, '').replace(/\.$/, '');
      out.innerHTML = '<p><strong>Total tax: ' + TaxCalc.fmt(r.totalCents) + '</strong></p><ul>' +
        '<li>State tax base: ' + TaxCalc.fmt(price) + ' × 6%</li>' +
        '<li>Surtax base: ' + TaxCalc.fmt(r.surtaxBaseCents) + ' × ' + form.surtax.value.replace('%', '') + '%' + (cap && price > 500000 ? ' (only the first $5,000 of this single item)' : '') + '</li>' +
        '<li>Unrounded tax: $' + exact + '. Carried to the third decimal place and rounded up only when the third decimal is greater than 4.</li></ul>';
    });
  }
  });
})();
