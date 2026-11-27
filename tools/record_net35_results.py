"""Audit NET35 conditional window evidence without certifying power transients."""
import hashlib
import json
from pathlib import Path
import subprocess
from record_net31_review import pending_integrity

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net35'
BASE='e2d466193a4f2e83e251ebb9c7ea985405907e9d'
PENDING=('verification/net27/full-timed/attempt-001/','verification/net30/full-timed/attempt-001/')
DOCS={'.gitattributes','README.md','AGENTS.md','PROVENANCE.md','DECISIONS.md','ROADMAP.md','CHANGELOG.md',
      'docs/LACUNAS.md','docs/engineering/VALIDATION_STATUS.md','docs/engineering/NET35_WINDOW.md'}
TOOLS={'tools/collect_window_sources.py','tools/build_sync_window.py','tools/check_sync_window.py',
       'tools/record_net35_results.py','tools/stage_net35_results.py'}

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',newline='\n')

def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE
    count=0
    def sources(report):
        nonlocal count
        for row in report.get('sources',[]):
            assert digest(ROOT/row['path'])==row['sha256'],row['path']
            count+=1
    native=json.loads((OUT/'native/native-results.json').read_text());sources(native)
    assert not native['failures'] and native['components']==22 and native['pins']==66 and native['ics']==4
    assert native['erc_unwaived']=={'power_pin_not_driven':2,'isolated_pin_label':2} and not native['erc_approved']
    assert not native['power_ramp_or_transients_qualified'] and not native['lt3042_original_local_pdf']
    jobs=json.loads((OUT/'native/commands.json').read_text());assert len(jobs)==4
    assert all(j['exit']==0 and not j['wall_timeout'] for j in jobs.values())
    report=json.loads((OUT/'window-results.json').read_text());sources(report)
    assert not report['failures'] and not report['physical_power_qualified'] and not report['new_full_frames_executed']
    a=report['arithmetic']
    assert len(a['conditional_discharge_corners'])==128
    assert min(r['voltage_at_disable_bound_v'] for r in a['conditional_discharge_corners'])==a['worst_voltage_at_disable_v']>3
    assert a['release_margin_mv']>0 and 3<=a['rail_min_max_v'][0]<a['rail_min_max_v'][1]<=3.6
    assert a['minimum_bleed_current_ma']>1
    assert len(report['qualified_state_runs'])==3
    assert sum(bool(r['negative']) for r in report['qualified_state_runs'])==1
    for row in report['qualified_state_runs']:
        assert row['passed'] and row['compile']['exit']==0 and not row['compile']['wall_timeout'] and not row['compile']['stderr']
        result=row['execution'];assert not result['wall_timeout'] and not result['stderr']
        assert row['expected_marker'] in result['stdout']
        assert (result['exit']!=0)==bool(row['negative'])
        if not row['negative']:assert 'sync_state_checks=14' in result['stdout']
    previous=(ROOT/'hardware/vga_sync_3v3/vga_sync_functional.sv').read_bytes()
    current=(ROOT/'hardware/vga_sync_window/sync_window_functional.sv').read_bytes()
    assert previous.replace(b'net34_sync',b'net35_sync')==current
    assert len(report['pin_negatives'])==8 and all(r['rejected'] for r in report['pin_negatives'])
    assert len(report['discharge_proxy'])==6 and sum(r['negative'] for r in report['discharge_proxy'])==2
    for row in report['discharge_proxy']:
        assert row['classified_as_expected'] and (row['voltage_v']<3)==row['negative']
        job=json.loads((OUT/'discharge-proxy'/str(row['case'])/'execution.json').read_text())
        assert job['exit']==0 and not job['wall_timeout']
    capture=json.loads((ROOT/'references/net35/sources.json').read_text())
    assert digest(ROOT/'tools/collect_window_sources.py')==capture['tool_sha256']
    assert digest(ROOT/'tools/collect_sync_sources.py')==capture['template_sha256']
    assert len(capture['rows'])==3 and sum(r['downloaded'] for r in capture['rows'])==2
    for row in capture['rows']:
        if row['downloaded']:
            assert row['extraction_exit']==0
            assert digest(ROOT/row['path'])==row['sha256'] and digest(ROOT/row['extraction'])==row['extraction_sha256']
        else:
            assert row['path']=='references/net35/lt3042.pdf' and row['error'] and not (ROOT/row['path']).exists()
    assert not git('diff','--name-only',BASE,'--','archive','revisions','hardware/vga_sync_3v3','hardware/dac_packet_video','hardware/vga_dac_rgb332','sim/net30','sim/net33','sim/net34')
    save(OUT/'pending-integrity.json',[pending_integrity(p) for p in PENDING])
    versions={}
    for name,command in [('python',['python3','--version']),('iverilog',['iverilog','-V']),('ngspice',['ngspice','--version']),
                         ('pdftotext',['pdftotext','-v']),('kicad',['/home/gabri/.local/opt/isa1-kicad-10.0.8/squashfs-root/usr/bin/kicad-cli','version'])]:
        cmd=['wsl','-d','Ubuntu','--',*command];result=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        assert result.returncode==0
        versions[name]={'command':cmd,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    audit={'date':'2026-11-27','base_git_commit':BASE,'source_records_checked':count,
        'versions':versions,'native_pin_values_checked':True,'qualified_state_scenarios':2,'state_checks_each':14,
        'new_full_frames_executed':False,'functional_model_equivalent_to_net34':True,
        'functional_negative':1,'pin_negatives':8,'conditional_discharge_corners':128,'passive_discharge_proxy_cases':6,
        'visual_review':'All four packages and 22 components visible without clipping in exported A3 preview; reviewed before publication.',
        'analog_regulator_supervisor_ramp_qualified':False,'universal_monitor_compatibility':False,'erc_approved':False,'production_released':False}
    save(OUT/'result-audit.json',audit)
    names=[];excluded=[]
    for row in git('status','--porcelain=v1','-z','--untracked-files=all').split(b'\0'):
        if not row:continue
        assert row[:2] not in (b'R ',b' R',b'C ',b' C')
        name=row[3:].decode()
        if name.startswith(PENDING):excluded.append(name);continue
        assert name in DOCS or name in TOOLS or name.startswith(('hardware/vga_sync_window/','verification/net35/','references/net35/')),name
        if name!='verification/net35/manifest.json':names.append(name)
    manifest={**audit,'scope':'Alternative supervised 3.51V sync window; qualified-state logic and conditional passive discharge only. No physical power/manufacturing approval.',
        'excluded_pending_run_prefix':PENDING,'excluded_files_at_snapshot':excluded,
        'commands':['python3 tools/build_sync_window.py','python3 tools/check_sync_window.py',
                    'python tools/record_net35_results.py','python tools/stage_net35_results.py verification/net35/manifest.json'],
        'files':[{'path':n,'bytes':(ROOT/n).stat().st_size,'sha256':digest(ROOT/n)} for n in sorted(names)]}
    save(OUT/'manifest.json',manifest)
    print(json.dumps({'files':len(names),'source_records_verified':count,'pending_runs':2,'power_transients_qualified':False,'production_released':False}))

if __name__=='__main__':main()
