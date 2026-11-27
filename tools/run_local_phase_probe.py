"""Strict native pulse/startup/glitch/pause investigation, including keyboard."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1]
MODELS=['sim/hdl/hc_models.sv','sim/net02/package_models.sv','sim/net24/package_models_pulse_diagnostic.sv',
 'sim/net04/package_models.sv','sim/net19a/package_models.sv','sim/net14c/package_models_async.sv',
 'sim/net22/phase_packages.sv','sim/net23/clock_models.sv','sim/net24/backend_pulse_model.sv','sim/net25/warm_packages.sv',
 'sim/net26/local_video_probe.sv','sim/net26/local_reset_probe.sv','sim/net26/local_control_probe.sv','sim/net26/local_keyboard_probe.sv','sim/net26/tb_local_phase_probe.sv']

def main():
    configs=[]
    for policy in [0,1]:
        for phase in range(-1,16):
            for release in [60000,12000000]:configs.append({'PROFILE':1,'POLICY':policy,'INITIAL_PHASE':phase,'RAW_RELEASE_NS':release,'OFFSET_NS':39})
        for offset in [0,20,30,39,40,60,100]:
            for low in [5,20,50,100,300,1000]:configs.append({'PROFILE':1,'POLICY':policy,'RAW_LOW_NS':low,'OFFSET_NS':offset})
        for level in [0,1]:configs.append({'PROFILE':1,'POLICY':policy,'PAUSE_LEVEL':level,'OFFSET_NS':39})
    report={'date':'2026-11-26','scope':'Native pin variants, keyboard included, strict original HC clock monitors even underCLR0, independent5ns keyboard clock check. Selected delays and bounded binary asynchronous warm/local-reset only; not global PVT/MTBF/analog/POR/PCB proof.',
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in MODELS+['tools/run_local_phase_probe.py','tools/prepare_local_phase_checks.py']],
      'cases':[],'failures':[],'production_released':False}
    with tempfile.TemporaryDirectory(prefix='isa1-local-phase-') as tmp:
        work=Path(tmp)
        for index,params in enumerate(configs):
            cmd=['iverilog','-g2012','-Wall','-s','tb_drain_pulse',*[f'-Ptb_drain_pulse.{k}={v}' for k,v in params.items()],'-o',str(work/'test.vvp'),*[str(ROOT/n) for n in MODELS]]
            row={'parameters':params,'compile':run(cmd,work)}
            if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=120)
            r=row.get('execution',{});row['passed']=r.get('exit')==0 and 'RESULT ' in r.get('stdout','') and 'failures=0' in r.get('stdout','') and not row['compile']['stderr']
            report['cases'].append(row)
            if not row['passed']:report['failures'].append(params)
            (ROOT/'verification/net26/local-phase-probe.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps({'index':index+1,'total':len(configs),'parameters':params,'passed':row['passed'],'execution':r if not row['passed'] else None}),flush=True)
            if not row['passed']:return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
