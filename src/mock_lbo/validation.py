"""Independent accounting identities and cached-workbook comparisons."""
import copy
import json
from pathlib import Path
from .sources import ROOT, load_inputs, historical_checks
from .operating import run_model
from .workbook import read_workbook, column


def validate_model(model: dict) -> dict[str, float]:
    a, b = model['transaction'], model['bridge']
    checks = {'sources_uses': a['sources']-a['uses'],
              'opening_balance': a['assets']-a['liabilities']-a['equity'],
              'bridge_balance': b['assets']-b['liabilities']-b['equity']}
    for i, q in enumerate(model['quarters']):
        checks[f'q{i+1}_balance'] = q['bs_check']
        checks[f'q{i+1}_debt'] = q['senior_begin']+q['junior_begin']+q['rev_begin']+q['lease_begin']+q['draw']-q['amort']-q['lease_pay']-q['revolver_pay']-q['senior_pay']-q['debt']
        checks[f'q{i+1}_cash'] = q['cash_begin']+q['fcf']+q['draw']-q['amort']-q['lease_pay']-q['revolver_pay']-q['senior_pay']-q['cash']
        checks[f'q{i+1}_negative_debt'] = min(0,q['senior'],q['junior'],q['revolver'],q['lease'])
        checks[f'q{i+1}_capacity'] = max(0,q['revolver']-a['capacity'])
    if any(abs(v)>1e-6 for v in checks.values()):
        raise AssertionError({k:v for k,v in checks.items() if abs(v)>1e-6})
    return checks


