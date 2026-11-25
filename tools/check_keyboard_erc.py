"""Record both partial NET-15 sheets without ERC waivers."""
import hashlib
import json
from pathlib import Path
import subprocess
from build_mmio_keyboard import ROOT,KICAD


def main():
    reports=[]
    for sheet,folder in [('mmio_keyboard','verification/net15'),('keyboard_access','verification/net15/access')]:
        source=ROOT/'hardware'/sheet;out=ROOT/folder
        cmd=[KICAD,'sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(out/'erc.json'),str(source/(sheet+'.kicad_sch'))]
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        raw=json.loads((out/'erc.json').read_text());counts={}
        for page in raw.get('sheets',[]):
            for item in page.get('violations',[]):counts[item['type']]=counts.get(item['type'],0)+1
        files=[source/(sheet+'.kicad_sch'),source/(sheet+'.kicad_pro'),*source.glob('*.kicad_sym'),Path(__file__)]
        report={'date':'2026-11-25','sheet':sheet,'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,
          'kicad':subprocess.check_output([KICAD,'version'],text=True).strip(),'violation_counts':counts,
          'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
          'erc_passed':r.returncode==0,'board_release':False,'scope':'Partial sheet; global power/signal union and PCB absent. No waivers.'}
        (out/'erc-summary.json').write_text(json.dumps(report,indent=2)+'\n')
        pdf=out/(sheet+'.pdf')
        subprocess.run([KICAD,'sch','export','pdf','-o',str(pdf),str(source/(sheet+'.kicad_sch'))],check=True,capture_output=True)
        subprocess.run(['pdftoppm','-scale-to','1800','-png','-singlefile',str(pdf),str(out/'preview')],check=True)
        reports.append(report)
    print(json.dumps(reports));return max(r['exit'] for r in reports)


if __name__=='__main__':raise SystemExit(main())
