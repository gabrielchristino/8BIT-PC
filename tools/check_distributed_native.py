"""Unwaived ERC/PDF exports of three new candidate leaves only."""
import hashlib
import json
from pathlib import Path
import subprocess
from build_cpu_global import KICAD

ROOT=Path(__file__).resolve().parents[1]

def main():
    for kind in ['video','keyboard','bus']:
        name='load_distributed_'+kind;folder=ROOT/'hardware'/name;out=ROOT/'verification/net30/native'/kind
        cmd=[KICAD,'sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(out/'erc.json'),str(folder/(name+'.kicad_sch'))]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        data=json.loads((out/'erc.json').read_text());counts={}
        for sheet in data.get('sheets',[]):
            for item in sheet.get('violations',[]):counts[item['type']]=counts.get(item['type'],0)+1
        record={'date':'2026-11-26','command':cmd,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
            'counts':counts,'erc_passed':result.returncode==0,'production_released':False,
            'scope':'Unwaived partial native candidate ERC, not global board approval.',
            'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [
                Path(__file__),folder/(name+'.kicad_sch'),folder/'design.json']]}
        (out/'erc-summary.json').write_text(json.dumps(record,indent=2)+'\n')
        subprocess.run([KICAD,'sch','export','pdf','-o',str(out/(name+'.pdf')),str(folder/(name+'.kicad_sch'))],capture_output=True,check=True,timeout=120)
        subprocess.run(['pdftoppm','-scale-to','1800','-png','-singlefile',str(out/(name+'.pdf')),str(out/'preview')],capture_output=True,check=True,timeout=120)
        print(json.dumps({'kind':kind,'erc':counts,'erc_passed':record['erc_passed']}),flush=True)

if __name__=='__main__':main()
