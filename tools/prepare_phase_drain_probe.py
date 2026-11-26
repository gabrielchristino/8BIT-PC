"""Separate simulation projection and original pulse monitors; no native edits."""
import hashlib
import json
from pathlib import Path
from run_request_skew_probe import once

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'sim/net25'

def main():
    DEST.mkdir(parents=True,exist_ok=True)
    names=['hardware/phase_drain_video/phase_drain_video_netlist.sv','hardware/phase_drain_reset/phase_drain_reset_netlist.sv','sim/net24/control_pulse_probe.sv']
    video=(ROOT/names[0]).read_text()
    video=once(video,'EARLY_CAPTURE=0)','EARLY_CAPTURE=0,RESOLVE_LATE=1,PROFILE=0)')
    video=once(video,'net22_ahc164 #(.TIMED(TIMED),.EARLY_CAPTURE(EARLY_CAPTURE)) U8',
               'net25_warm164 #(.TIMED(TIMED),.BOUNDARY(1),.RESOLVE_LATE(RESOLVE_LATE)) U8')
    for ref in ['U8','U9']:
        lines=video.splitlines()
        selected=[i for i,s in enumerate(lines) if ') '+ref+'(' in s]
        assert len(selected)==1
        i=selected[0];assert lines[i].endswith(',checks);')
        lines[i]=lines[i][:-len(',checks);')]+",1'b1);"
        video='\n'.join(lines)+'\n'
    video=once(video,'net14b_ahc74 #(.TIMED(TIMED),.EARLY(0 && EARLY_CAPTURE)) U11_0',
               'net24_backend_ff #(.TIMED(TIMED),.RISE_T(10.5),.FALL_T(PROFILE?1:10.5),.EARLY(0 && EARLY_CAPTURE)) U11_0')
    reset=(ROOT/names[1]).read_text()
    reset=once(reset,'TIMED=0,RESOLVE_LATE=1,parameter realtime','TIMED=0,RESOLVE_LATE=1,PROFILE=0,parameter realtime')
    for net in ['BACKEND_ROOT','ACCESS_CLK']:
        reset=once(reset,f'assign #(TIMED?10:0) n_{net}=',f'assign #(TIMED?(PROFILE?8.5:10):0,TIMED?(PROFILE?1:10):0) n_{net}=')
    control=(ROOT/names[2]).read_text().replace('net24_control_pulse_netlist','net25_control_pulse_netlist')
    outputs={'video_drain_probe.sv':video,'reset_drain_probe.sv':reset,'control_drain_probe.sv':control}
    for n,s in outputs.items():(DEST/n).write_text('// GENERATED investigation with bounded warm input/reset only; other original predicates retained.\n'+s)
    paths=names+['tools/prepare_phase_drain_probe.py']+['sim/net25/'+n for n in outputs]
    out=ROOT/'verification/net25';out.mkdir(parents=True,exist_ok=True)
    (out/'probe-origin.json').write_text(json.dumps({'date':'2026-11-26','scope':'Selected rise/fall delays as NET24. Bounded binary asynchronous warm input/reset only. Native strict models unchanged; not analog/MTBF/global PVT.',
        'files':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in paths]},indent=2)+'\n')

if __name__=='__main__':main()
