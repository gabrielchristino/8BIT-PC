"""Calibrate explicitly bounded warm model against strict selected constraints."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1]

def main():
    names=['sim/net25/warm_packages.sv','sim/net25/tb_warm_packages.sv']
    report={'date':'2026-11-26','scope':'Strict default with explicit negative setup/hold/recovery/pulse/clear/frequency. Binary policies only at marked warm input/reset; no analog or bounded real metastability claim.',
        'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+['tools/run_warm_calibration.py','sim/net22/phase_packages.sv','references/net22/sn74ahc164.pdf']],
        'runs':[],'failures':[]}
    cases=[(0,0,0)]+[(c,0,0) for c in range(1,7)]+[(c,1,p) for c in range(4) for p in [0,1]]+[(c,1,0) for c in [4,5,6]]
    with tempfile.TemporaryDirectory(prefix='isa1-warm-calibration-') as tmp:
        work=Path(tmp)
        for case,boundary,policy in cases:
            cmd=['iverilog','-g2012','-Wall','-s','tb_warm_packages',f'-Ptb_warm_packages.CASE={case}',f'-Ptb_warm_packages.BOUNDARY={boundary}',f'-Ptb_warm_packages.POLICY={policy}',
                '-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names]]
            row={'case':case,'boundary':boundary,'policy':policy,'compile':run(cmd,work)}
            if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=30)
            negative=case>0 and (not boundary or case>=4)
            r=row.get('execution',{});output=r.get('stdout','')
            expected={1:'data setup violation',2:'reset recovery violation',3:'data hold violation',4:'clock pulse violation',5:'clear pulse violation',6:'clock outside95MHz qualification envelope'}
            row['expected_rejection']=negative
            row['passed']=row['compile']['exit']==0 and not row['compile']['stderr'] and (r.get('exit') not in (None,0) and expected[case] in output if negative else r.get('exit')==0 and 'RESULT ' in output and 'failures=0' in output)
            report['runs'].append(row)
            if not row['passed']:report['failures'].append([case,boundary,policy])
            (ROOT/'verification/net25/warm-calibration.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(row),flush=True)
            if not row['passed']:return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
