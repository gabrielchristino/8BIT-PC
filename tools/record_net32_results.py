"""Audit standalone NET32 evidence and preserve two pending full-program runs."""
import collections
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from record_net31_review import pending_integrity

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net32'
BASE='793d391819712b85bae46fd2d6e9f9d9092b21c7'
PENDING=('verification/net27/full-timed/attempt-001/','verification/net30/full-timed/attempt-001/')
DOCS={'.gitattributes','AGENTS.md','README.md','PROVENANCE.md','DECISIONS.md','ROADMAP.md',
      'CHANGELOG.md','docs/engineering/VALIDATION_STATUS.md','docs/engineering/NET32_DAC_LEAF.md','references/net32-review.json'}
TOOLS={'tools/build_dac_leaf.py','tools/check_dac_leaf.py','tools/record_net32_results.py','tools/stage_net32_results.py'}

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n',newline='\n')

def graph(path):
    root=ET.parse(path).getroot()
    parts=sorted((c.get('ref'),c.findtext('value'),json.dumps(c.find('libsource').attrib,sort_keys=True)) for c in root.findall('./components/comp'))
    nets=sorted((n.get('name'),sorted((p.get('ref'),p.get('pin')) for p in n.findall('node'))) for n in root.findall('./nets/net'))
    return {'parts':parts,'nets':nets}

def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE
    resolved=[];records=0
    def sources(report,aliases=None):
        nonlocal records
        for row in report.get('sources',[]):
            path=row['path'];source=ROOT/path
            if digest(source)!=row['sha256']:
                assert aliases and path in aliases,path
                source=ROOT/aliases[path];assert digest(source)==row['sha256'],path
                resolved.append({'path':path,'sha256':row['sha256'],'preserved_source':source.relative_to(ROOT).as_posix()})
            records+=1
    leaf=json.loads((OUT/'leaf-results.json').read_text());sources(leaf)
    assert not leaf['failures'] and len(leaf['pin_negatives'])==8 and all(r['rejected'] for r in leaf['pin_negatives'])
    assert leaf['digital']['compile']['exit']==0 and leaf['digital']['execution']['exit']==0
    assert 'distinct_codes_each_channel=1024 analog_model=0 failures=0' in leaf['digital']['execution']['stdout']
    assert leaf['dc_arithmetic']['conditional_voltage_evaluations']==12288
    assert leaf['dc_arithmetic']['no_passive_single_shunt_solution']
    assert len(leaf['spice_kcl_proxy'])==3
    for row in leaf['spice_kcl_proxy']:
        job=json.loads((ROOT/row['execution']).read_text())
        assert job['exit']==0 and not job['wall_timeout'] and row['samples']==1024
    native=json.loads((OUT/'native/schematic-check.json').read_text());sources(native)
    assert native['components']==24 and native['pins']==126 and native['no_connects']==15
    assert native['erc_unwaived_count']==65 and not native['erc_approved'] and not native['footprints_assigned']
    commands=json.loads((OUT/'native/commands.json').read_text())
    assert len(commands)==5 and all(j['exit']==0 and not j['wall_timeout'] for j in commands.values())
    erc=json.loads((OUT/'native/erc.json').read_text())
    categories=dict(collections.Counter(v['type'] for s in erc['sheets'] for v in s['violations']))
    assert categories=={'pin_not_driven':31,'power_pin_not_driven':2,'pin_to_pin':2,'isolated_pin_label':30}
    current=OUT/'native/vga_dac_experiment.xml'
    initial=OUT/'development/initial-native/native/vga_dac_experiment.xml'
    assert graph(current)==graph(initial)
    for folder,files in [('initial-native',['native/schematic-check.json']),
                         ('first-leaf-check',['native/schematic-check.json','leaf-results.json'])]:
        base=OUT/'development'/folder
        aliases={'tools/build_dac_leaf.py':(base/'build_dac_leaf.py').relative_to(ROOT).as_posix(),
                 'tools/check_dac_leaf.py':(base/'check_dac_leaf.py').relative_to(ROOT).as_posix(),
                 'verification/net32/native/vga_dac_experiment.xml':(base/'native/vga_dac_experiment.xml').relative_to(ROOT).as_posix()}
        for file in files:sources(json.loads((base/file).read_text()),aliases)
    assert not git('diff','--name-only',BASE,'--','archive','revisions','hardware/load_distributed_video','sim/net30')
    pending=[pending_integrity(prefix) for prefix in PENDING]
    write(OUT/'pending-integrity.json',pending)
    audit={'date':'2026-11-27','base_git_commit':BASE,'source_records_checked':records,
        'historical_source_resolutions':resolved,'initial_and_final_electrical_graph_equal':True,
        'erc_unwaived':categories,'erc_approved':False,'production_released':False,
        'native_leaf_integrated_into_net30':False,'original_adi_pdf_available':False,
        'visual_review':'Exported preview inspected: three channels, all NC markers and passive groups visible; diagnostic/not-production title present.'}
    write(OUT/'result-audit.json',audit)
    names=[];excluded=[]
    for row in git('status','--porcelain=v1','-z','--untracked-files=all').split(b'\0'):
        if not row:continue
        assert row[:2] not in (b'R ',b' R',b'C ',b' C')
        name=row[3:].decode()
        if name.startswith(PENDING):excluded.append(name);continue
        assert name in DOCS or name in TOOLS or name.startswith(('hardware/vga_dac_experiment/','sim/net32/','verification/net32/')),name
        if name!='verification/net32/manifest.json':names.append(name)
    manifest={**audit,'scope':'Standalone experimental native DAC leaf, selected digital latch projection and ideal KCL proxy; not integrated VGA or production',
        'commands':['python3 tools/build_dac_leaf.py','python3 tools/check_dac_leaf.py','python tools/record_net32_results.py','python tools/stage_net32_results.py verification/net32/manifest.json'],
        'excluded_pending_run_prefix':PENDING,'excluded_files_at_snapshot':excluded,
        'files':[{'path':n,'bytes':(ROOT/n).stat().st_size,'sha256':digest(ROOT/n)} for n in sorted(names)]}
    write(OUT/'manifest.json',manifest)
    print(json.dumps({'manifest_files':len(names),'source_records_checked':records,'historical_source_resolutions':len(resolved),'pending_runs_preserved':len(pending),'production_released':False}))

if __name__=='__main__':main()
