"""Conditional native reset logic tests; no physical metastability guarantee."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net16/native'
def main():
    names=['sim/net03/package_models.sv','sim/net14c/package_models_async.sv','hardware/reset_domains/reset_domains_netlist.sv','sim/net16/tb_reset_domains.sv']
    report={'date':'2026-11-25','scope':'Native pin graph with bounded inertial RC and binary external reset resolution; no MTBF, short pulse train, supervisor or full CPU integration approval',
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+['tools/run_reset_domains.py','tools/build_reset_domains.py','verification/net16/native/reset_domains.xml']],
      'runs':[],'negative':[],'failures':[],'production_released':False}
    def save():(OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='isa1-reset-') as tmp:
        work=Path(tmp)
        configs=[(t,p,a,r,0,0) for t in (0,1) for p in (0,1) for a in (1000,19000) for r in (2000,42000)]+[(1,1,1000,42000,1,0),(1,1,1000,42000,0,1)]
        for timed,policy,assertion,release,early,bypass in configs:
            cmd=['iverilog','-g2012','-Wall','-s','tb_reset_domains',f'-Ptb_reset_domains.TIMED={timed}',f'-Ptb_reset_domains.RESOLVE_LATE={policy}',f'-Ptb_reset_domains.ASSERT_DELAY={assertion}',f'-Ptb_reset_domains.RELEASE_DELAY={release}',f'-Ptb_reset_domains.FAULT_EARLY={early}',f'-Ptb_reset_domains.FAULT_CPU={bypass}','-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names]]
            row={'timed':timed,'resolution_policy':policy,'assertion_delay_ns':assertion,'release_delay_ns':release,'early_reset_fault':early,'cpu_ready_bypass_fault':bypass,'compile':run(cmd,work)}
            if not row['compile']['exit']:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=120)
            if early or bypass:
                expected='state reset before WE inhibition' if early else 'access released while CPU clock stopped'
                row['expected_rejection']=True;row['passed']=row['compile']['exit']==0 and row.get('execution',{}).get('exit',0)!=0 and expected in row['execution']['stdout'];report['negative'].append(row)
            else:
                row['passed']=row['compile']['exit']==0 and row.get('execution',{}).get('exit')==0 and 'reset_cuts=32 cpu_pauses=11 backend_pauses=11' in row['execution']['stdout'];report['runs'].append(row)
            if not row['passed']:report['failures'].append([timed,policy,assertion,release,early,bypass])
            save();print(json.dumps(row),flush=True)
            if report['failures']:return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
