"""Offline command-line demo and workbook audit."""
import argparse
import json
import logging
from pathlib import Path
from .sources import ROOT, load_inputs, historical_checks
from .operating import run_model
from .validation import validate_model, audit_workbook


def main() -> None:
    parser=argparse.ArgumentParser(description='Educational hypothetical LBO. Not investment advice.')
    parser.add_argument('command',choices=['demo','audit','validate'])
    parser.add_argument('--case',choices=['base','downside','upside'],default='base')
    parser.add_argument('--workbook',type=Path,default=ROOT/'excel/mock_lbo_energizer.xlsx')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(message)s')
    h,a=load_inputs()
    if args.command=='audit':
        result=audit_workbook(args.workbook)
    else:
        model=run_model(h,a,args.case)
        checks=validate_model(model)
        if any(abs(v)>0.15 for v in historical_checks().values()):
            raise AssertionError('Historical reconciliation failed')
        result=model if args.command=='demo' else {'case':args.case,'checks':len(checks),'max_accounting_residual':max(abs(v) for v in checks.values()),'returns':model['returns']}
    logging.info(json.dumps({'event':'command_completed','command':args.command,'case':result.get('case', args.case)}))
    payload=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload)
    else:
        print(payload)


if __name__=='__main__':
    main()
