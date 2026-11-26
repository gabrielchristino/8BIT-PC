"""Verify row-enable restart; calibrate old CLR wiring and strict recovery."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net17/native'
def main():
    names=['sim/hdl/hc_models.sv','sim/net03/package_models.sv','sim/net04/package_models.sv','sim/net14c/package_models_async.sv','hardware/keyboard_500/keyboard_500_netlist.sv','sim/net17/tb_keyboard_resume.sv']
    report={'date':'2026-11-26','scope':'Native safe-release synchronization with binary boundary abstraction, no physical MTBF or global CPU integration approval','sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+['tools/run_keyboard_resume.py','tools/build_keyboard_500.py']], 'runs':[],'negative':[],'failures':[]}
    with tempfile.TemporaryDirectory(prefix='isa1-key-resume-') as tmp:
        work=Path(tmp)
        for timed,policy,bypass,strict in [(0,1,0,0),(1,0,0,0),(1,1,0,0),(1,1,1,0),(1,1,0,1)]:
            sources=[ROOT/n for n in names]
            if bypass or strict:
                s=sources[4].read_text()
                if bypass:
                    assert s.count(',n_TIMER_SAFE_CLEAR_N,')==4
                    s=s.replace(',n_TIMER_SAFE_CLEAR_N,',',n_G_10,')
                if strict:
                    assert s.count('.RESET_BOUNDARY(1)')==2
                    s=s.replace('.RESET_BOUNDARY(1)','.RESET_BOUNDARY(0)')
                source=work/'mutated.sv';source.write_text(s);sources[4]=source
            cmd=['iverilog','-g2012','-Wall','-s','tb_keyboard_resume',f'-Ptb_keyboard_resume.TIMED={timed}',f'-Ptb_keyboard_resume.RESOLVE_LATE={policy}','-o',str(work/'test.vvp'),*map(str,sources)]
            row={'timed':timed,'resolution_policy':policy,'old_clear_wiring':bypass,'strict_boundary':strict,'compile':run(cmd,work)}
            if not row['compile']['exit']:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=120)
            if bypass or strict:
                message='quiet timer advanced while row drivers disabled' if bypass else 'AHC74 reset recovery violation'
                row['expected_rejection']=True;row['passed']=row['compile']['exit']==0 and row.get('execution',{}).get('exit',0)!=0 and message in row['execution']['stdout'];report['negative'].append(row)
            else:
                row['passed']=row['compile']['exit']==0 and row.get('execution',{}).get('exit')==0 and 'late_enables=2' in row['execution']['stdout'] and 'failures=0' in row['execution']['stdout'];report['runs'].append(row)
            if not row['passed']:report['failures'].append([timed,policy,bypass,strict])
            (OUT/'resume-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(row),flush=True)
            if report['failures']:return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
