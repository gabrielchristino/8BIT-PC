"""Prove the single native backend-clear pin change against pulse-width cuts."""
import hashlib
import json
from pathlib import Path
import re
import tempfile
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net14c'


def main():
    source=ROOT/'sim/net14c/tb_reset_resolution.sv';text=source.read_text()
    text=text.replace('tb_reset_resolution','tb_video_clock_cuts')
    text=text.replace('observe=0;@(negedge master);','observe=0;@(negedge backend);#k;')
    text=text.replace(' initial begin\n',' initial begin\n   reset_n=0;#1000;reset_n=1;#1000;\n',1)
    monitor=''' realtime backend_changed=-10000;
 always @(backend)begin
   if($realtime>5000 && $realtime-backend_changed<20)$fatal(1,"backend truncated pulse");
   backend_changed=$realtime;
 end
'''
    text=text.replace(' integer cuts=',monitor+' integer cuts=')
    bench=ROOT/'sim/net14c/tb_video_clock_cuts.sv';bench.write_text(text)
    model=ROOT/'sim/net14c/package_models_async.sv';native=ROOT/'sim/net14c/video_raster_async_netlist.sv'
    changed=json.loads((OUT/'native/changed-pin.json').read_text())[0]
    defs=json.loads((ROOT/'hardware/video_system/package-functions.json').read_text())['SN74AHC74']['pins']
    channel=int(defs[changed['pin']]['name'][3]);ref=changed['reference']+'_'+str(channel)
    original=native.read_text();bad=original.splitlines();found=False
    for i,line in enumerate(bad):
        if ') '+ref+'(' in line:
            start=line.index(') '+ref+'(')+len(') '+ref+'(');args=line[start:-2].split(',')
            assert args[1]=="1'b1";args[1]='n_'+changed['from'];bad[i]=line[:start]+','.join(args)+');';found=True
    assert found
    report={'date':'2026-11-25','scope':'Backend pulse width during 80 phase-swept reset/PG cuts; bounded external reset resolution, no analog/PVT approval',
      'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [source,model,native,bench,Path(__file__),OUT/'native/changed-pin.json']],
      'runs':[],'negative':[],'failures':[]}
    def save():(OUT/'clock-cuts.json').write_text(json.dumps(report,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='isa1-clock-cuts-') as tmp:
        work=Path(tmp);fault=work/'old-clear.sv';fault.write_text('\n'.join(bad)+'\n')
        for negative,graph in [(False,native),(True,fault)]:
            cmd=['iverilog','-g2012','-Wall','-s','tb_video_clock_cuts','-o',str(work/'test.vvp'),str(model),str(graph),str(bench)]
            row={'reverted_backend_clear':negative,'compile':run(cmd,work)}
            if not row['compile']['exit']:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=90)
            if negative:
                row['expected_rejection']=True
                row['passed']=row['compile']['exit']==0 and row.get('execution',{}).get('exit',0)!=0 and 'backend truncated pulse' in row['execution']['stdout']
                row['mutated_netlist_sha256']=hashlib.sha256(fault.read_bytes()).hexdigest();report['negative'].append(row)
            else:
                row['passed']=row['compile']['exit']==0 and row.get('execution',{}).get('exit')==0 and 'reset_cuts=80 captured_pixels=2560' in row['execution']['stdout']
                report['runs'].append(row)
            if not row['passed']:report['failures'].append(negative)
            save();print(json.dumps(row),flush=True)
    return int(bool(report['failures']))


if __name__=='__main__':raise SystemExit(main())
