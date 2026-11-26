"""Reject reverting either part of the simulation-only combined hypothesis."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_phase_drain_probe import MODELS
from run_rtl import run
from run_request_skew_probe import once

ROOT=Path(__file__).resolve().parents[1]

def main():
    base='sim/net25/tb_direct_backend_hypothesis.sv'
    old_clock='sim/net25/tb_direct_backend_revert_clock.sv'
    (ROOT/old_clock).write_text('// NEGATIVE: restores two upstream clock buffers.\n'+once((ROOT/base).read_text(),'.clk(backend)', '.clk(access_clock)'))
    common=[n for n in MODELS if n not in ['sim/net25/tb_drain_pulse.sv','sim/net25/video_drain_probe.sv']]
    cases=[('clock',old_clock,'sim/net25/direct_backend_video_hypothesis.sv',{'PROFILE':1,'INITIAL_PHASE':4,'RAW_RELEASE_NS':60000,'POLICY':0},'measured_ns=7.722 required_ns=20 clr_n=0'),
           ('local_reset',base,'sim/net25/video_drain_probe.sv',{'PROFILE':1,'RAW_LOW_NS':50,'OFFSET_NS':39,'POLICY':0},'AHC74 reset recovery violation tb_drain_pulse.video.U36_1')]
    report={'date':'2026-11-26','scope':'Negative calibration of simulation-only changes. Original strict monitors; no cold CLK exemption. No native schematic or analog qualification.',
        'runs':[],'failures':[],'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in list(dict.fromkeys(common+[base,old_clock,'sim/net25/direct_backend_video_hypothesis.sv','sim/net25/video_drain_probe.sv','tools/run_direct_backend_negative.py']))]}
    with tempfile.TemporaryDirectory(prefix='isa1-direct-negative-') as tmp:
        work=Path(tmp)
        for name,bench,video,params,expected in cases:
            cmd=['iverilog','-g2012','-Wall','-s','tb_drain_pulse',*[f'-Ptb_drain_pulse.{k}={v}' for k,v in params.items()],'-o',str(work/'test.vvp'),*[str(ROOT/n) for n in common+[video,bench]]]
            row={'negative':name,'parameters':params,'compile':run(cmd,work)}
            if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=90)
            r=row.get('execution',{});row['passed']=row['compile']['exit']==0 and not row['compile']['stderr'] and r.get('exit') not in (None,0) and expected in r.get('stdout','')
            report['runs'].append(row)
            if not row['passed']:report['failures'].append(name)
            (ROOT/'verification/net25/direct-backend-negative.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(row),flush=True)
            if not row['passed']:return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
