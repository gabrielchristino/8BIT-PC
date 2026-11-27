"""Audit NET34 qualified-state evidence without certifying power transients."""
import hashlib
import json
from pathlib import Path
import subprocess
from record_net31_review import pending_integrity

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net34'
BASE='8aa26ed00ec94f87f3f21fa8cd93f4b1abf1e14b'
PENDING=('verification/net27/full-timed/attempt-001/','verification/net30/full-timed/attempt-001/')
DOCS={'.gitattributes','README.md','AGENTS.md','PROVENANCE.md','DECISIONS.md','ROADMAP.md','CHANGELOG.md',
      'docs/engineering/VALIDATION_STATUS.md','docs/engineering/NET34_SYNC.md'}
TOOLS={'tools/collect_sync_sources.py','tools/collect_sync_regulator.py','tools/build_vga_sync.py',
       'tools/run_sync_checks.py','tools/check_sync_electrical.py','tools/record_net34_results.py','tools/stage_net34_results.py'}

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',newline='\n')

def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE
    count=0;resolved=[]
    def sources(report,old=False):
        nonlocal count
        for row in report.get('sources',[]):
            name=row['path'];path=ROOT/name
            if digest(path)!=row['sha256']:
                assert old and name=='tools/check_sync_electrical.py',name
                path=OUT/'development/receiver-profile/check_sync_electrical.py'
                assert digest(path)==row['sha256'];resolved.append({'path':name,'sha256':row['sha256'],'preserved_source':path.relative_to(ROOT).as_posix()})
            count+=1
    native=json.loads((OUT/'native/native-results.json').read_text());sources(native)
    assert not native['failures'] and native['components']==17 and native['pins']==50 and native['ics']==4
    assert native['erc_unwaived']=={'power_pin_not_driven':2,'isolated_pin_label':2} and not native['erc_approved']
    jobs=json.loads((OUT/'native/commands.json').read_text());assert len(jobs)==4
    assert all(j['exit']==0 and not j['wall_timeout'] for j in jobs.values())
    functional=json.loads((OUT/'sync-results.json').read_text());sources(functional)
    assert not functional['failures'] and len(functional['runs'])==5
    for row in functional['runs']:
        assert row['passed'] and row['compile']['exit']==0 and not row['compile']['stderr']
        result=row['execution'];assert not result['wall_timeout'] and not result['stderr']
        assert row['expected_marker'] in result['stdout']
        assert (result['exit']!=0)==bool(row['negative'])
        if row['kind']=='states' and not row['negative']:assert 'sync_state_checks=14' in result['stdout']
    electrical=json.loads((OUT/'electrical-results.json').read_text());sources(electrical)
    assert not electrical['failures'] and not electrical['ramp_transient_esd_qualified']
    assert len(electrical['arithmetic']['dc_corners'])==32 and all(electrical['arithmetic']['rejected_shortcuts'].values())
    assert len(electrical['pin_negatives'])==8 and all(r['rejected'] for r in electrical['pin_negatives'])
    assert len(electrical['rc_proxy'])==3
    for row in electrical['rc_proxy']:
        job=json.loads((OUT/'rc-proxy'/str(row['load_pf'])/'execution.json').read_text())
        assert job['exit']==0 and not job['wall_timeout']
    sources(json.loads((OUT/'development/receiver-profile/electrical-results.json').read_text()),True)
    for ledger,tool in [('sources.json','tools/collect_sync_sources.py'),('regulator-source.json','tools/collect_sync_regulator.py')]:
        capture=json.loads((ROOT/'references/net34'/ledger).read_text())
        assert digest(ROOT/tool)==capture['tool_sha256']
        for row in capture['rows']:
            assert row['downloaded'] and row['extraction_exit']==0
            assert digest(ROOT/row['path'])==row['sha256'] and digest(ROOT/row['extraction'])==row['extraction_sha256']
    assert not git('diff','--name-only',BASE,'--','archive','revisions','hardware/dac_packet_video','hardware/vga_dac_rgb332','sim/net30','sim/net33')
    save(OUT/'pending-integrity.json',[pending_integrity(p) for p in PENDING])
    versions={}
    for name,command in [('python',['python3','--version']),('iverilog',['iverilog','-V']),('ngspice',['ngspice','--version']),
                         ('pdftotext',['pdftotext','-v']),('kicad',['/home/gabri/.local/opt/isa1-kicad-10.0.8/squashfs-root/usr/bin/kicad-cli','version'])]:
        cmd=['wsl','-d','Ubuntu','--',*command];result=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        assert result.returncode==0
        versions[name]={'command':cmd,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    audit={'date':'2026-11-27','base_git_commit':BASE,'source_records_checked':count,'historical_source_resolutions':resolved,
        'versions':versions,'native_pin_values_checked':True,'qualified_state_scenarios':2,'state_checks_each':14,
        'native_frame_scenarios':2,'reset_epochs_each':2,'samples_each':210000,'colors_each':256,
        'functional_negative':1,'pin_negatives':8,'conditional_dc_corners':32,'rc_proxy_cases':3,
        'rejected_receiver_profile_preserved':True,'visual_review':'All four packages, passive groups and intentional EN/CT no-connects visible in exported A3 preview.',
        'analog_regulator_supervisor_ramp_qualified':False,'universal_monitor_compatibility':False,'erc_approved':False,'production_released':False}
    save(OUT/'result-audit.json',audit)
    names=[];excluded=[]
    for row in git('status','--porcelain=v1','-z','--untracked-files=all').split(b'\0'):
        if not row:continue
        assert row[:2] not in (b'R ',b' R',b'C ',b' C')
        name=row[3:].decode()
        if name.startswith(PENDING):excluded.append(name);continue
        assert name in DOCS or name in TOOLS or name.startswith(('hardware/vga_sync_3v3/','sim/net34/','verification/net34/','references/net34/')),name
        if name!='verification/net34/manifest.json':names.append(name)
    manifest={**audit,'scope':'Experimental supervised sync stage; qualified functional states, conditional DC and ideal RC. No analog power/ESD/manufacturing approval.',
        'excluded_pending_run_prefix':PENDING,'excluded_files_at_snapshot':excluded,
        'commands':['python3 tools/build_vga_sync.py','python3 tools/run_sync_checks.py','python3 tools/check_sync_electrical.py',
                    'python tools/record_net34_results.py','python tools/stage_net34_results.py verification/net34/manifest.json'],
        'files':[{'path':n,'bytes':(ROOT/n).stat().st_size,'sha256':digest(ROOT/n)} for n in sorted(names)]}
    save(OUT/'manifest.json',manifest)
    print(json.dumps({'files':len(names),'source_records_verified':count,'historical_sources_resolved':len(resolved),'pending_runs':2,'power_transients_qualified':False,'production_released':False}))

if __name__=='__main__':main()