def audit_workbook(file: Path, root: Path = ROOT) -> dict:
    """Audit release inputs and saved values, separately from native recalculation evidence."""
    h, assumptions = load_inputs(root)
    values, formulas = read_workbook(file)
    errors = [(s,c,v) for s, cells in values.items() for c,v in cells.items()
              if isinstance(v,str) and v.startswith(('#REF!','#DIV/0!','#VALUE!','#NUM!','#NAME?','#NULL!'))]
    if errors:
        raise AssertionError(errors[:10])
    for s,cells in formulas.items():
        if s != 'Checks' and any("'Checks'!" in f for f in cells.values()):
            raise AssertionError('Checks feed a business calculation')
    case = ['base','downside','upside'][int(values['Sensitivities']['D5'])-1]
    assumptions=copy.deepcopy(assumptions)
    # Read editable workbook inputs, so audits remain useful after assumption changes.
    for key in assumptions['transaction']:
        matches=[cell for cell,value in values['Assumptions'].items() if cell.startswith('C') and value==key.replace('_',' ')]
        if matches:
            assumptions['transaction'][key]=float(values['Assumptions']['D'+matches[0][1:]])
    for key in assumptions['base']:
        matches=[cell for cell,value in values['Assumptions'].items() if cell.startswith('C') and value==key.replace('_',' ')+' — active']
        if len(matches)!=1:
            raise AssertionError(f'Missing driver {key}')
        row=int(matches[0][1:])
        for ci,name in enumerate(('base','downside','upside'),1):
            assumptions[name][key]=[float(values['Assumptions'][f'{column(4+y)}{row+ci}']) for y in range(5)]
    assumptions['transaction']['entry_multiple']=float(values['Sensitivities']['D6'])
    assumptions['transaction']['exit_multiple']=float(values['Sensitivities']['D7'])
    for name in ('base','downside','upside'):
        assumptions[name]['reference_rate']=[v+float(values['Sensitivities']['D8']) for v in assumptions[name]['reference_rate']]
        assumptions[name]['dso']=[v+float(values['Sensitivities']['D9']) for v in assumptions[name]['dso']]
    model=run_model(h,assumptions,case)
    m=json.loads((root/'data/workbook_map.json').read_text())
    pairs=[('Operating Case','operating',{'annual_battery':None,'annual_auto':None,'bm':None,'am':None,'fixed':None,'annual_cogs':None,'pretax':None}),
           ('Debt Schedule','debt',{'gap':'liquidity_gap','sf':'senior_fees','jf':'junior_fees','rf':'revolver_fees','total_debt':'debt','pre_cash':None,'excess':None,'sf_begin':None,'sf_amort':None,'sf_writeoff':None,'jf_amort':None,'rf_amort':None}),
           ('Capex & DA','capital',{'old_ppe_begin':None,'old_ppe_end':None,'new_ppe_begin':None,'new_ppe_end':None,'step_ppe_begin':None,'step_ppe_end':None,'old_int_begin':None,'old_int_end':None,'step_int_end':None}),
           ('Working Capital','working',{'nwc':None,'opening':None,'delta':'delta_wc'}),
           ('Balance Sheet','balance',{'oca':None,'rou':None,'goodwill':None,'dta':None,'other':None,'revfee':'revolver_fees','ocl':None,'oplease':None,'dtl':None,'otherliab':None,'fees':None,'paidin':None,'retained':None})]
    differences=[]
    def compare(sheet: str, cell: str, expected: float | None) -> None:
        actual=values[sheet].get(cell)
        if expected is None:
            if actual!='n.a.':
                raise AssertionError((sheet,cell,actual,'n.a.'))
        elif not isinstance(actual,(int,float)):
            raise AssertionError((sheet,cell,actual,expected))
        else:
            diff=abs(actual-expected)
            tolerance=0.000001 if (sheet=='Returns' and cell=='D25') or (sheet=='Sensitivities' and (15<=int(''.join(filter(str.isdigit,cell)))<=19 or 35<=int(''.join(filter(str.isdigit,cell)))<=37)) else 0.001
            if diff>tolerance:
                raise AssertionError((sheet,cell,actual,expected))
            differences.append(diff)
    for sheet,mapkey,aliases in pairs:
        for key,row in m[mapkey].items():
            field=aliases.get(key,key)
            if field is None:
                continue
            for i,q in enumerate(model['quarters']):
                compare(sheet,f'{column(i+11)}{row}',q[field])
    for key,row in m['transaction'].items():
        compare('Sources & Uses',f'D{row}',model['transaction'][key])
    for key in ['moic','xirr','exit_ebitda','exit_ev','exit_debt','proceeds']:
        compare('Returns',f'D{m["returns"][key]}',model['returns'][key])
    # Every native table combination is recalculated independently, including operating changes.
    sensitivity_count=0
    for top,metric,operating in [(14,'xirr',False),(24,'moic',False),(34,'xirr',True),(42,'moic',True)]:
        for ri in range(3 if operating else 5):
            row=top+1+ri
            for ci in range(5):
                aa=copy.deepcopy(assumptions)
                aa['transaction']['exit_multiple']=float(values['Sensitivities'][f'{column(5+ci)}{top}'])
                cc=case
                if operating:
                    cc=['base','downside','upside'][ri]
                else:
                    aa['transaction']['entry_multiple']=float(values['Sensitivities'][f'D{row}'])
                rr=run_model(h,aa,cc)['returns']
                compare('Sensitivities',f'{column(5+ci)}{row}',rr[metric])
                sensitivity_count+=1
    for ri in range(3):
        for ci in range(5):
            aa=copy.deepcopy(assumptions)
            aa[case]['reference_rate']=[v-float(values['Sensitivities']['D8'])+float(values['Sensitivities'][f'D{51+ri}']) for v in aa[case]['reference_rate']]
            aa[case]['dso']=[v-float(values['Sensitivities']['D9'])+float(values['Sensitivities'][f'{column(5+ci)}50']) for v in aa[case]['dso']]
            rr=run_model(h,aa,case)['returns']
            compare('Sensitivities',f'{column(5+ci)}{51+ri}',rr['max_liquidity_gap'])
            sensitivity_count+=1
    native=sum(f=='DATA_TABLE' for sheet in formulas.values() for f in sheet.values())
    if native!=5:
        raise AssertionError(f'Expected five native tables, got {native}')
    return dict(case=case,numeric_comparisons=len(differences),sensitivity_combinations=sensitivity_count,
                max_absolute_difference=max(differences),native_data_tables=native,unexpected_formula_errors=len(errors),
                accounting_checks=len(validate_model(model)),historical_checks=len(historical_checks(root)))
