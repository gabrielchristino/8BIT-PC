"""Cross-check a four-state compiled engine before any engineering adoption."""
import hashlib
import json
from pathlib import Path
import re
import tempfile
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1]
EXE=Path('/home/gabri/.local/opt/isa1-cvc-source/build64/cvc64')
OUT=ROOT/'verification/net26/tool-research'

def main():
    report={'date':'2026-11-26','scope':'Tool calibration only. Default four-state CVC, no2state/no ignored timing flags. Compare actual original guards and smoke semantics against Icarus before any adoption.',
        'executable':{'path':str(EXE),'sha256':hashlib.sha256(EXE.read_bytes()).hexdigest()},
        'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in ['tools/calibrate_compiled_simulator.py','sim/net26/compiled_smoke.sv','sim/net25/warm_packages.sv','sim/net25/tb_warm_packages.sv']],
        'runs':[],'failures':[],'adopted_for_full_simulation':False,'production_released':False}
    def save():(OUT/'cvc-calibration.json').write_text(json.dumps(report,indent=2)+'\n')
    cases=[('smoke',None,None,None)]+[('warm',c,b,p) for c,b,p in [(0,0,0)]+[(c,0,0) for c in range(1,7)]+[(c,1,p) for c in range(4) for p in [0,1]]+[(c,1,0) for c in [4,5,6]]]
    with tempfile.TemporaryDirectory(prefix='isa1-cvc-calibration-') as tmp:
        parent=Path(tmp)
        for index,(name,case,boundary,policy) in enumerate(cases):
            work=parent/str(index);work.mkdir()
            if name=='smoke':
                bench=ROOT/'sim/net26/compiled_smoke.sv';libraries=[];top='compiled_smoke';negative=False
            else:
                text=(ROOT/'sim/net25/tb_warm_packages.sv').read_text()
                old='parameter CASE=0,BOUNDARY=0,POLICY=0;';assert text.count(old)==1
                text=text.replace(old,f'parameter CASE={case},BOUNDARY={boundary},POLICY={policy};')
                bench=work/'tb_warm_packages.sv';bench.write_text(text)
                libraries=[ROOT/'sim/net25/warm_packages.sv'];top='tb_warm_packages';negative=case>0 and (not boundary or case>=4)
            cvc_cmd=[str(EXE),'-sv','-o',str(work/'compiled'),str(bench)]
            for lib in libraries:cvc_cmd+=['-v',str(lib)]
            row={'name':name,'case':case,'boundary':boundary,'policy':policy,'negative':negative,
                'compile_cvc':run(cvc_cmd,work,timeout=120)}
            if row['compile_cvc']['exit']==0 and (work/'compiled').is_file():row['execution_cvc']=run([str(work/'compiled')],work,timeout=30)
            cmd=['iverilog','-g2012','-Wall','-s',top,'-o',str(work/'icarus.vvp'),*map(str,libraries),str(bench)]
            row['compile_icarus']=run(cmd,work)
            if row['compile_icarus']['exit']==0:row['execution_icarus']=run(['vvp',str(work/'icarus.vvp')],work,timeout=30)
            cvc=row.get('execution_cvc',{});icarus=row.get('execution_icarus',{})
            if negative:
                expected={1:'data setup violation',2:'reset recovery violation',3:'data hold violation',4:'clock pulse violation',5:'clear pulse violation',6:'clock outside95MHz qualification envelope'}[case]
                row['passed']=cvc.get('exit') not in (None,0) and icarus.get('exit') not in (None,0) and expected in cvc.get('stdout','') and expected in icarus.get('stdout','')
            else:
                results=[re.findall(r'^RESULT .*$',r.get('stdout',''),re.M) for r in [cvc,icarus]]
                row['passed']=cvc.get('exit')==0 and icarus.get('exit')==0 and len(results[0])==1 and results[0]==results[1] and 'failures=0' in results[0][0]
            report['runs'].append(row)
            if not row['passed']:report['failures'].append(index)
            save();print(json.dumps({'index':index,'name':name,'passed':row['passed'],'cvc':row.get('compile_cvc') if not row['passed'] else None,'execution_cvc':cvc if not row['passed'] else None}),flush=True)
            if not row['passed']:return 1
    report['unit_calibration_equivalent']=True;save();return 0

if __name__=='__main__':raise SystemExit(main())
