"""Audit NET30 results with explicit historical source resolution for titles."""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import xml.etree.ElementTree as ET
from audit_pending_timed_run import audit

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net30'
BASE='16a82e4866ac9c791dfae0e162c2f887842b1f52'
PENDING='verification/net27/full-timed/attempt-001/'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args,**kwargs):return subprocess.check_output(['git',*args],cwd=ROOT,**kwargs)

def graph(p):
    root=ET.parse(p).getroot()
    parts=sorted((c.get('ref'),c.findtext('value'),c.findtext('footprint',''),json.dumps(c.find('libsource').attrib,sort_keys=True)) for c in root.findall('./components/comp'))
    nets=sorted((n.get('name'),sorted((p.get('ref'),p.get('pin')) for p in n.findall('node'))) for n in root.findall('./nets/net'))
    return json.dumps({'parts':parts,'nets':nets},sort_keys=True).encode()

def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE
    aliases={};resolved=[];count=0
    titles=json.loads((OUT/'title-update-final/report.json').read_text())
    assert len(titles['rows'])==3
    for row in titles['rows']:
        kind=row['kind'];name='load_distributed_'+kind
        sch='hardware/'+name+'/'+name+'.kicad_sch';xml='verification/net30/native/'+kind+'/'+name+'.xml'
        for path,snapshot in [(sch,row['original_schematic']),(xml,row['original_xml'])]:
            assert digest(ROOT/snapshot)==row['before_sha256'][path]
            assert hashlib.sha256(git('show',BASE+':'+path)).hexdigest()==row['before_sha256'][path]
            aliases[path]=snapshot
        for path,sha in row['after_sha256'].items():assert digest(ROOT/path)==sha,path
        assert graph(ROOT/xml)==graph(ROOT/row['original_xml'])
        assert hashlib.sha256(graph(ROOT/xml)).hexdigest()==row['pin_component_graph_sha256']
        for path,sha in row['before_sha256'].items():
            if path.endswith(('_netlist.sv','design.json')):assert digest(ROOT/path)==sha
    aliases.update({'sim/net30/tb_load_frames.sv':'verification/net30/development/frames-short-reset/tb_load_frames.sv',
        'tools/run_distributed_load_frames.py':'verification/net30/development/frames-short-reset/run_distributed_load_frames.py'})
    def hashed(rows,allow_historical=False):
        nonlocal count
        for row in rows:
            path=row['path'];current=ROOT/path
            if digest(current)!=row['sha256']:
                assert allow_historical and path in aliases,path
                snapshot=aliases[path];assert digest(ROOT/snapshot)==row['sha256'],path
                resolved.append({'path':path,'sha256':row['sha256'],'resolved_snapshot':snapshot})
            count+=1
    def read(name):
        report=json.loads((OUT/name).read_text());hashed(report.get('sources',[]),True)
        assert not report.get('failures'),name
        return report
    def complete(row,negative=False):
        assert row['passed'] and row['compile']['exit']==0 and not row['compile']['stderr']
        result=row['execution'];assert not result.get('wall_timeout')
        if negative:assert result['exit']!=0 and 'FATAL:' in result['stdout']
        else:assert result['exit']==0 and 'RESULT ' in result['stdout'] and 'failures=0' in result['stdout'] and not result['stderr']
    structural=read('system-pin-loads.json');assert structural['maximum_input_count']==4 and structural['connected_pins']==7814
    assert sum(map(len,structural['native_pin_deltas'].values()))==15
    hashed(titles['sources'])
    for kind in ['video','keyboard','bus']:
        read('native/'+kind+'/schematic-check.json')
        erc=json.loads((OUT/'native'/kind/'erc-summary.json').read_text());hashed(erc['sources'],True)
        assert not erc['erc_passed']
    hashed(json.loads((OUT/'adapter-origin.json').read_text())['files'])
    memory=read('memory-pin-results.json');assert len(memory['runs'])==4 and len(memory['negative'])==2
    for row in memory['runs']:complete(row);assert 'active_write_cuts=12 stopped_clocks=2 max_we_inhibit_ns=94.000' in row['execution']['stdout']
    for row in memory['negative']:complete(row,True)
    for filename,n in [('verified-cpu-ideal.json',6886),('verified-cpu-timed-quick.json',1062),('verified-cpu-early-timed-quick.json',1062)]:
        data=read('vectors/'+filename);assert len(data['runs'])==1
        complete(data['runs'][0]);assert 'instruction_cases='+str(n)+' ' in data['runs'][0]['execution']['stdout']
        if n==1062:assert 'observed_setup_ns=54.888/16.944/26.944' in data['runs'][0]['execution']['stdout']
    for filename in ['actual-cpu-write-reset.json','frequency-corners/actual-cpu-write-reset.json']:
        data=read(filename);assert len(data['runs'])==2
        for row in data['runs']:complete(row);assert 'actual_cpu_write_cuts=2 restarted_scans=2 max_we_inhibit_ns=84.000 fixture_defaults=0' in row['execution']['stdout']
        for row in data.get('compiled_corner_benches',[]):assert digest(ROOT/row['path'])==row['sha256']
    frames=read('native-frame-results.json');assert len(frames['runs'])==4
    for row in frames['runs']:
        complete(row)
        assert 'native_frames=2 samples=210000 visible=153600 hsync=25200 vsync=800 writes=2014 grant_starts=32' in row['execution']['stdout']
        assert 'seeded_vram=1 seeded_vb=1' in row['execution']['stdout']
    program=read('program/system-program-ideal.json');assert len(program['runs'])==1
    row=program['runs'][0];complete(row);assert row['frame_matches_reference']
    assert 'retirements=132197 transactions=232576 vram_transactions=32771 frame_pixels=76800' in row['execution']['stdout']
    assert 'ram_valid_writes=337 vram_valid_writes=32770 ram_aborts=0 vram_aborts=0 fixture_defaults=0' in row['execution']['stdout']
    # A failed exploratory fixture is preserved, not included among passes.
    failed=json.loads((OUT/'development/frames-short-reset/native-frame-results.json').read_text())
    assert failed['failures']==[[0,0]] and 'native frame watchdog' in failed['runs'][0]['execution']['stdout']
    diagnostic=json.loads((OUT/'development/frames-short-reset/diagnostic-result.json').read_text())
    assert diagnostic['compile']['exit']==0 and 'p0=x arm=x bank=x' in diagnostic['execution']['stdout'] and 'safe=x' in diagnostic['execution']['stdout']
    jobs=[]
    for path in sorted((OUT/'jobs').glob('*/run-state.json')):
        state=json.loads(path.read_text());assert state['status']=='process_finished',path
        assert state['exit']==(1 if path.parent.name=='frames' else 0)
        origin=json.loads((path.parent/'origin.json').read_text());hashed(origin['sources'],True)
        assert digest(Path(state['stdout_path'].replace('/mnt/c/Users/gabri/projetos/isa1/',str(ROOT)+'/')))==state['stdout_sha256']
        jobs.append({'job':path.parent.name,'exit':state['exit'],'seconds':state['seconds'],'source_superset_in_origin':True})
    assert len(jobs)==9
    prepared=json.loads((OUT/'full-program-preparation.json').read_text())
    assert digest(ROOT/prepared['parent'])==prepared['parent_sha256'] and digest(ROOT/prepared['result'])==prepared['result_sha256']
    assert digest(ROOT/'tools/prepare_full_load_program.py')==prepared['generator_sha256']
    previous=prepared.get('previous_unlaunched_preparation')
    if previous:
        reconstructed=(ROOT/prepared['result']).read_bytes().replace(b"'date_started':'2026-11-27'",b"'date_started':'2026-11-26'")
        assert hashlib.sha256(reconstructed).hexdigest()==previous['result_sha256']
    frozen=audit()
    result={'date':'2026-11-27','scope':'NET30 own selected digital regressions accepted for continued engineering; no full timed program, global electrical/STA/POR/MTBF or production pass.',
        'sources_records_checked':count,'historical_sources_resolved':resolved,'finished_jobs':jobs,
        'net27_read_only_integrity':frozen,'title_only_graph_equal':True,
        'completed':{'ideal_instruction_cases':6886,'timed_cases_each':1062,'timed_scenarios':2,'sram_cuts':48,'memory_negatives':2,
            'cpu_write_cuts_nominal_and_corners':8,'frame_scenarios':4,'frames_each':2,'boot_retirements':132197,'boot_pixels':76800,'boot_frame_equal':True,'boot_unseeded_sram':True},
        'development_failures_preserved':['Cold frame fixture with1us reset','First title-export attempt with missing ERC JSON; cause unknown'],
        'candidate_promoted_for_continued_engineering':True,'full_timed_program_net30_completed':False,'production_released':False}
    (OUT/'result-audit.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    names=[];pending=[]
    docs={'.gitattributes','README.md','AGENTS.md','PROVENANCE.md','DECISIONS.md','ROADMAP.md','CHANGELOG.md','docs/engineering/NET30.md','docs/engineering/VALIDATION_STATUS.md'}
    allowed_tools={'tools/prepare_full_load_program.py','tools/run_full_load_program.py','tools/update_load_drawing_titles.py','tools/record_net30_results.py'}
    for entry in git('status','--porcelain=v1','-z','--untracked-files=all').split(b'\0'):
        if not entry:continue
        assert entry[:2] not in (b'R ',b' R',b'C ',b' C')
        name=entry[3:].decode()
        if name.startswith(PENDING):pending.append(name);continue
        assert name in docs or name in allowed_tools or name.startswith(('verification/net30/','hardware/load_distributed_')),name
        if name!='verification/net30/manifest.json':names.append(name)
    assert pending
    manifest={'date':'2026-11-27','base_git_commit':BASE,'scope':result['scope'],'python':platform.python_version(),
        'commands':['python tools/record_net30_results.py','python tools/stage_with_pending_timed_run.py verification/net30/manifest.json'],
        'result_audit':'verification/net30/result-audit.json','excluded_pending_run_prefix':PENDING,'excluded_files_at_snapshot':pending,
        'files':[{'path':name,'bytes':(ROOT/name).stat().st_size,'sha256':digest(ROOT/name)} for name in sorted(names)],'production_released':False}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',newline='\n')
    print(json.dumps({'files':len(names),'source_records_checked':count,'historical_resolutions':len(resolved),'finished_jobs':len(jobs),'full_timed_program_accepted':False,'production_released':False}))

if __name__=='__main__':main()
