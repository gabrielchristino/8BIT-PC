"""Strict functional pulse acceptance, not collection of rejected pulses as pass."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net25'
MODELS=['sim/hdl/hc_models.sv','sim/net02/package_models.sv','sim/net24/package_models_pulse_diagnostic.sv',
 'sim/net04/package_models.sv','sim/net19a/package_models.sv','sim/net14c/package_models_async.sv',
 'sim/net22/phase_packages.sv','sim/net23/clock_models.sv','sim/net24/backend_pulse_model.sv','sim/net25/warm_packages.sv',
 'sim/net25/video_drain_probe.sv','sim/net25/reset_drain_probe.sv','sim/net25/control_drain_probe.sv','sim/net25/tb_drain_pulse.sv']

def main():
    report={'date':'2026-11-26','scope':'Selected digital pulse delays, two bounded asynchronous warm policies; all downstream strict predicates retained. No global PVT/MTBF/analog approval.',
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in MODELS+['tools/run_phase_drain_probe.py']],
      'cases':[],'failures':[],'production_released':False}
    with tempfile.TemporaryDirectory(prefix='isa1-phase-drain-') as tmp:
        work=Path(tmp)
        for policy in [0,1]:
            for profile in [0,1]:
                for offset in [-1,0,20,30,39,40,60,100]:
                    params={'PROFILE':profile,'POLICY':policy,'OFFSET_NS':offset}
                    command=['iverilog','-g2012','-Wall','-s','tb_drain_pulse',*[f'-Ptb_drain_pulse.{k}={v}' for k,v in params.items()],'-o',str(work/'test.vvp'),*[str(ROOT/n) for n in MODELS]]
                    row={'parameters':params,'compile':run(command,work)}
                    if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=90)
                    r=row.get('execution',{});row['passed']=r.get('exit')==0 and 'RESULT ' in r.get('stdout','') and 'failures=0' in r.get('stdout','') and not row['compile']['stderr']
                    report['cases'].append(row)
                    if not row['passed']:report['failures'].append(params)
                    (OUT/'drain-pulse.json').write_text(json.dumps(report,indent=2)+'\n')
                    print(json.dumps({'parameters':params,'passed':row['passed'],'execution':r if not row['passed'] else None}),flush=True)
                    if not row['passed']:return 1
    print(json.dumps({'passed':len(report['cases']),'failures':report['failures']}));return 0

if __name__=='__main__':raise SystemExit(main())
