"""Preserve failed frame fixture and inspect its cold-start forcepoint."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from limited_process import run_limited
from run_request_skew_probe import once

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net30/development/frames-short-reset'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for source in ['sim/net30/tb_load_frames.sv','tools/run_distributed_load_frames.py','verification/net30/native-frame-results.json']:
        target=OUT/Path(source).name
        assert not target.exists(),'Preserve prior diagnostic evidence'
        shutil.copyfile(ROOT/source,target)
    shutil.copytree(ROOT/'verification/net30/jobs/frames',OUT/'job')
    prior=json.loads((ROOT/'verification/net30/native-frame-results.json').read_text())
    assert prior['failures']==[[0,0]] and 'native frame watchdog' in prior['runs'][0]['execution']['stdout']
    text=(OUT/'tb_load_frames.sv').read_text()
    text=once(text,'#90000000;$fatal', '''#12000000;
   $display("STARTUP raw=%b rc=%b phase_init=%b warm_run=%b p0=%b arm=%b bank=%b cpu_reset=%b safe=%b",raw,memory.reset_domains.n_DELAY_RC,memory.phase_init_n,memory.raster.n_PHASE_RUN,memory.raster.n_P0,memory.bank_arm,memory.bank_reset_n,memory.cpu_reset_n,memory.safe);
   $fatal''')
    bench=OUT/'diagnostic.sv';bench.write_text(text)
    command=list(prior['runs'][0]['compile']['command'])
    assert command[-1].endswith('/tb_load_frames.sv')
    command[-1]=str(bench)
    with tempfile.TemporaryDirectory(prefix='isa1-frame-startup-') as tmp:
        work=Path(tmp);command[command.index('-o')+1]=str(work/'test.vvp')
        compile_result=run_limited(command,work,timeout=60,memory_mb=1024,cpu_seconds=45)
        execution=run_limited(['vvp',str(work/'test.vvp')],work,timeout=60,memory_mb=1024,cpu_seconds=45) if compile_result['exit']==0 else None
    report={'date':'2026-11-26','scope':'Diagnostic of failed new frame test only; no hardware correction/pass claimed.',
        'compile':compile_result,'execution':execution,'source_sha256':hashlib.sha256(bench.read_bytes()).hexdigest(),
        'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT/'diagnostic-result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()
