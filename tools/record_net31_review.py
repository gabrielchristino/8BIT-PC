"""Audit a separate feasibility study while two immutable timed runs continue."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE='4b74c8c6681d43bc0329e29ce4ab93f5ab4787f6'
PENDING=('verification/net27/full-timed/attempt-001/','verification/net30/full-timed/attempt-001/')
DOCS={'.gitattributes','README.md','AGENTS.md','PROVENANCE.md','DECISIONS.md',
      'ROADMAP.md','CHANGELOG.md','docs/engineering/VALIDATION_STATUS.md','docs/engineering/NET31_DAC.md'}
TOOLS={'tools/collect_dac_sources.py','tools/collect_dac_supplement.py',
       'tools/check_dac_contract.py','tools/run_dac_packet_contract.py',
       'tools/record_net31_review.py','tools/stage_net31_review.py'}

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n',newline='\n')

def pending_integrity(prefix):
    attempt=ROOT/prefix
    origin=json.loads((attempt/'run-origin.json').read_text())
    rows=json.loads((attempt/'compiler-inputs.json').read_text())
    checked=[]
    for row in origin['sources']:
        assert digest(ROOT/row['path'])==row['sha256'],row
        checked.append(row['path'])
    for row in rows:
        assert digest(ROOT/row['snapshot'])==row['sha256'],row
        source=row['original'];root_prefix='/mnt/c/Users/gabri/projetos/isa1/'
        if source.startswith(root_prefix):
            relative=source[len(root_prefix):]
            assert digest(ROOT/relative)==row['sha256'],relative
            checked.append(relative)
    state=json.loads((attempt/'run-state.json').read_text())
    assert state['status']=='running' and not state['simulation_passed']
    assert (attempt/'simulation.stderr.log').read_bytes()==b''
    log=(attempt/'simulation.stdout.log').read_text().splitlines()
    return {'prefix':prefix,'scope':'Read-only checkpoint, not final approval',
            'origin':origin,'state_at_read':state,'snapshot_count':len(rows),
            'source_paths_checked':checked,'snapshot_hashes_match':True,
            'last_progress_at_read':log[-1] if log else None,'simulation_passed':False}

def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE
    out=ROOT/'verification/net31';out.mkdir(parents=True,exist_ok=True)
    checked=0
    for name in ['contract-results.json','packet-results.json']:
        report=json.loads((out/name).read_text());assert not report['failures']
        for source in report['sources']:
            assert digest(ROOT/source['path'])==source['sha256'];checked+=1
        if name=='contract-results.json':
            assert len(report['all_256_rgb332_codes'])==256 and len(report['calibration_corners'])==16
            assert len(report['negative_checks'])==5 and all(report['negative_checks'].values())
        else:
            assert len(report['runs'])==5
            for run in report['runs']:
                assert run['passed'] and run['compile']['exit']==0
                assert not run['execution']['wall_timeout'] and not run['execution']['stderr']
                assert run['expected_marker'] in run['execution']['stdout']
                assert (run['execution']['exit']!=0)==(run['negative']!=0)
    captured=json.loads((ROOT/'references/net31/sources.json').read_text())
    assert digest(ROOT/'tools/collect_dac_sources.py')==captured['tool_sha256']
    successful=[row for row in captured['rows'] if row['downloaded']]
    assert len(successful)==6
    for row in successful:
        assert digest(ROOT/row['file'])==row['sha256']
        assert digest(ROOT/row['extraction'])==row['extraction_sha256']
        assert row['extraction_exit']==0
    supplement=json.loads((ROOT/'references/net31/supplement.json').read_text())
    assert digest(ROOT/'tools/collect_dac_supplement.py')==supplement['tool_sha256']
    assert len(supplement['rows'])==3 and all(not row['downloaded'] and row['error'] for row in supplement['rows'])
    assert not (ROOT/'references/net31/ad9760.pdf').exists()
    assert not git('diff','--name-only',BASE,'--','archive','revisions','hardware','sim/net30')
    pending=[pending_integrity(prefix) for prefix in PENDING]
    write(out/'pending-integrity.json',pending)
    audit={'date':'2026-11-27','base_git_commit':BASE,'python':platform.python_version(),
           'validated_source_records':checked,'downloaded_primary_pdfs':6,
           'local_download_failures':4,'original_ad9760_pdf_available':False,
           'contract_arithmetic_passed':True,'functional_packet_proposal_passed':True,
           'native_dac_circuit_built':False,'bom_adopted':False,'production_released':False}
    write(out/'review-audit.json',audit)
    names=[];excluded=[]
    for row in git('status','--porcelain=v1','-z','--untracked-files=all').split(b'\0'):
        if not row:continue
        assert row[:2] not in (b'R ',b' R',b'C ',b' C')
        name=row[3:].decode()
        if name.startswith(PENDING):excluded.append(name);continue
        assert name in DOCS or name in TOOLS or name.startswith(('engineering/net31/','references/net31/','sim/net31/','verification/net31/')),name
        if name!='verification/net31/manifest.json':names.append(name)
    assert excluded
    manifest={**audit,'scope':'Candidate VGA DAC review and separate functional proposal; no native/global/analog approval',
        'commands':['python3 tools/check_dac_contract.py','python3 tools/run_dac_packet_contract.py',
                    'python tools/record_net31_review.py','python tools/stage_net31_review.py verification/net31/manifest.json'],
        'excluded_pending_run_prefix':PENDING,'excluded_files_at_snapshot':excluded,
        'files':[{'path':name,'bytes':(ROOT/name).stat().st_size,'sha256':digest(ROOT/name)} for name in sorted(names)]}
    write(out/'manifest.json',manifest)
    print(json.dumps({'files':len(names),'source_records_verified':checked,'pending_runs':len(pending),**audit}))

if __name__=='__main__':main()
