"""Record unwaived ERC for the partial NET-11 decoder schematic."""
import collections
import hashlib
import json
import subprocess
from build_memory_decode import ROOT,OUT,VERIFY,KICAD


def main():
    command=[KICAD,'sch','erc','--format','json','--severity-all','--exit-code-violations',
      '-o',str(VERIFY/'erc.json'),str(OUT/'memory_decode.kicad_sch')]
    r=subprocess.run(command,capture_output=True,text=True,timeout=120)
    if r.returncode not in (0,5):raise RuntimeError(r.stdout+r.stderr)
    raw=json.loads((VERIFY/'erc.json').read_text());v=[v for s in raw['sheets'] for v in s['violations']]
    report={'date':'2026-11-25','kicad':subprocess.check_output([KICAD,'version'],text=True).strip(),
      'command':command,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,
      'violation_counts':dict(collections.Counter(x['type'] for x in v)),
      'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in [OUT/'memory_decode.kicad_sch',OUT/'memory_packages.kicad_sym',OUT/'sym-lib-table',OUT/'memory_decode.kicad_pro']],
      'erc_passed':not v,'board_release':False,
      'reason':'Partial decoder has no external sources or output consumers; no waivers inserted'}
    (VERIFY/'erc-summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['exit','violation_counts','erc_passed','board_release']}));return r.returncode


if __name__=='__main__':raise SystemExit(main())
