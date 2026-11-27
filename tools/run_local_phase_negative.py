"""Revert each physical NET26 change separately in simulation-only copies."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_local_phase_probe import MODELS
from run_request_skew_probe import once
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1]

def main():
    inputs=['sim/net26/local_reset_probe.sv','sim/net26/local_video_probe.sv','sim/net26/local_keyboard_probe.sv']
    reset=(ROOT/inputs[0]).read_text()
    reset=once(reset,'assign access_clk=n_BACKEND;', 'assign #(TIMED?(PROFILE?8.5:10):0,TIMED?(PROFILE?1:10):0) access_clk=n_BACKEND_ROOT;')
    video=(ROOT/inputs[1]).read_text()
    lines=video.splitlines();indexes=[i for i,s in enumerate(lines) if ') U37_1(' in s];assert len(indexes)==1
    i=indexes[0];assert lines[i].count(',n_LOCAL_RESET_N,')==1
    lines[i]=lines[i].replace(',n_LOCAL_RESET_N,',',reverted_local_q,')
    lines.insert(i,'wire reverted_local_q;\nassign #GATE_T n_LOCAL_RESET_N=n_SAFE & n_PHASE_RUN;')
    video='\n'.join(lines)+'\n'
    keyboard=(ROOT/inputs[2]).read_text()
    keyboard=once(keyboard,'net19_ahc174 #(.TIMED(TIMED)) U1(', 'hc174_model #(.TIMED(TIMED)) U1(')
    generated={'revert_clock':reset,'revert_local':video,'revert_keyboard':keyboard}
    for name,s in generated.items():(ROOT/f'sim/net26/{name}.sv').write_text('// NEGATIVE only: physical predecessor connection/family projected, candidate native files unchanged.\n'+s)
    all_names=list(dict.fromkeys(MODELS+inputs+[f'sim/net26/{n}.sv' for n in generated]+['tools/run_local_phase_negative.py']))
    report={'date':'2026-11-26','scope':'Three independent one-change reversions; original strict clock/recovery predicates retained. Not approval of another circuit.',
       'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in all_names], 'runs':[],'failures':[]}
    cases=[('revert_clock',inputs[0],{'PROFILE':1,'INITIAL_PHASE':4,'RAW_RELEASE_NS':60000,'POLICY':0},'DFF clock pulse violation measured_ns=7.722 required_ns=20 clr_n=0','control.genblk1.U4_check_second'),
        ('revert_local',inputs[1],{'PROFILE':1,'RAW_LOW_NS':50,'OFFSET_NS':39,'POLICY':0},'AHC74 reset recovery violation','video.U36_1'),
        ('revert_keyboard',inputs[2],{'PROFILE':1,'INITIAL_PHASE':4,'RAW_RELEASE_NS':60000,'POLICY':0},'DFF clock pulse violation measured_ns=7.722 required_ns=20 clr_n=0','keyboard.U1.genblk1.check_state')]
    with tempfile.TemporaryDirectory(prefix='isa1-local-negative-') as tmp:
        work=Path(tmp)
        for name,replace,params,expected,scope in cases:
            names=[f'sim/net26/{name}.sv' if n==replace else n for n in MODELS]
            cmd=['iverilog','-g2012','-Wall','-s','tb_drain_pulse',*[f'-Ptb_drain_pulse.{k}={v}' for k,v in params.items()],'-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names]]
            row={'negative':name,'parameters':params,'compile':run(cmd,work)}
            if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=120)
            r=row.get('execution',{});row['passed']=row['compile']['exit']==0 and not row['compile']['stderr'] and r.get('exit') not in (None,0) and expected in r.get('stdout','') and scope in r.get('stdout','')
            report['runs'].append(row)
            if not row['passed']:report['failures'].append(name)
            (ROOT/'verification/net26/local-phase-negative.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(row),flush=True)
            if not row['passed']:return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
