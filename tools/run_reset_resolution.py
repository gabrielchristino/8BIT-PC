"""Sweep external reset release phases under explicit bounded binary resolution.

This supplements, never replaces, the strict recovery rejection and MTBF gate.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net14c'


def main():
    base=ROOT/'sim/net14b/tb_raster_reset.sv';text=base.read_text()
    text=text.replace('tb_raster_reset','tb_reset_resolution')
    text=text.replace('video_raster_netlist','video_system_netlist')
    text=text.replace('parameter integer TIMED=1;','parameter integer TIMED=1,RESOLVE_LATE=1;')
    text=text.replace('.TIMED(TIMED)) dut','.TIMED(TIMED),.RESOLVE_LATE(RESOLVE_LATE),.EARLY_CAPTURE(1)) dut')
    text=text.replace('k<8','k<40').replace('#(k<4?k*4:24+(k-4)*4);','#k;')
    a=text.index('   // Explicit cuts');b=text.index('   for(j=',a)
    text=text[:a]+'''   // Include the recovery aperture at the two marked external reset FFs.
   // Bounded binary resolution here is an assumption, not analog validation.
'''+text[b:]
    text=text.replace('recovery_aperture_excluded=1','recovery_aperture_excluded=0 bounded_binary_resolution=1')
    marker='$finish;'
    assert text.count(marker)==1
    text=text.replace(marker,'''if(dut.U8_0.recovery_events==0 || dut.U8_1.recovery_events==0)$fatal(1,"recovery aperture was not exercised");
   $display("BOUNDARY_EVENTS resolution_late=%0d stage1=%0d stage2=%0d analog_metastability_approved=0",RESOLVE_LATE,dut.U8_0.recovery_events,dut.U8_1.recovery_events);$finish;''')
    bench=ROOT/'sim/net14c/tb_reset_resolution.sv';bench.write_text(text)
    names=['sim/net14c/package_models_async.sv','sim/net14c/video_raster_async_netlist.sv','sim/net14c/tb_reset_resolution.sv','tools/run_reset_resolution.py','tools/make_video_reset_model.py']
    report={'date':'2026-11-25','scope':'80 reset/PG releases per binary policy, including external recovery aperture; no metastability-duration or MTBF guarantee',
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+[base.relative_to(ROOT).as_posix()]],
      'runs':[],'failures':[],'analog_metastability_approved':False}
    def save():(OUT/'reset-resolution.json').write_text(json.dumps(report,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='isa1-reset-resolution-') as tmp:
        work=Path(tmp)
        for policy in (0,1):
            cmd=['iverilog','-g2012','-Wall','-s','tb_reset_resolution',f'-Ptb_reset_resolution.RESOLVE_LATE={policy}',
              '-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names[:3]]]
            row={'resolution_late':policy,'compile':run(cmd,work)}
            if not row['compile']['exit']:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=90)
            row['passed']=row['compile']['exit']==0 and row.get('execution',{}).get('exit')==0 and 'reset_cuts=80 captured_pixels=2560' in row['execution']['stdout']
            report['runs'].append(row)
            if not row['passed']:report['failures'].append(policy)
            save();print(json.dumps(row),flush=True)
    return int(bool(report['failures']))


if __name__=='__main__':raise SystemExit(main())
