"""Record structural evidence without publishing mutable NET27 outputs."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from audit_pending_timed_run import audit

ROOT=Path(__file__).resolve().parents[1]
BASE='e7d0f1bbe872c1927f6684ece5c118c6e3631e4b'
OUT=ROOT/'verification/net29'
PENDING='verification/net27/full-timed/attempt-001/'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)

def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE
    graph=json.loads((OUT/'system-pin-loads.json').read_text())
    checks=json.loads((OUT/'reader-checks.json').read_text())
    for report in [graph,checks]:
        for row in report['sources']:assert digest(ROOT/row['path'])==row['sha256'],row['path']
    assert graph['connected_pins']==7810 and graph['maximum_input_count']==6
    assert len(graph['nets_above_four_inputs'])==4 and not graph['production_released']
    assert checks['passed'] and len(checks['negative'])==4 and all(r['passed'] for r in checks['negative'])
    frozen=audit();(OUT/'pending-run-integrity.json').write_text(json.dumps(frozen,indent=2)+'\n',newline='\n')
    allowed={'.gitattributes','README.md','AGENTS.md','DECISIONS.md','PROVENANCE.md','ROADMAP.md','CHANGELOG.md',
        'docs/engineering/NET29_LOADS.md','docs/engineering/VALIDATION_STATUS.md',
        'tools/audit_system_pin_loads.py','tools/check_system_pin_load_audit.py','tools/record_net29_manifest.py'}
    names=[];pending=[]
    for row in git('status','--porcelain=v1','-z','--untracked-files=all').split(b'\0'):
        if not row:continue
        assert row[:2] not in (b'R ',b' R',b'C ',b' C')
        name=row[3:].decode()
        if name.startswith(PENDING):pending.append(name);continue
        assert name in allowed or name.startswith('verification/net29/'),name
        if name!='verification/net29/manifest.json':names.append(name)
    assert pending
    report={'date':'2026-11-26','base_git_commit':BASE,'scope':'Structural load audit only; no circuit change, electrical or full timed program approval.',
        'commands':['python tools/audit_system_pin_loads.py','python tools/check_system_pin_load_audit.py',
            'python tools/record_net29_manifest.py','python tools/stage_with_pending_timed_run.py verification/net29/manifest.json'],
        'python':platform.python_version(),'git':git('--version').decode().strip(),
        'connected_pins':7810,'signals_above_four_inputs':4,'reader_negative_cases':4,'pending_inputs_unchanged':True,
        'excluded_pending_run_prefix':PENDING,'excluded_files_at_snapshot':pending,
        'files':[{'path':n,'bytes':(ROOT/n).stat().st_size,'sha256':digest(ROOT/n)} for n in sorted(names)],
        'production_released':False}
    (OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    print(json.dumps({'files':len(names),'negative_reader_checks':4,'pending_inputs_unchanged':True}))

if __name__=='__main__':main()
