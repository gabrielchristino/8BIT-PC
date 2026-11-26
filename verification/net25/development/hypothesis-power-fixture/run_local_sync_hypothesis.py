"""Simulation-only hypothesis: extra local reset FF pair clocked by phase1.

Not a native schematic or accepted circuit. Parent NET25 files frozen.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from run_request_skew_probe import once
from run_phase_drain_probe import MODELS
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1]

def main():
    source='sim/net25/video_drain_probe.sv'
    text=(ROOT/source).read_text()
    old='assign #GATE_T n_LOCAL_RESET_N=n_SAFE & n_PHASE_RUN;'
    new='''// HYPOTHESIS ONLY: one additional dual AHC74 package, clock on P1.
wire local_stage0,local_unused0,local_unused1;
net14b_ahc74 #(.TIMED(TIMED),.RESET_BOUNDARY(1),.FIRST_STAGE(1),.RESOLVE_LATE(RESOLVE_LATE)) HYP_LOCAL0(n_P1,n_SAFE,1'b1,1'b1,local_stage0,local_unused0,1'b1);
net14b_ahc74 #(.TIMED(TIMED),.RESET_BOUNDARY(1),.FIRST_STAGE(0),.RESOLVE_LATE(RESOLVE_LATE)) HYP_LOCAL1(n_P1,n_SAFE,1'b1,local_stage0,n_LOCAL_RESET_N,local_unused1,1'b1);'''
    text=once(text,old,new)
    dest='sim/net25/local_sync_hypothesis.sv';(ROOT/dest).write_text('// SIMULATION-ONLY hypothesis, no native graph approval.\n'+text)
    names=[dest if n==source else n for n in MODELS if n!='sim/net25/tb_drain_pulse.sv']
    names=['sim/net25/package_models_cold_diagnostic.sv' if n=='sim/net24/package_models_pulse_diagnostic.sv' else n for n in names]
    names+=['sim/net25/tb_drain_startup.sv']
    configs=[]
    for policy in [0,1]:
        for phase in range(-1,16):
            for release in [60000,12000000]:configs.append({'PROFILE':1,'POLICY':policy,'INITIAL_PHASE':phase,'RAW_RELEASE_NS':release,'OFFSET_NS':39})
        for offset in [0,20,30,39,40,60,100]:
            for low in [5,20,50,100,300,1000]:configs.append({'PROFILE':1,'POLICY':policy,'RAW_LOW_NS':low,'OFFSET_NS':offset})
        for level in [0,1]:configs.append({'PROFILE':1,'POLICY':policy,'PAUSE_LEVEL':level,'OFFSET_NS':39})
    report={'date':'2026-11-26','scope':'SIMULATION-ONLY extra phase1-clocked AHC74 reset pair. Native circuit not built. All CLR-low OPEN_RESET_CLOCK lines remain unqualified, active clock and recovery guards retained. Not analog/MTBF/PCB approval.',
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+[source,'tools/run_local_sync_hypothesis.py']],
      'cases':[],'failures':[],'production_released':False,'native_schematic_exists_for_hypothesis':False,'strict_cold_clock_pulses_qualified':False}
    with tempfile.TemporaryDirectory(prefix='isa1-local-sync-') as tmp:
        work=Path(tmp)
        for index,params in enumerate(configs):
            cmd=['iverilog','-g2012','-Wall','-s','tb_drain_pulse',*[f'-Ptb_drain_pulse.{k}={v}' for k,v in params.items()],'-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names]]
            row={'parameters':params,'compile':run(cmd,work)}
            if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=90)
            r=row.get('execution',{});row['passed']=r.get('exit')==0 and 'RESULT ' in r.get('stdout','') and 'failures=0' in r.get('stdout','') and not row['compile']['stderr']
            report['cases'].append(row)
            if not row['passed']:report['failures'].append(params)
            (ROOT/'verification/net25/local-sync-hypothesis.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps({'index':index+1,'total':len(configs),'parameters':params,'passed':row['passed'],'execution':r if not row['passed'] else None}),flush=True)
            if not row['passed']:return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
