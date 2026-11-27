"""Audit native video/DAC evidence without touching pending CPU simulations."""
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from record_net31_review import pending_integrity

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net33'
BASE='052928f344e1fad6f6d43f380345793f60b748ff'
PENDING=('verification/net27/full-timed/attempt-001/','verification/net30/full-timed/attempt-001/')
DOCS={'.gitattributes','README.md','AGENTS.md','PROVENANCE.md','DECISIONS.md','ROADMAP.md','CHANGELOG.md',
      'docs/engineering/VALIDATION_STATUS.md','docs/engineering/NET33_VIDEO_DAC.md','references/net33-review.json'}
TOOLS={'tools/build_dac_video_adapter.py','tools/run_video_dac_checks.py','tools/check_video_dac_native.py',
       'tools/record_net33_results.py','tools/stage_net33_results.py'}

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',newline='\n')
def graph(path):
    root=ET.parse(path).getroot()
    return {'parts':sorted((c.get('ref'),c.findtext('value'),json.dumps(c.find('libsource').attrib,sort_keys=True)) for c in root.findall('./components/comp')),
            'nets':sorted((n.get('name'),sorted((p.get('ref'),p.get('pin')) for p in n.findall('node'))) for n in root.findall('./nets/net'))}

def main():
    assert git('rev-parse','HEAD').decode().strip()==BASE
    checked=0;resolved=[]
    def sources(report,aliases=None):
        nonlocal checked
        for row in report.get('sources',[]):
            name=row['path'];path=ROOT/name
            if digest(path)!=row['sha256']:
                assert aliases and name in aliases,name
                path=ROOT/aliases[name];assert digest(path)==row['sha256'],name
                resolved.append({'path':name,'sha256':row['sha256'],'preserved_source':path.relative_to(ROOT).as_posix()})
            checked+=1
    native=json.loads((OUT/'native-results.json').read_text());sources(native)
    assert not native['failures'] and native['video_ics']==38 and native['dac_ics']==3
    assert len(native['video_pin_changes_in_spare_channels'])==14 and native['combined_components']==100
    cases=json.loads((OUT/'raster-dac-results.json').read_text());sources(cases)
    assert not cases['failures'] and len(cases['runs'])==6
    for row in cases['runs']:
        assert row['passed'] and row['compile']['exit']==0 and not row['compile']['stderr']
        result=row['execution'];assert not result['wall_timeout'] and not result['stderr']
        assert row['expected_marker'] in result['stdout']
        assert (result['exit']!=0)==(row['negative']!=0)
    pins=json.loads((OUT/'pin-negative-results.json').read_text());sources(pins)
    assert not pins['failures'] and len(pins['pin_negatives'])==8 and all(r['rejected'] for r in pins['pin_negatives'])
    loads=json.loads((OUT/'pin-loads.json').read_text());assert loads['maximum_inputs']==4
    assert len(loads['inputs']['DAC_CLK'])==4 and len(loads['inputs']['P1'])==4
    for name in ['BLUE0_BUFFER','BLUE1_BUFFER','PIXEL_0','PIXEL_1','BUF_1_2']:assert len(loads['inputs'][name])==3
    before=OUT/'development/page-A1'
    for label,name in [('video','dac_packet_video'),('dac','vga_dac_rgb332')]:
        assert graph(OUT/label/(name+'.xml'))==graph(before/label/(name+'.xml'))
        for file in ['commands.json','preview-commands.json']:
            jobs=json.loads((OUT/label/file).read_text())
            assert all(j['exit']==0 and not j['wall_timeout'] for j in jobs.values())
    for path,sha in json.loads((before/'model-hashes.json').read_text()).items():assert digest(ROOT/path)==sha
    aliases={'tools/build_dac_video_adapter.py':(before/'build_dac_video_adapter.py').relative_to(ROOT).as_posix(),
             'verification/net33/video/dac_packet_video.xml':(before/'video/dac_packet_video.xml').relative_to(ROOT).as_posix(),
             'verification/net33/dac/vga_dac_rgb332.xml':(before/'dac/vga_dac_rgb332.xml').relative_to(ROOT).as_posix()}
    for file in ['native-results.json','pin-negative-results.json']:sources(json.loads((before/file).read_text()),aliases)
    parent=json.loads((ROOT/'hardware/load_distributed_video/design.json').read_text())['parts']
    current=json.loads((ROOT/'hardware/dac_packet_video/design.json').read_text())['parts']
    old={p['reference']:p for p in parent};new={p['reference']:p for p in current}
    assert set(new)-set(old)=={'U38','C38'}
    observed=[]
    for ref,p in old.items():
        assert p['part']==new[ref]['part']
        observed.extend({'reference':ref,'pin':pin,'before':net,'after':new[ref]['nets'][pin]} for pin,net in p['nets'].items() if net!=new[ref]['nets'][pin])
    assert observed==native['video_pin_changes_in_spare_channels'] or sorted(observed,key=str)==sorted(native['video_pin_changes_in_spare_channels'],key=str)
    assert not git('diff','--name-only',BASE,'--','archive','revisions','hardware/load_distributed_video','sim/net30')
    save(OUT/'pending-integrity.json',[pending_integrity(p) for p in PENDING])
    versions={}
    for name,command in [('python',['python3','--version']),('iverilog',['iverilog','-V']),
                         ('kicad',['/home/gabri/.local/opt/isa1-kicad-10.0.8/squashfs-root/usr/bin/kicad-cli','version'])]:
        cmd=['wsl','-d','Ubuntu','--',*command]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        assert result.returncode==0
        versions[name]={'command':cmd,'stdout':result.stdout,'stderr':result.stderr,'exit':result.returncode}
    audit={'date':'2026-11-27','base_git_commit':BASE,'source_records_checked':checked,'historical_source_resolutions':resolved,
        'original_video_pin_changes_exact':True,'model_bytes_unchanged_after_page_fix':True,'electrical_graph_unchanged_after_page_fix':True,
        'positive_native_scenarios':4,'reset_epochs_each':2,'samples_each':210000,'colors_each':256,
        'functional_negatives':2,'structural_negatives':8,'versions':versions,
        'visual_review':'A0 video preview now contains all components; DAC preview checked; earlier clipped A1 presentation preserved.',
        'erc_approved':False,'complete_net30_system_integrated':False,'analog_validated':False,'production_released':False}
    save(OUT/'result-audit.json',audit)
    files=[];excluded=[]
    for row in git('status','--porcelain=v1','-z','--untracked-files=all').split(b'\0'):
        if not row:continue
        assert row[:2] not in (b'R ',b' R',b'C ',b' C')
        name=row[3:].decode()
        if name.startswith(PENDING):excluded.append(name);continue
        assert name in DOCS or name in TOOLS or name.startswith(('hardware/dac_packet_video/','hardware/vga_dac_rgb332/','sim/net33/','verification/net33/')),name
        if name!='verification/net33/manifest.json':files.append(name)
    manifest={**audit,'scope':'Two native video/DAC leaves, selected digital tests, not CPU/full-system/analog qualification',
        'excluded_pending_run_prefix':PENDING,'excluded_files_at_snapshot':excluded,
        'commands':['python3 tools/build_dac_video_adapter.py','python3 tools/run_video_dac_checks.py','python3 tools/check_video_dac_native.py',
                    'python tools/record_net33_results.py','python tools/stage_net33_results.py verification/net33/manifest.json'],
        'files':[{'path':n,'bytes':(ROOT/n).stat().st_size,'sha256':digest(ROOT/n)} for n in sorted(files)]}
    save(OUT/'manifest.json',manifest)
    print(json.dumps({'files':len(files),'source_records_verified':checked,'historical_resolutions':len(resolved),'pending_runs':2,'production_released':False}))

if __name__=='__main__':main()
