"""Investigate global clock pulse width during phase-swept reset transitions."""
import hashlib
import json
from pathlib import Path
import re
import tempfile
from run_rtl import run
from run_request_skew_probe import once

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net24'


def main():
    inputs=['sim/net22/video_common_async_netlist.sv','hardware/clocked_reset/clocked_reset_netlist.sv',
            'hardware/common_request/common_request_netlist.sv','sim/net14c/package_models_async.sv','sim/net03/package_models.sv']
    video=(ROOT/inputs[0]).read_text().replace('module video_common_clock_netlist','module net24_video_pulse_netlist')
    video=once(video,'EARLY_CAPTURE=0,RESOLVE_LATE=1)','EARLY_CAPTURE=0,RESOLVE_LATE=1,PROFILE=0)')
    video=once(video,'net14b_ahc74 #(.TIMED(TIMED),.EARLY(0 && EARLY_CAPTURE)) U11_0',
               'net24_backend_ff #(.TIMED(TIMED),.RISE_T(10.5),.FALL_T(PROFILE?1:10.5),.EARLY(0 && EARLY_CAPTURE)) U11_0')
    reset=(ROOT/inputs[1]).read_text().replace('module clocked_reset_netlist','module net24_reset_pulse_netlist')
    reset=once(reset,'TIMED=0,RESOLVE_LATE=1,parameter realtime','TIMED=0,RESOLVE_LATE=1,PROFILE=0,parameter realtime')
    for net in ['BACKEND_ROOT','ACCESS_CLK']:
        reset=once(reset,f'assign #(TIMED?10:0) n_{net}=',
                   f'assign #(TIMED?(PROFILE?8.5:10):0,TIMED?(PROFILE?1:10):0) n_{net}=')
    control=(ROOT/inputs[2]).read_text().replace('module common_request_netlist','module net24_control_pulse_netlist')
    control=once(control,'TIMED=0,EARLY=0)','TIMED=0,EARLY=0,PROFILE=0)')
    for net in ['BUF_3_3','BUF_3_4','BUF_4_1']:
        control=once(control,f'assign #GATE_T n_{net}=',
                     f'assign #(TIMED?(PROFILE?8.5:10):0,TIMED?(PROFILE?1:10):0) n_{net}=')
    ff=re.search(r'module net14b_ahc74 .*?endmodule',(ROOT/inputs[3]).read_text(),re.S).group(0)
    ff=once(ff,'module net14b_ahc74','module net24_backend_ff')
    ff=once(ff,'RESOLVE_LATE=1)','RESOLVE_LATE=1,parameter realtime RISE_T=10.5,FALL_T=10.5)')
    assert ff.count('q<=#CQ d')==2
    ff=ff.replace('q<=#CQ d','q<=#(TIMED?(d?RISE_T:FALL_T):0) d')
    diagnostics=once((ROOT/inputs[4]).read_text(),'$fatal(1,"DFF clock pulse violation");',
                     '$fatal(1,"DFF clock pulse violation measured_ns=%0.3f required_ns=20 clr_n=%b",$realtime-clock_changed,clr_n);')
    generated={'video_reset_pulse_probe.sv':video,'reset_pulse_probe.sv':reset,'control_pulse_probe.sv':control,
               'backend_pulse_model.sv':'`timescale 1ns/1ps\n'+ff+'\n','package_models_pulse_diagnostic.sv':diagnostics}
    for name,text in generated.items():(ROOT/'sim/net24'/name).write_text('// GENERATED selected pulse investigation; original predicates/guards retained.\n'+text)
    names=['sim/hdl/hc_models.sv','sim/net02/package_models.sv','sim/net24/package_models_pulse_diagnostic.sv',
           'sim/net04/package_models.sv','sim/net19a/package_models.sv','sim/net14c/package_models_async.sv',
           'sim/net22/phase_packages.sv','sim/net23/clock_models.sv']
    names += ['sim/net24/'+name for name in generated if name!='package_models_pulse_diagnostic.sv']
    names += ['sim/net24/tb_reset_pulse_probe.sv']
    source_names=list(dict.fromkeys(names+inputs+['tools/run_reset_pulse_probe.py','tools/run_request_skew_probe.py',
                        'references/ti/sn74hc74.pdf','references/ti/sn74ahc125.pdf','references/ti/sn74ahc74.pdf']))
    report={'date':'2026-11-26','scope':'Simulation-only copies of native source/reset/video/controller graphs. PROFILE1 assigns backendCQ rise10.5/fall1ns and three AHC125 clock stages rise8.5/fall1ns; other predecessor delays fixed. Original timing predicates preserved, only clock-pulse diagnostic message adds measured width. Not a silicon/analog/MTBF/full PVT proof.',
            'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in source_names],
            'baseline':[],'investigations':[],'failures':[],'production_released':False}
    with tempfile.TemporaryDirectory(prefix='isa1-reset-pulse-') as tmp:
        work=Path(tmp)
        for profile in (0,1):
            for offset in (-1,0,20,30,39,40,60,100):
                command=['iverilog','-g2012','-Wall','-s','tb_reset_pulse_probe',
                         f'-Ptb_reset_pulse_probe.PROFILE={profile}',f'-Ptb_reset_pulse_probe.OFFSET_NS={offset}',
                         '-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names]]
                row={'profile':profile,'raw_after_backend_fall_ns':offset,'compile':run(command,work)}
                if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=60)
                result=row.get('execution',{});output=result.get('stdout','')
                row['completed']=result.get('exit')==0 and 'RESULT ' in output and 'failures=0' in output
                row['pulse_constraint_rejected']=result.get('exit') not in (None,0) and 'DFF clock pulse violation measured_ns=' in output
                accepted=row['completed'] if not profile or offset<0 else row['completed'] or row['pulse_constraint_rejected']
                row['investigation_recorded']=row['compile']['exit']==0 and not row['compile']['stderr'] and accepted
                report['investigations' if profile else 'baseline'].append(row)
                if not row['investigation_recorded']:report['failures'].append([profile,offset])
                (OUT/'reset-pulse-probe.json').write_text(json.dumps(report,indent=2)+'\n')
                print(json.dumps({'profile':profile,'offset':offset,'completed':row['completed'],
                                  'pulse_rejected':row['pulse_constraint_rejected'],'execution':result if not row['completed'] else None}),flush=True)
                if not row['investigation_recorded']:return 1
    report['reset_transition_pulse_envelope_qualified']=False
    report['rejected_profile_cases']=sum(r['pulse_constraint_rejected'] for r in report['investigations'])
    (OUT/'reset-pulse-probe.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'cases':16,'rejected_profile_cases':report['rejected_profile_cases'],'failures':report['failures']}))
    return 0


if __name__=='__main__':raise SystemExit(main())
