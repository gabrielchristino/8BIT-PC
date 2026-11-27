"""Four two-frame tests with native memory/controller/video/reset/keyboard."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1]

def main():
    origin=ROOT/'verification/net30/memory-pin-results.json'
    prior=json.loads(origin.read_text());assert not prior['failures']
    names=[p for p in prior['runs'][0]['compile']['command'] if p.endswith('.sv')]
    names=[Path(p) for p in names if not p.endswith('/tb_load_memory.sv')]
    bench=ROOT/'sim/net30/tb_load_frames.sv';names.append(bench)
    report={'date':'2026-11-26','scope':'Two full seeded frames per policy/early-capture scenario, six native memory-subsystem blocks without CPU instance/execution. Includes four spare buffers. Cold RAW held low50us beyond19us RC bound; VB and VRAM seeded, qualified oscillator VDD/RAW digital. No PVT/MTBF/analog/DAC/PCB approval.',
        'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in names+[origin,Path(__file__)]],
        'runs':[],'failures':[],'production_released':False}
    target=ROOT/'verification/net30/native-frame-results.json'
    with tempfile.TemporaryDirectory(prefix='isa1-load-frames-') as tmp:
        work=Path(tmp)
        for policy in [0,1]:
            for early in [0,1]:
                command=['iverilog','-g2012','-Wall','-s','tb_load_frames',f'-Ptb_load_frames.POLICY={policy}',f'-Ptb_load_frames.EARLY_CAPTURE={early}','-o',str(work/'test.vvp'),*map(str,names)]
                row={'policy':policy,'early':early,'compile':run(command,work)}
                if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=300)
                result=row.get('execution',{})
                row['passed']=row['compile']['exit']==0 and not row['compile']['stderr'] and result.get('exit')==0 and 'RESULT native_frames=2 samples=210000 visible=153600 hsync=25200 vsync=800' in result.get('stdout','') and 'grant_starts=32' in result['stdout'] and 'failures=0' in result['stdout']
                report['runs'].append(row)
                if not row['passed']:report['failures'].append([policy,early])
                target.write_text(json.dumps(report,indent=2)+'\n')
                print(json.dumps({'policy':policy,'early':early,'passed':row['passed'],'execution':result}),flush=True)
                if not row['passed']:return 1
    return 0

if __name__=='__main__':
    if '--worker' in sys.argv:raise SystemExit(main())
    import run_distributed_load_job as bounded
    bounded.JOBS={'frames-qualified-start':['tools/run_distributed_load_frames.py','--worker']}
    sys.argv=[sys.argv[0],'frames-qualified-start'];raise SystemExit(bounded.main())
