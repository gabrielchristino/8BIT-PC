"""Audit CPU/video integration, incomplete runs and explicit reset assumptions."""
import hashlib
import inspect
import json
from pathlib import Path
import re
import subprocess
import sys
import record_net14a_manifest as original_auditor

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net14c'
BASE='6a83d5601ff42b7a970f7d180b405094f612ba09';MANIFEST=OUT/'manifest.json'


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


exec(inspect.getsource(original_auditor.audit_history).replace('verification/net13/','verification/net14b/'),globals())


def main():
    failures=[]
    def read(n):return json.loads((OUT/n).read_text())
    ideal=read('cpu/results-ideal.json');strict=read('cpu/results-timed.json');timed=read('cpu/results-timed-async.json')
    batches=read('timed-safety-batches.json');resolution=read('reset-resolution.json');clock=read('clock-cuts.json');native=read('native/results.json')
    for report in (ideal,strict,timed,batches,resolution,clock,native):
        for x in report['sources']:
            if digest(ROOT/x['path'])!=x['sha256']:failures.append('Changed tested source '+x['path'])
    if len(ideal['runs'])!=4 or ideal['quick'] or any(x['compile']['exit'] or x['execution']['exit'] or 'RESULT ' not in x['execution']['stdout'] for x in ideal['runs']):failures.append('Full ideal integration')
    if not ideal['runs'][-1].get('frame_matches_reference') or 'ram_aborts=0 vram_aborts=0 fixture_defaults=0' not in ideal['runs'][-1]['execution']['stdout']:failures.append('Unseeded SRAM/frame acceptance')
    if len(strict['runs'])!=1 or strict['runs'][0]['compile']['exit'] or strict['runs'][0]['execution']['exit']==0 or 'reset recovery violation' not in strict['runs'][0]['execution']['stdout']:failures.append('Strict async recovery rejection missing')
    if not timed['timed'] or not timed['quick'] or 'instruction_cases=1062 transactions=1821' not in timed['runs'][0]['execution']['stdout'] or timed['runs'][0]['execution']['exit']:failures.append('Delayed instruction acceptance')
    # The interrupted safety process returned zero, but has no RESULT and must
    # never count as a pass. Batches independently supply complete coverage.
    if len(timed['runs'])!=2 or 'RESULT ' in timed['runs'][1]['execution']['stdout']:failures.append('Interrupted-run classification changed')
    if batches['failures'] or batches['covered_opcode_indices']!=list(range(26)) or len(batches['runs'])!=7 or batches['reset_power_cases']!=1700:failures.append('Full batched delayed safety')
    for row in batches['runs']:
        match=re.search(r'reset_power_cases=(\d+) opcodes=26 failures=0',row['execution']['stdout'])
        if not row['passed'] or not match or int(match.group(1))!=row['reset_power_cases']:failures.append('Batched completion marker')
    for report in (resolution,clock,native):
        if report['failures'] or not all(r['passed'] for r in report['runs']):failures.append('Failed isolated scenario')
    if len(resolution['runs'])!=2 or any('reset_cuts=80 captured_pixels=2560' not in r['execution']['stdout'] for r in resolution['runs']):failures.append('Resolution policies/cut coverage')
    if len(clock['negative'])!=1 or not clock['negative'][0]['passed']:failures.append('Backend-clear negative calibration')
    if len(native['runs'])!=3:failures.append('Native frame configurations')
    graph=read('native/schematic-check.json');erc=read('native/erc-summary.json')
    if graph['failures'] or graph['ics']!=35 or graph['pins']!=582 or graph['max_signal_input_loads']>4:failures.append('Native pin graph')
    if erc['erc_passed'] or erc['board_release'] or erc['exit']!=5:failures.append('Partial ERC scope')
    for name in ('adapter-origin.json','reset-model-origin.json','native/check-origin.json'):
        for x in read(name)['files']:
            if digest(ROOT/x['path'])!=x['sha256']:failures.append('Changed provenance '+x['path'])
    for x in erc['sources']:
        if digest(ROOT/x['path'])!=x['sha256']:failures.append('Changed ERC source '+x['path'])
    old=json.loads((ROOT/'hardware/video_raster/design.json').read_text())['parts'];new=json.loads((ROOT/'hardware/video_system/design.json').read_text())['parts']
    changed=[{'reference':a['reference'],'pin':pin,'from':value,'to':b['nets'][pin]} for a,b in zip(old,new) for pin,value in a['nets'].items() if value!=b['nets'][pin]]
    declared=[{k:x[k] for k in ('reference','pin','from','to')} for x in read('native/changed-pin.json')]
    if len(old)!=len(new) or len(changed)!=1 or changed!=declared:failures.append('Single native pin change')
    if '--check' in sys.argv:
        m=json.loads(MANIFEST.read_text())
        for x in m['files']:
            p=(ROOT/x['path']).resolve()
            if not p.is_relative_to(ROOT) or not p.is_file() or digest(p)!=x['sha256']:failures.append(x['path'])
        print(json.dumps({'checked':len(m['files']),'failures':failures,'production_released':False}));return int(bool(failures))
    if failures:print(json.dumps({'failures':failures}));return 1
    failures+=audit_history()
    if failures:print(json.dumps({'failures':failures}));return 1
    acceptance={'date':'2026-11-25','ideal_complete':True,'delayed_instruction_cases':1062,'delayed_safety_cases':1700,'delayed_safety_opcode_indices':list(range(26)),
      'monolithic_delayed_safety':'INCOMPLETE: deliberately interrupted, no RESULT, never approved even though exit code zero',
      'strict_external_recovery':'EXPECTED REJECTION; remains a physical signoff gap',
      'bounded_external_reset_resolution':'Conditional digital assumption only; analog duration/MTBF not approved',
      'full_delayed_program_frame_executed':False,'production_released':False}
    (OUT/'acceptance.json').write_text(json.dumps(acceptance,indent=2)+'\n')
    names=['README.md','ROADMAP.md','DECISIONS.md','PROVENANCE.md','CHANGELOG.md','AGENTS.md','docs/engineering/NET14C.md','docs/engineering/VALIDATION_STATUS.md','docs/engineering/PRODUCTION_GATES.md',
      'tools/build_video_system.py','tools/make_video_cpu.py','tools/run_video_cpu.py','tools/make_video_reset_model.py','tools/run_video_cpu_async.py','tools/run_reset_resolution.py','tools/run_video_clock_cuts.py','tools/run_video_safety_batches.py','tools/prepare_video_system_checks.py','tools/run_video_system.py','tools/check_video_system_erc.py','tools/record_net14c_manifest.py']
    files={ROOT/n for n in names}
    for folder in ('hardware/video_system','sim/net14c','verification/net14c'):
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl' and '__pycache__' not in p.parts)
    data={'iteration':'NET-14C','date':'2026-11-25','base_git_commit':BASE,'scope':'Native CPU/video integration and explicit bounded reset assumptions, strict recovery gap preserved; not analog/PVT/MTBF/PCB approval',
      'files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p),'origin':'New NET-14C work or identified preserved intermediate evidence; not recovered historical originals'} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'recorded':len(files),'historical_snapshots':16,'failures':failures,'production_released':False}));return 0


if __name__=='__main__':raise SystemExit(main())
