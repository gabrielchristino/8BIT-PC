"""Calibrate specified AHC174 monitor boundaries; not silicon qualification."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net19a/native'


def main():
    names=['sim/net19a/package_models.sv','sim/net19a/tb_ahc174_limits.sv']
    report={'date':'2026-11-26','scope':'Two selected model delay scenarios and five deliberately invalid timing stimuli. Datasheet-bound monitor calibration, not vendor SPICE/PVT/MTBF signoff',
            'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+['tools/check_ahc174_limits.py','references/ti/sn74ahc174.pdf']],
            'runs':[],'negative':[],'failures':[],'production_released':False}
    wanted={1:'AHC174 setup violation',2:'AHC174 hold violation',3:'AHC174 recovery violation',4:'AHC174 clear pulse violation',5:'AHC174 clock pulse violation'}
    with tempfile.TemporaryDirectory(prefix='isa1-ahc174-') as tmp:
        work=Path(tmp)
        for mode,early in [(0,0),(0,1)]+[(i,0) for i in wanted]:
            cmd=['iverilog','-g2012','-Wall','-s','tb_ahc174_limits',f'-Ptb_ahc174_limits.MODE={mode}',f'-Ptb_ahc174_limits.EARLY={early}','-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names]]
            row={'mode':mode,'early':early,'compile':run(cmd,work)}
            if not row['compile']['exit']:row['execution']=run(['vvp',str(work/'test.vvp')],work)
            output=row.get('execution',{})
            row['passed']=row['compile']['exit']==0 and (output.get('exit',0)!=0 and wanted[mode] in output.get('stdout','') if mode else output.get('exit')==0 and 'selected_cq_checked=1 failures=0' in output.get('stdout',''))
            if mode:row['expected_rejection']=wanted[mode]
            report['negative' if mode else 'runs'].append(row)
            if not row['passed']:report['failures'].append([mode,early])
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'ahc174-model-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'positive':len(report['runs']),'negative':len(report['negative']),'failures':report['failures']}));return int(bool(report['failures']))


if __name__=='__main__':raise SystemExit(main())
