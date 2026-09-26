"""Independent quarterly reference model; Excel owns its own linked formulas."""
from calendar import monthrange
from datetime import date
from typing import Any
from .debt import waterfall
from .taxes import cash_tax
from .transaction import acquisition, closing_bridge, normalize
from .returns import xirr


def run_model(h: dict[str, float], assumptions: dict, case: str = 'base') -> dict:
    t, c = assumptions['transaction'], assumptions[case]
    n = normalize(h,t)
    b = closing_bridge(h,t,n)
    a = acquisition(h,t,n,b)
    if min(a['sponsor'],a['seller'],n['ebitda']) <= 0:
        raise ValueError('Nonpositive sponsor contribution, seller proceeds, or entry EBITDA')
    quarterly: list[dict[str, Any]] = []
    senior,junior,rev,lease,cash=a['senior'],a['junior'],0.0,b['lease'],a['minimum_cash']
    sf,jf,rf=a['senior']*t['debt_fee_rate'],a['junior']*t['debt_fee_rate'],a['revolver_fees']
    old_ppe,new_ppe,step_ppe=b['ppe'],0.0,t['ppe_stepup']
    old_int,step_int=b['intangibles'],t['intangible_stepup']
    ar,inv,ap=h['ar'],h['inventory'],h['ap']
    ic,nol,retained=0.0,0.0,0.0
    annual_battery,annual_auto=h['battery_sales'],h['auto_sales']
    bm,am=n['battery_margin'],n['auto_margin']
    fixed=h['adjusted_sga']
    previous_date=date(2025,12,31)
    cumulative_ppa_release=0.0
    for year in range(5):
        annual_battery *= (1+c['battery_volume'][year])*(1+c['price'][year])*(1+c['fx'][year])
        annual_auto *= (1+c['auto_volume'][year])*(1+c['price'][year])*(1+c['fx'][year])
        bm += c['margin_change'][year]
        am += c['margin_change'][year]
        fixed *= 1+c['sga_inflation'][year]
        annual_cogs=annual_battery*(1-bm)+annual_auto*(1-am)
        for q in range(1,5):
            d=date(2026+year,3*q,monthrange(2026+year,3*q)[1])
            days=(d-previous_date).days
            fiscal_q=q+1 if q<4 else 1
            bsales=annual_battery*h[f'battery_fq{fiscal_q}']/h['battery_sales']
            asales=annual_auto*h[f'auto_fq{fiscal_q}']/h['auto_sales']
            sales=bsales+asales
            cogs=bsales*(1-bm)+asales*(1-am)
            gross=sales-cogs
            variable=sales*n['variable_opex']
            recurring=c['recurring_cost'][year]/4
            ebitda=gross-variable-fixed/4-recurring
            capex=sales*c['capex_rate'][year]
            depreciation=min(old_ppe,b['ppe']/t['old_ppe_life_years']/4)
            new_dep=min(new_ppe,new_ppe/t['new_ppe_life_years']/4)
            step_dep=min(step_ppe,t['ppe_stepup']/t['ppa_life_years']/4)
            amort=min(old_int,t['old_intangible_amort_annual']/4)
            step_amort=min(step_int,t['intangible_stepup']/t['ppa_life_years']/4)
            da=depreciation+new_dep+step_dep+amort+step_amort
            old_ppe-=depreciation
            new_ppe+=capex-new_dep
            step_ppe-=step_dep
            old_int-=amort
            step_int-=step_amort
            new_ar=sales/days*c['dso'][year]
            new_inv=annual_cogs/365*c['dio'][year]
            new_ap=annual_cogs/365*c['dpo'][year]
            delta_wc=new_ar+new_inv-new_ap-(ar+inv-ap)
            ar,inv,ap=new_ar,new_inv,new_ap
            rate=max(c['reference_rate'][year],t['rate_floor'])
            senior_interest=senior*(rate+t['senior_spread'])*days/360
            junior_interest=junior*t['junior_rate']*days/360
            rev_interest=rev*(rate+t['revolver_spread'])*days/360
            lease_interest=lease*t['lease_rate']*days/360
            commit=(a['capacity']-rev)*t['commitment_fee_rate']*days/360
            cash_interest=senior_interest+junior_interest+rev_interest+lease_interest+commit
            tax=cash_tax(ebitda=ebitda,tax_depreciation=depreciation+new_dep+amort,interest=cash_interest,interest_carry=ic,nol=nol,rate=t['tax_rate'],interest_limit=t['interest_limit_ebitda'],nol_limit=t['nol_limit'])
            ic,nol=tax['interest_carry'],tax['nol']
            fcf=ebitda-cash_interest-tax['cash_tax']-capex-delta_wc
            w=waterfall(cash=cash,fcf=fcf,minimum=a['minimum_cash'],senior=senior,junior=junior,revolver=rev,lease=lease,senior_original=a['senior'],capacity=a['capacity'],amort_rate=t['senior_amort_rate'],lease_annual=t['lease_amort_annual'],sweep=t['cash_sweep'])
            sf_amort=min(sf,a['senior']*t['debt_fee_rate']/t['debt_fee_life_years']/4)
            sf_writeoff=(sf-sf_amort)*(w.amort+w.senior_pay)/senior if senior>0 else 0
            jf_amort=min(jf,a['junior']*t['debt_fee_rate']/t['debt_fee_life_years']/4)
            rf_amort=min(rf,a['revolver_fees']/t['revolver_fee_life_years']/4)
            fee_expense=sf_amort+sf_writeoff+jf_amort+rf_amort
            sf-=sf_amort+sf_writeoff
            jf-=jf_amort
            rf-=rf_amort
            ppa_release=(step_dep+step_amort)*t['tax_rate']
            cumulative_ppa_release+=ppa_release
            book_tax=tax['cash_tax']-ppa_release
            ebit=ebitda-da
            ni=ebit-cash_interest-fee_expense-book_tax
            retained+=ni
            total_assets=w.cash+ar+inv+h['other_current_assets']+old_ppe+new_ppe+step_ppe+h['rou']+a['goodwill']+old_int+step_int+h['dta']+h['other_assets']+rf
            total_debt=w.senior+w.junior+w.revolver+w.lease
            total_liabilities=ap+h['other_current_liabilities']+h['current_operating_lease']+h['operating_lease']+h['dtl']+a['ppa_dtl']-cumulative_ppa_release+h['other_liabilities']+total_debt-sf-jf
            equity=a['equity']+retained
            r=dict(date=d.isoformat(),days=days,battery=bsales,auto=asales,revenue=sales,cogs=cogs,gross_profit=gross,variable_opex=variable,sga=fixed/4,recurring=recurring,ebitda=ebitda,capex=capex,old_dep=depreciation,new_dep=new_dep,step_dep=step_dep,old_amort=amort,step_amort=step_amort,da=da,ppe=old_ppe+new_ppe+step_ppe,intangibles=old_int+step_int,ar=ar,inventory=inv,ap=ap,delta_wc=delta_wc,senior_begin=senior,junior_begin=junior,rev_begin=rev,lease_begin=lease,cash_begin=cash,senior_interest=senior_interest,junior_interest=junior_interest,rev_interest=rev_interest,lease_interest=lease_interest,commitment_fee=commit,cash_interest=cash_interest,**tax,fcf=fcf,senior=w.senior,junior=w.junior,revolver=w.revolver,lease=w.lease,draw=w.draw,revolver_pay=w.revolver_pay,senior_pay=w.senior_pay,amort=w.amort,lease_pay=w.lease_pay,cash=w.cash,liquidity_gap=w.liquidity_gap,senior_fees=sf,junior_fees=jf,revolver_fees=rf,fee_expense=fee_expense,ppa_release=ppa_release,book_tax=book_tax,ebit=ebit,net_income=ni,assets=total_assets,liabilities=total_liabilities,equity=equity,bs_check=total_assets-total_liabilities-equity,debt=total_debt)
            quarterly.append(r)
            senior,junior,rev,lease,cash=w.senior,w.junior,w.revolver,w.lease,w.cash
            previous_date=d
    last=quarterly[-1]
    exit_ebitda=sum(q['ebitda'] for q in quarterly[-4:])
    exit_ev=exit_ebitda*t['exit_multiple']
    proceeds_raw=exit_ev-last['debt']+max(0,last['cash']-a['minimum_cash'])-h['pension_deficit']-exit_ev*t['exit_fee_rate']
    feasible=all(q['liquidity_gap']<=1e-8 for q in quarterly)
    proceeds=max(0.0,proceeds_raw)
    irr=xirr([-a['sponsor'],proceeds],[date(2025,12,31),date(2030,12,31)]) if feasible else None
    returns=dict(exit_ebitda=exit_ebitda,exit_ev=exit_ev,proceeds=proceeds,moic=proceeds/a['sponsor'] if feasible else None,xirr=irr,feasible=feasible,max_liquidity_gap=max(q['liquidity_gap'] for q in quarterly),exit_debt=last['debt'],entry_debt=a['senior']+a['junior']+b['lease'])
    return dict(case=case,normalization=n,bridge=b,transaction=a,quarters=quarterly,returns=returns)
