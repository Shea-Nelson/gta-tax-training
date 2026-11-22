// node --test tests/cstcalc.test.js — rules from s. 202.16(3), TIP 11A19-01, DR-700016N and the CST page
const test = require('node:test'); const assert = require('node:assert');
const C = require('../docs/assets/js/cstcalc.js');
const run = (amt, kind, local = '0') => C.computeCst({ chargeCents: C.toCents(amt), kind, localMpct: C.toMilliPct(local) });
const tot = (...a) => C.fmt(run(...a).totalCents);
const lines = (...a) => Object.fromEntries(run(...a).lines.map(l => [l.key, C.fmt(l.cents)]));
test('TIP 11A19-01: $5.045 rounds to $5.05', () => assert.equal(C.roundMills(5045), 505));
test('TIP 11A19-01: $3.213 rounds to $3.21', () => assert.equal(C.roundMills(3213), 321));
test('third decimal 4 does not round up: $2.534 -> $2.53', () => assert.equal(C.roundMills(2534), 253));
test('$100 business line, no local: 5.07 + 2.37 = $7.44 (the 7.44% Florida CST)', () => assert.equal(tot('100', 'business'), '$7.44'));
test('$100 satellite: 11.44% = $11.44 and local ignored', () => { assert.equal(tot('100', 'dths', '5.22'), '$11.44'); assert.deepEqual(Object.keys(lines('100', 'dths', '5.22')), ['dths']); });
test('$100 residential line: no 5.07%, only 2.37% + local 5.22% = $7.59', () => assert.deepEqual(lines('100', 'residential', '5.22'), { grt: '$2.37', local: '$5.22' }));
test('mobile gets no residential exemption: $100 at local 5.22% = $12.66', () => assert.equal(tot('100', 'mobile', '5.22'), '$12.66'));
test('Module 3 worked example: $49.99 business line, local 5.22% -> $2.53 + $1.18 + $2.61 = $6.32', () => {
  assert.deepEqual(lines('49.99', 'business', '5.22'), { state: '$2.53', grt: '$1.18', local: '$2.61' }); assert.equal(tot('49.99', 'business', '5.22'), '$6.32'); });
test('local rate with three decimals (Tallahassee 6.90% in the Jan 2026 workbook): $80 video -> $4.06 + $1.90 + $5.52', () =>
  assert.deepEqual(lines('80', 'video', '6.9'), { state: '$4.06', grt: '$1.90', local: '$5.52' }));
test('input parsing rejects bad values', () => { assert.equal(C.toCents('12.345'), null); assert.equal(C.toMilliPct('5.2222'), null); assert.equal(C.toCents('$1,250.00'), 125000); });
