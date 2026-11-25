"""Force both reset synchronizers into recovery; preserve strict rejection."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net16/native'
def main():
    names=['sim/net03/package_models.sv','sim/net14c/package_models_async.sv','hardware/reset_domains/reset_domains_netlist.sv','sim/net16/tb_reset_apertures.sv']
    report={'date':'2026-11-25','scope':'Binary reset-boundary policies only, not physical metastability or MTBF approval','sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+['tools/run_reset_apertures.py']], 'runs':[],'negative':[],'failures':[]}
    with tempfile.TemporaryDirectory(prefix='isa1-aperture-') as tmp:
        work=Path(tmp)
        for policy,strict in [(0,0),(1,0),(1,1)]:
            sources=[ROOT/n for n in names]
            if strict:
                original=sources[2].read_text();assert original.count('.RESET_BOUNDARY(1)')==4
                source=work/'strict.sv';source.write_text(original.replace('.RESET_BOUNDARY(1)','.RESET_BOUNDARY(0)'));sources[2]=source
            cmd=['iverilog','-g2012','-Wall','-s','tb_reset_apertures',f'-Ptb_reset_apertures.RESOLVE_LATE={policy}','-o',str(work/'test.vvp'),*map(str,sources)]
            row={'resolution_policy':policy,'strict_boundary':strict,'compile':run(cmd,work)}
            if not row['compile']['exit']:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=120)
            row['passed']=row['compile']['exit']==0 and ((row.get('execution',{}).get('exit',0)!=0 and 'AHC74 reset recovery violation' in row['execution']['stdout']) if strict else (row.get('execution',{}).get('exit')==0 and 'aperture_cuts=10' in row['execution']['stdout'] and 'failures=0' in row['execution']['stdout']))
            if strict:row['expected_rejection']=True;report['negative'].append(row)
            else:report['runs'].append(row)
            if not row['passed']:report['failures'].append([policy,strict])
            (OUT/'apertures.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(row),flush=True)
            if report['failures']:return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
