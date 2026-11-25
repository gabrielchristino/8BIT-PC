"""Expected failures prove selected register timing monitors reject bad pulses."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import ROOT,run
OUT=ROOT/'verification/net06'


def main():
    models=[ROOT/'sim/net02/package_models.sv',ROOT/'sim/net03/package_models.sv']
    bench=ROOT/'sim/net06/tb_register_timing_negative.sv'
    sources=[*models,bench,Path(__file__)]
    cases=[('HC273 data setup','HC273 data setup violation'),('HC273 clear recovery','HC273 clear recovery violation'),
      ('HC273 clock pulse','HC273 clock pulse violation'),('HC273 clear pulse','HC273 clear pulse violation'),
      ('HC74 data setup','DFF data setup violation'),('HC74 clear recovery','DFF clear recovery violation'),
      ('HC74 clock pulse','DFF clock pulse violation'),('HC74 clear pulse','DFF clear pulse violation')]
    report={'date':'2026-11-25','scope':'Expected-negative selected timing monitor checks; not production timing closure',
      'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],'checks':[]}
    with tempfile.TemporaryDirectory(prefix='isa1-register-timing-') as tmp:
        work=Path(tmp)
        for number,(name,message) in enumerate(cases):
            compiled=run(['iverilog','-g2012','-Wall','-s','tb_register_timing_negative',f'-Ptb_register_timing_negative.CASE={number}','-o',str(work/'bad.vvp'),*map(str,models),str(bench)],work)
            executed=run(['vvp',str(work/'bad.vvp')],work) if compiled['exit']==0 else None
            passed=executed is not None and executed['exit']!=0 and message in executed['stdout']
            report['checks'].append({'case':name,'expected_rejection':True,'passed':passed,'compile':compiled,'execution':executed})
    (OUT/'timing-negative.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'checks':len(cases),'passed':sum(c['passed'] for c in report['checks'])}))
    return int(not all(c['passed'] for c in report['checks']))


if __name__=='__main__':raise SystemExit(main())
