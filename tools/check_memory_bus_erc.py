"""Record unwaived ERC for both separate NET-13 native schematics."""
import collections
import hashlib
import json
import subprocess
from build_memory_bus import ROOT,VERIFY,KICAD


def main():
    reports=[]
    for directory,schematic,library,label in [('hardware/memory_bus','memory_bus','bus_packages','bus'),('hardware/memory_bus_access','memory_access','access_packages','access')]:
        folder=ROOT/directory;out=VERIFY/(label+'-erc.json')
        cmd=[KICAD,'sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(out),str(folder/(schematic+'.kicad_sch'))]
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        if r.returncode not in (0,5):raise RuntimeError(r.stdout+r.stderr)
        raw=json.loads(out.read_text());v=[v for s in raw['sheets'] for v in s['violations']]
        reports.append({'name':label,'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'violation_counts':dict(collections.Counter(x['type'] for x in v)),
          'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [folder/(schematic+'.kicad_sch'),folder/(library+'.kicad_sym'),folder/'sym-lib-table',folder/(schematic+'.kicad_pro')]],'erc_passed':not v})
    report={'date':'2026-11-25','kicad':subprocess.check_output([KICAD,'version'],text=True).strip(),'schematics':reports,
      'scope':'Separate partial sheets, not joined board ERC. No waivers inserted; external sources/consumers/power remain absent.','board_release':False}
    (VERIFY/'erc-summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([{'name':r['name'],'exit':r['exit'],'counts':r['violation_counts']} for r in reports]));return 5 if any(r['exit'] for r in reports) else 0


if __name__=='__main__':raise SystemExit(main())
