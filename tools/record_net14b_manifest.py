"""Audit native video results and fifteen preserved historical snapshots."""
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
import record_net14a_manifest as prior

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net14b'
BASE='ea529d0b7acac89abbbf07b42632f93006fd63af';MANIFEST=OUT/'manifest.json'


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


# Same batched Git-blob verification, starting from the NET-14A snapshot.
exec(inspect.getsource(prior.audit_history).replace('verification/net13/','verification/net14a/'),globals())


def main():
    failures=[]
    result=json.loads((OUT/'results.json').read_text());checks=json.loads((OUT/'checks.json').read_text());erc=json.loads((OUT/'erc-summary.json').read_text())
    for report in (result,checks):
        failures+=report['failures']
        for x in report['sources']:
            if digest(ROOT/x['path'])!=x['sha256']:failures.append('Changed tested source '+x['path'])
        if not all(x['passed'] for x in report['runs']):failures.append('Failed run')
    if len(result['runs'])!=3 or any('frames=2 samples=210000 visible=153600 hsync=25200 vsync=800 writes=2012 grant_starts=32' not in r['execution']['stdout'] for r in result['runs']):failures.append('Frame coverage')
    if len(checks['runs'])!=1 or 'reset_cuts=16 captured_pixels=512' not in checks['runs'][0]['execution']['stdout']:failures.append('Reset coverage')
    if len(checks['negative'])!=4 or not all(x['passed'] for x in checks['negative']):failures.append('Negative calibration')
    graph=json.loads((OUT/'schematic-check.json').read_text())
    if graph['failures'] or graph['ics']!=35 or graph['pins']!=582 or graph['max_signal_input_loads']>4:failures.append('Pin graph')
    if erc['erc_passed'] or erc['board_release'] or erc['exit']!=5:failures.append('Partial ERC scope changed')
    for x in erc['sources']:
        if digest(ROOT/x['path'])!=x['sha256']:failures.append('Changed ERC source '+x['path'])
    for name,key in [('references/video-raster-2026-11-25.json','files'),('verification/net14b/origin.json','files')]:
        for x in json.loads((ROOT/name).read_text())[key]:
            if digest(ROOT/x['path'])!=x['sha256']:failures.append('Changed provenance '+x['path'])
    if '--check' in sys.argv:
        manifest=json.loads(MANIFEST.read_text())
        for x in manifest['files']:
            p=(ROOT/x['path']).resolve()
            if not p.is_relative_to(ROOT) or not p.is_file() or digest(p)!=x['sha256']:failures.append(x['path'])
        print(json.dumps({'checked':len(manifest['files']),'failures':failures,'production_released':False}));return int(bool(failures))
    if failures:print(json.dumps({'failures':failures}));return 1
    failures+=audit_history()
    if failures:print(json.dumps({'failures':failures}));return 1
    names=['README.md','ROADMAP.md','DECISIONS.md','PROVENANCE.md','CHANGELOG.md','AGENTS.md',
      'docs/engineering/NET14B.md','docs/engineering/VALIDATION_STATUS.md',
      'tools/build_video_raster.py','tools/run_video_raster.py','tools/run_video_raster_checks.py','tools/check_video_raster_erc.py','tools/record_net14b_manifest.py',
      'references/video-raster-2026-11-25.json','references/ti/sn74ahc74.pdf','references/ti/sn74lv161a.pdf','references/ti/sn74ahc574.pdf','references/ti/sn74ahct574.pdf']
    files={ROOT/n for n in names}
    for folder in ('hardware/video_raster','sim/net14b','verification/net14b'):
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and p!=MANIFEST and p.suffix!='.kicad_prl')
    data={'iteration':'NET-14B','date':'2026-11-25','base_git_commit':BASE,
      'scope':'Native partial raster/clock/capture plus selected component scenarios, not full CPU integration/PVT/physical approval',
      'files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p),
        'origin':'New NET-14B work or identified original manufacturer PDF; development preserves failed intermediate evidence'} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'recorded':len(files),'historical_snapshots':15,'failures':failures,'production_released':False}));return 0


if __name__=='__main__':raise SystemExit(main())
