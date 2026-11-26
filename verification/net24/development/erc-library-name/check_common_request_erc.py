"""Record actual partial-sheet ERC and rendering, with no exceptions."""
import hashlib
import json
from pathlib import Path
import subprocess
from build_common_request import ROOT,OUT,VERIFY,KICAD


def main():
    command=[KICAD,'sch','erc','--format','json','--severity-all','--exit-code-violations',
             '-o',str(VERIFY/'erc.json'),str(OUT/'common_request.kicad_sch')]
    result=subprocess.run(command,capture_output=True,text=True)
    data=json.loads((VERIFY/'erc.json').read_text());counts={}
    for sheet in data.get('sheets',[]):
        for item in sheet.get('violations',[]):counts[item['type']]=counts.get(item['type'],0)+1
    paths=[OUT/'common_request.kicad_sch',OUT/'common_request.kicad_pro',OUT/'bus_packages.kicad_sym',Path(__file__)]
    report={'date':'2026-11-26','kicad':subprocess.check_output([KICAD,'version'],text=True).strip(),
            'command':command,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
            'violation_counts':counts,'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
            'erc_passed':result.returncode==0,'board_release':False,
            'scope':'Partial controller candidate sheet. Power/inputs/outputs require global union; no waivers added.'}
    (VERIFY/'erc-summary.json').write_text(json.dumps(report,indent=2)+'\n')
    subprocess.run([KICAD,'sch','export','pdf','-o',str(VERIFY/'common_request.pdf'),str(OUT/'common_request.kicad_sch')],capture_output=True,check=True)
    subprocess.run(['pdftoppm','-scale-to','1800','-png','-singlefile',str(VERIFY/'common_request.pdf'),str(VERIFY/'preview')],check=True)
    print(json.dumps(report));return result.returncode


if __name__=='__main__':raise SystemExit(main())
