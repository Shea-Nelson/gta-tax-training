// node --test tests/  — vectors come from Department examples where noted
const test = require('node:test'); const assert = require('node:assert');
const T = require('../docs/assets/js/taxcalc.js');
const tax = (p, s, cap = true) => T.fmt(T.computeTax({ priceCents: T.toCents(p), surtaxBp: T.toBp(s), capApplies: cap }).totalCents);
test('GT-300015 rounding example: $50.45 at 6% = $3.03', () => assert.equal(tax('50.45', '0'), '$3.03'));
test('GT-300015 surtax limit example: $7,000 item, 1% surtax = $470.00', () => assert.equal(tax('7000', '1'), '$470.00'));
test('no cap for services/admissions: $7,000 at 6% + 1% = $490.00', () => assert.equal(tax('7000', '1', false), '$490.00'));
test('TIP 24A01-11 boat + trailer: $55,000, 1.5% = $3,375.00', () => assert.equal(tax('55000', '1.5'), '$3,375.00'));
test('capstone sculpture: $8,000, 1.5% = $555.00', () => assert.equal(tax('8000', '1.5'), '$555.00'));
test('third decimal 5 rounds up: $0.25 -> $0.015 -> $0.02', () => assert.equal(tax('0.25', '0'), '$0.02'));
test('third decimal 4 rounds down: $0.24 -> $0.0144 -> $0.01', () => assert.equal(tax('0.24', '0'), '$0.01'));
test('exactly $5,000 at 1% = $350.00', () => assert.equal(tax('5000', '1'), '$350.00'));
test('input validation', () => { assert.equal(T.toCents('abc'), null); assert.equal(T.toCents('1.234'), null); assert.equal(T.toCents('$1,250.5'), 125050); assert.equal(T.toBp('1.5%'), 150); });
