"""Record unwaived CPU-only ERC; violations remain a failed production gate."""
import collections
import hashlib
import json
import subprocess
from build_cpu_global import ROOT, OUT, VERIFY, KICAD


def main():
    command=[KICAD,'sch','erc','--format','json','--severity-all',
             '--exit-code-violations','-o',str(VERIFY/'erc-cpu-only.json'),str(OUT/'cpu_global.kicad_sch')]
    result=subprocess.run(command,capture_output=True,text=True,timeout=120)
    if result.returncode not in (0,5):raise RuntimeError(result.stdout+result.stderr)
    raw=json.loads((VERIFY/'erc-cpu-only.json').read_text())
    violations=[v for sheet in raw['sheets'] for v in sheet['violations']]
    report={'date':'2026-11-25','kicad':subprocess.check_output([KICAD,'version'],text=True).strip(),
        'command':command,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
        'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                   for p in [*sorted(OUT.glob('*.kicad_sch')),OUT/'cpu_packages.kicad_sym',OUT/'sym-lib-table',OUT/'cpu_global.kicad_pro']],
        'violation_counts':dict(collections.Counter(v['type'] for v in violations)),
        'erc_passed':not violations,'board_release':False,
        'reason':'CPU-only boundary lacks external power/clock/reset/ack/data/boot/run and consumers; violations retained, no waivers inserted'}
    (VERIFY/'erc-summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('exit','violation_counts','erc_passed','board_release')}))
    return result.returncode


if __name__=='__main__':raise SystemExit(main())
