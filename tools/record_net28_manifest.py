"""Audit documentary power evidence and publish independently of live HDL logs."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from audit_pending_timed_run import audit

ROOT=Path(__file__).resolve().parents[1]
BASE='ba3353f585fff94469d89674a8c1bdfa08ea70f1'
OUT=ROOT/'verification/net28'
PENDING='verification/net27/full-timed/attempt-001/'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)

def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE
    extracts=json.loads((OUT/'power-evidence/extractions.json').read_text())
    ledger=json.loads((OUT/'power-allowances.json').read_text())
    assert len(extracts['rows'])==34 and len(ledger['rows'])==34
    for row in extracts['rows']:
        assert digest(ROOT/row['pdf'])==row['pdf_sha256']
        assert digest(ROOT/row['extraction'])==row['extraction_sha256']
        assert row['exit']==0
    for row in ledger['sources']:assert digest(ROOT/row['path'])==row['sha256']
    assert ledger['board_current_upper_bound_a'] is None and ledger['dynamic_current_upper_bound_a'] is None
    assert sum(row['count'] for row in ledger['rows'])==462
    assert ledger['mixed_condition_reference_sum_ma']=='473.516'
    checkpoint=audit()
    (OUT/'pending-run-integrity.json').write_text(json.dumps(checkpoint,indent=2)+'\n',newline='\n')
    allowed={'.gitattributes','AGENTS.md','CHANGELOG.md','DECISIONS.md','PROVENANCE.md','README.md','ROADMAP.md',
        'docs/engineering/VALIDATION_STATUS.md','docs/engineering/NET28_POWER.md',
        'tools/extract_power_evidence.py','tools/record_power_allowances.py','tools/audit_pending_timed_run.py',
        'tools/stage_with_pending_timed_run.py','tools/record_net28_manifest.py'}
    names=[];pending=[]
    for row in git('status','--porcelain=v1','-z','--untracked-files=all').split(b'\0'):
        if not row:continue
        assert row[:2] not in (b'R ',b' R',b'C ',b' C')
        name=row[3:].decode()
        if name.startswith(PENDING):pending.append(name);continue
        assert name in allowed or name.startswith('verification/net28/'),name
        if name!='verification/net28/manifest.json':names.append(name)
    assert pending
    report={'date':'2026-11-26','base_git_commit':BASE,
        'scope':'NET28 documentary current ledger and reconciled current status only; pending NET27 outputs deliberately unpublished.',
        'verification':{'datasheet_families':34,'candidate_ics':460,'configured_oscillators':2,'pdf_and_extraction_hashes_match':True,
            'pending_compiler_snapshots_checked':checkpoint['snapshot_count'],'pending_input_hashes_match':True,
            'power_budget_closed':False,'new_circuit_simulation_pass_claimed':False},
        'commands':['WSL Ubuntu: python3 tools/extract_power_evidence.py','WSL Ubuntu: python3 tools/record_power_allowances.py',
            'Windows: python tools/record_net28_manifest.py','Windows: python tools/stage_with_pending_timed_run.py verification/net28/manifest.json'],
        'manifest_python':platform.python_version(),'git_version':git('--version').decode().strip(),
        'excluded_pending_run_prefix':PENDING,'excluded_files_at_snapshot':pending,
        'files':[{'path':name,'bytes':(ROOT/name).stat().st_size,'sha256':digest(ROOT/name)} for name in sorted(names)],
        'production_released':False}
    (OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    print(json.dumps({'files':len(names),'excluded_pending':len(pending),'families':34,'integrity_verified':True,'power_budget_closed':False}))

if __name__=='__main__':main()
