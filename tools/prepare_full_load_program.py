"""Prepare independent complete timed boot for the four-buffer candidate."""
import hashlib
import json
from pathlib import Path
from run_request_skew_probe import once

ROOT=Path(__file__).resolve().parents[1]

def main():
    source=ROOT/'tools/run_full_timed_program.py';text=source.read_text()
    for old,new in [
        ('import run_local_phase_program as template','import run_distributed_load_program as template'),
        ("CIRCUIT_BASE='f1c6c27d60d921286ed8729cd6f47e90e5948a3b'","CIRCUIT_BASE='16a82e4866ac9c791dfae0e162c2f887842b1f52'"),
        ("OUT=ROOT/'verification/net27/full-timed'","OUT=ROOT/'verification/net30/full-timed'"),
        ("folder = ROOT / 'verification/net26/program'","folder = ROOT / 'verification/net30/program'")]:text=once(text,old,new)
    text=text.replace('tools/run_local_phase_program.py','tools/run_distributed_load_program.py').replace('tools/run_full_timed_program.py','tools/run_full_load_program.py')
    text=text.replace('Run the complete NET26 program','Run the complete NET30 candidate program')
    text=once(text,"'date_started':'2026-11-26'","'date_started':'2026-11-27'")
    target=ROOT/'tools/run_full_load_program.py'
    previous=None
    if target.exists():
        previous=json.loads((ROOT/'verification/net30/full-program-preparation.json').read_text())
        assert hashlib.sha256(target.read_bytes()).hexdigest()==previous['result_sha256']
        assert not (ROOT/'verification/net30/full-timed').exists(),'Never overwrite a launched runner'
    target.write_text('# GENERATED separate NET30 complete timed candidate; ancestors unchanged.\n'+text)
    report={'date':'2026-11-27','scope':'Preparation only. Separate full timed NET30 run, no result claimed; keep NET27 running independently.',
        'parent':source.relative_to(ROOT).as_posix(),'parent_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'result':target.relative_to(ROOT).as_posix(),'result_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'circuit_commit':'16a82e4866ac9c791dfae0e162c2f887842b1f52','previous_unlaunched_preparation':previous,
        'transformation':'Use NET30 program template, candidate circuit commit and separate output folder. Same nominal clocks/startup, unknown SRAM, original assertions, progress, snapshots and process limits.'}
    (ROOT/'verification/net30/full-program-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'prepared':report['result'],'simulation_passed':False}))

if __name__=='__main__':main()
