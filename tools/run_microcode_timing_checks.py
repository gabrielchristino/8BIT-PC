"""Intentional setup/hold/recovery failures must be detected by NET-04 monitors."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import ROOT,run


def main():
    files=[ROOT/'sim/net04/package_models.sv',ROOT/'sim/net04/tb_timing_negative.sv']
    report={'date':'2026-11-25','scope':'Expected-negative monitor checks, not board timing closure',
      'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [*files,Path(__file__)]],'checks':[]}
    messages=['HC161 setup envelope','HC161 clear recovery','HCT377 data setup','HCT377 enable setup','HCT377 data hold','HCT377 enable hold']
    with tempfile.TemporaryDirectory(prefix='isa1-micro-timing-') as temporary:
        work=Path(temporary)
        for case,message in enumerate(messages):
            compiled=run(['iverilog','-g2012','-Wall','-s','tb_timing_negative',f'-Ptb_timing_negative.CASE={case}','-o',str(work/'bad.vvp'),*map(str,files)],work)
            executed=run(['vvp',str(work/'bad.vvp')],work) if compiled['exit']==0 else None
            passed=executed is not None and executed['exit']!=0 and message+' violation' in executed['stdout']
            report['checks'].append({'case':message,'expected_rejection':True,'passed':passed,'compile':compiled,'execution':executed})
    (ROOT/'verification/net04/timing-negative.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True);return int(not all(r['passed'] for r in report['checks']))


if __name__=='__main__':raise SystemExit(main())
