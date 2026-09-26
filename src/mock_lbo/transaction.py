"""Historical earnings normalization, estimated close bridge and acquisition accounting."""


def normalize(h: dict[str, float], t: dict[str, float]) -> dict[str, float]:
    battery_margin = (h['battery_sales'] - h['battery_cost'] + h['battery_dep'] - h['current_credits']) / h['battery_sales']
    auto_margin = (h['auto_sales'] - h['auto_cost'] + h['auto_dep']) / h['auto_sales']
    underwritten = h['management_ebitda'] - h['sbc'] - h['current_credits'] - t['recurring_cost_reserve'] - h['adjusted_other_income']
    return dict(ebitda=underwritten, battery_margin=battery_margin, auto_margin=auto_margin,
                variable_opex=(h['advertising'] + h['rd']) / h['revenue'])


def closing_bridge(h: dict[str, float], t: dict[str, float], n: dict[str, float]) -> dict[str, float]:
    growth = (1 + t['bridge_volume_growth']) * (1 + t['bridge_price_growth'])
    battery = h['battery_fq1'] * growth
    auto = h['auto_fq1'] * growth
    revenue = battery + auto
    ebitda = battery*n['battery_margin'] + auto*n['auto_margin'] - revenue*n['variable_opex'] - h['adjusted_sga']/4 - t['recurring_cost_reserve']/4
    dep, amort = (h['da']-h['amortization'])/4, h['amortization']/4
    interest = t['bridge_interest_annual'] * 92/360
    pretax = ebitda-dep-amort-interest-t['bridge_fee_amort']
    taxes = max(0.0, pretax)*t['tax_rate']
    ni = pretax-taxes
    # Closing working-capital balances held at September levels: explicit bridge assumption.
    lease_pay = t['lease_amort_annual']/4
    cash = h['cash']+ebitda-interest-taxes-h['revenue']*0.03/4-t['bridge_debt_amort']-lease_pay
    ppe = h['ppe']+h['revenue']*0.03/4-dep
    intangible = h['intangibles']-amort
    financial_debt = h['financial_debt_face']+h['notes']-t['bridge_debt_amort']
    finance_lease = h['finance_lease']-lease_pay
    remaining_fees = h['old_finance_fees']-t['bridge_fee_amort']
    assets = h['assets']-h['cash']-h['ppe']-h['intangibles']+cash+ppe+intangible
    liabilities = h['liabilities']-t['bridge_debt_amort']-lease_pay+t['bridge_fee_amort']
    return dict(battery=battery,auto=auto,revenue=revenue,ebitda=ebitda,dep=dep,amort=amort,interest=interest,taxes=taxes,net_income=ni,cash=cash,ppe=ppe,intangibles=intangible,financial_debt=financial_debt,lease=finance_lease,remaining_fees=remaining_fees,assets=assets,liabilities=liabilities,equity=h['equity']+ni)


def acquisition(h: dict[str, float], t: dict[str, float], n: dict[str, float], b: dict[str, float]) -> dict[str, float]:
    ev = n['ebitda']*t['entry_multiple']
    seller = ev-b['financial_debt']-b['lease']+b['cash']-h['pension_deficit']
    senior = n['ebitda']*t['senior_leverage']
    junior = n['ebitda']*t['junior_leverage']
    capacity = n['ebitda']*t['revolver_leverage']
    fees = ev*t['transaction_fee_rate']
    debt_fees = (senior+junior)*t['debt_fee_rate']
    rev_fees = capacity*t['revolver_fee_rate']
    minimum = h['revenue']*t['minimum_cash_rate']
    uses = seller+b['financial_debt']+fees+debt_fees+rev_fees+minimum
    sponsor = uses-senior-junior-b['cash']
    ppa_dtl = (t['ppe_stepup']+t['intangible_stepup'])*t['tax_rate']
    identifiable_net = b['assets']-h['goodwill']+t['ppe_stepup']+t['intangible_stepup']-b['liabilities']-b['remaining_fees']-ppa_dtl
    goodwill = seller-identifiable_net
    assets = b['assets']-b['cash']-h['goodwill']+minimum+goodwill+t['ppe_stepup']+t['intangible_stepup']+rev_fees
    liabilities = b['liabilities']-b['financial_debt']+b['remaining_fees']+senior+junior-debt_fees+ppa_dtl
    return dict(ev=ev,seller=seller,senior=senior,junior=junior,capacity=capacity,transaction_fees=fees,debt_fees=debt_fees,revolver_fees=rev_fees,minimum_cash=minimum,uses=uses,sponsor=sponsor,sources=sponsor+senior+junior+b['cash'],ppa_dtl=ppa_dtl,identifiable_net=identifiable_net,goodwill=goodwill,assets=assets,liabilities=liabilities,equity=sponsor-fees)
