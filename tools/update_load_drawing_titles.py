"""Correct candidate title metadata after regressions, prove pin graphs equal."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from build_cpu_global import KICAD
from limited_process import run_limited

ROOT=Path(__file__).resolve().parents[1]
BASE='16a82e4866ac9c791dfae0e162c2f887842b1f52'
OUT=ROOT/'verification/net30/title-update-final'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def canonical(path):
    root=ET.parse(path).getroot()
    parts=sorted((p.get('ref'),p.findtext('value'),p.findtext('footprint',''),json.dumps(p.find('libsource').attrib,sort_keys=True)) for p in root.findall('./components/comp'))
    nets=sorted((n.get('name'),sorted((p.get('ref'),p.get('pin')) for p in n.findall('node'))) for n in root.findall('./nets/net'))
    return json.dumps({'parts':parts,'nets':nets},sort_keys=True).encode()

def main():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==BASE
    assert all(json.loads(p.read_text())['status']!='running' for p in (ROOT/'verification/net30/jobs').glob('*/run-state.json'))
    assert not OUT.exists(),'Preserve prior title update'
    OUT.mkdir(parents=True)
    report={'date':'2026-11-27','base_commit':BASE,'scope':'Title/date metadata only, no SV/design/pin changes or new functional pass. Before bytes remain in base commit and copied originals.',
        'rows':[],'sources':[{'path':'tools/update_load_drawing_titles.py','sha256':digest(Path(__file__))}],'production_released':False}
    for kind,old_revision,new_revision in [('video','NET-26V','NET-30V'),('keyboard','NET-26K','NET-30K'),('bus','NET-30B','NET-30B')]:
        name='load_distributed_'+kind;folder=ROOT/'hardware'/name;native=ROOT/'verification/net30/native'/kind
        schematic=folder/(name+'.kicad_sch');xml=native/(name+'.xml');model=folder/(name+'_netlist.sv');design=folder/'design.json'
        saved=OUT/'original'/kind;saved.mkdir(parents=True)
        before={p.relative_to(ROOT).as_posix():digest(p) for p in [schematic,xml,model,design]}
        for p in [schematic,xml]:
            assert subprocess.check_output(['git','show',BASE+':'+p.relative_to(ROOT).as_posix()],cwd=ROOT)==p.read_bytes()
            shutil.copyfile(p,saved/p.name)
        text=schematic.read_text();old_date='(date "2026-11-25")';new_date='(date "2026-11-27")'
        assert text.count(old_date)==1 and text.count('(rev "'+old_revision+'")')==1
        revised=text.replace(old_date,new_date).replace('(rev "'+old_revision+'")','(rev "'+new_revision+'")')
        # Reversibility of exactly these field substitutions rules out an
        # accidental symbol/position/net/pin change in the schematic text.
        assert revised.replace(new_date,old_date).replace('(rev "'+new_revision+'")','(rev "'+old_revision+'")')==text
        schematic.write_text(revised)
        commands=[]
        with tempfile.TemporaryDirectory(prefix='isa1-title-export-') as tmp:
            candidate=Path(tmp)/'candidate.xml'
            command=[KICAD,'sch','export','netlist','--format','kicadxml','-o',str(candidate),str(schematic)]
            result=run_limited(command,ROOT,120,2048,90,8);commands.append(result)
            (OUT/(kind+'-netlist-command.json')).write_text(json.dumps(result,indent=2)+'\n')
            assert result['exit']==0,result
            assert canonical(candidate)==canonical(xml)
            shutil.copyfile(candidate,xml)
        erc_file=OUT/(kind+'-erc.json')
        command=[KICAD,'sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(erc_file),str(schematic)]
        result=run_limited(command,ROOT,120,2048,90,8);commands.append(result)
        (OUT/(kind+'-erc-command.json')).write_text(json.dumps(result,indent=2)+'\n')
        assert erc_file.is_file(),result
        erc=json.loads(erc_file.read_text());counts={}
        for sheet in erc.get('sheets',[]):
            for row in sheet.get('violations',[]):counts[row['type']]=counts.get(row['type'],0)+1
        old=json.loads((native/'erc-summary.json').read_text())
        assert counts==old['counts'] and result['exit']==old['exit']
        for command in [[KICAD,'sch','export','pdf','-o',str(native/(name+'.pdf')),str(schematic)],
            ['pdftoppm','-scale-to','1800','-png','-singlefile',str(native/(name+'.pdf')),str(native/'preview')]]:
            result=run_limited(command,ROOT,120,2048,90,8);commands.append(result)
            (OUT/(kind+'-render-command-'+str(len(commands))+'.json')).write_text(json.dumps(result,indent=2)+'\n')
            assert result['exit']==0,result
        assert digest(model)==before[model.relative_to(ROOT).as_posix()] and digest(design)==before[design.relative_to(ROOT).as_posix()]
        report['rows'].append({'kind':kind,'before_sha256':before,'after_sha256':{p.relative_to(ROOT).as_posix():digest(p) for p in [schematic,xml,model,design]},
            'original_schematic':(saved/schematic.name).relative_to(ROOT).as_posix(),'original_xml':(saved/xml.name).relative_to(ROOT).as_posix(),
            'pin_component_graph_sha256':hashlib.sha256(canonical(xml)).hexdigest(),'pin_component_graph_equal':True,'commands':commands,'erc_counts':counts})
        (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({'kind':kind,'pin_graph_unchanged':True,'erc_unchanged':counts}),flush=True)

if __name__=='__main__':main()
