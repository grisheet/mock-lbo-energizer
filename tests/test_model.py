"""Synthetic boundary fixtures are tests, never presented as market observations."""
import copy
import unittest
from datetime import date
from mock_lbo.sources import load_inputs, historical_checks
from mock_lbo.operating import run_model
from mock_lbo.debt import waterfall
from mock_lbo.returns import xirr, xnpv
from mock_lbo.taxes import cash_tax
from mock_lbo.validation import validate_model


class SourceTests(unittest.TestCase):
    def test_historical_reconciliations(self):
        self.assertLess(max(abs(v) for v in historical_checks().values()),0.15)

    def test_fiscal_quarter_totals(self):
        h,_=load_inputs()
        for seg in ('battery','auto'):
            self.assertAlmostEqual(sum(h[f'{seg}_fq{i}'] for i in range(1,5)),h[f'{seg}_sales'])

    def test_adjustment_bridge(self):
        h,a=load_inputs()
        r=run_model(h,a)
        self.assertAlmostEqual(r['normalization']['ebitda'],534.0)
        self.assertLess(r['normalization']['ebitda'],h['management_ebitda'])


class ReturnTests(unittest.TestCase):
    def test_simple_annual(self):
        self.assertAlmostEqual(xirr([-100,110],[date(2025,1,1),date(2026,1,1)]),.1)

    def test_actual_leap_days(self):
        ds=[date(2027,1,1),date(2029,1,1)]
        r=xirr([-100,144],ds)
        self.assertAlmostEqual(r,1.44**(365/731)-1)
        self.assertAlmostEqual(xnpv(r,[-100,144],ds),0)

    def test_total_loss_undefined(self):
        self.assertIsNone(xirr([-100,0],[date(2025,1,1),date(2026,1,1)]))

    def test_negative_return(self):
        self.assertAlmostEqual(xirr([-100,80],[date(2025,1,1),date(2026,1,1)]),-.2)

    def test_nonconventional_rejected(self):
        with self.assertRaises(ValueError):
            xirr([-100,120,-10],[date(2025,1,1),date(2026,1,1),date(2027,1,1)])

    def test_date_order_rejected(self):
        with self.assertRaises(ValueError):
            xirr([-100,120],[date(2026,1,1),date(2025,1,1)])


class DebtTests(unittest.TestCase):
    def compute(self,**kwargs):
        args=dict(cash=10,fcf=20,minimum=10,senior=100,junior=20,revolver=0,lease=5,
                  senior_original=100,capacity=30,amort_rate=.04,lease_annual=4,sweep=1)
        args.update(kwargs)
        return waterfall(**args)

    def test_cash_sweep(self):
        r=self.compute()
        self.assertEqual(r.cash,10)
        self.assertEqual(r.senior,81)

    def test_revolver_priority(self):
        r=self.compute(revolver=10)
        self.assertEqual(r.revolver_pay,10)
        self.assertEqual(r.senior_pay,8)

    def test_deficit_draw(self):
        r=self.compute(fcf=-10)
        self.assertEqual(r.draw,12)
        self.assertEqual(r.cash,10)

    def test_capacity_shortfall(self):
        r=self.compute(fcf=-50)
        self.assertEqual(r.draw,30)
        self.assertEqual(r.liquidity_gap,22)

    def test_no_overpayment(self):
        r=self.compute(fcf=1000)
        self.assertEqual(r.senior,0)
        self.assertGreater(r.cash,10)

    def test_zero_debt(self):
        r=self.compute(senior=0,junior=0,lease=0,senior_original=0)
        self.assertEqual(r.senior_pay,0)
        self.assertEqual(r.cash,30)

    def test_zero_sweep(self):
        r=self.compute(sweep=0)
        self.assertEqual(r.senior_pay,0)
        self.assertEqual(r.cash,28)


class TaxTests(unittest.TestCase):
    def compute(self,**kw):
        d=dict(ebitda=100,tax_depreciation=10,interest=50,interest_carry=0,nol=0,rate=.25,interest_limit=.30,nol_limit=.80)
        d.update(kw)
        return cash_tax(**d)

    def test_interest_cap(self):
        r=self.compute()
        self.assertEqual(r['deductible'],30)
        self.assertEqual(r['interest_carry'],20)
        self.assertEqual(r['cash_tax'],15)

    def test_nol_limit(self):
        r=self.compute(nol=100)
        self.assertEqual(r['nol_used'],48)
        self.assertEqual(r['cash_tax'],3)

    def test_loss_no_tax_refund(self):
        r=self.compute(ebitda=-10)
        self.assertEqual(r['cash_tax'],0)
        self.assertEqual(r['nol'],20)


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h,cls.a=load_inputs()

    def test_all_case_accounting(self):
        for c in ('base','downside','upside'):
            self.assertTrue(validate_model(run_model(self.h,self.a,c)))

    def test_downside_is_unfunded(self):
        r=run_model(self.h,self.a,'downside')['returns']
        self.assertFalse(r['feasible'])
        self.assertIsNone(r['xirr'])
        self.assertGreater(r['max_liquidity_gap'],0)

    def test_zero_exit_equity(self):
        a=copy.deepcopy(self.a)
        a['transaction']['exit_multiple']=1
        r=run_model(self.h,a)['returns']
        self.assertEqual(r['moic'],0)
        self.assertIsNone(r['xirr'])

    def test_entry_multiple_changes_funding(self):
        a=copy.deepcopy(self.a)
        a['transaction']['entry_multiple']+=1
        r=run_model(self.h,self.a)
        s=run_model(self.h,a)
        self.assertGreater(s['transaction']['sponsor'],r['transaction']['sponsor'])
        self.assertLess(s['returns']['xirr'],r['returns']['xirr'])

    def test_no_multiple_expansion_baseline(self):
        self.assertEqual(self.a['transaction']['entry_multiple'],self.a['transaction']['exit_multiple'])

    def test_determinism_and_no_input_mutation(self):
        before=copy.deepcopy(self.a)
        self.assertEqual(run_model(self.h,self.a),run_model(self.h,self.a))
        self.assertEqual(before,self.a)

    def test_simple_return_baseline(self):
        r=run_model(self.h,self.a)['returns']
        elapsed=(date(2030,12,31)-date(2025,12,31)).days/365
        self.assertAlmostEqual(r['xirr'],r['moic']**(1/elapsed)-1)


if __name__=='__main__':
    unittest.main()
