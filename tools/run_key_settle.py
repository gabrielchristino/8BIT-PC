"""NET-15 real quiet counter + controller wait, ABI and held-reset scenarios."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net15'


def main():
    names=['sim/hdl/hc_models.sv','sim/net03/package_models.sv','sim/net04/package_models.sv','sim/net14b/package_models.sv',
      'hardware/memory_decode/memory_decode_netlist.sv','hardware/keyboard_access/keyboard_access_netlist.sv','hardware/mmio_keyboard/mmio_keyboard_netlist.sv','sim/net15/tb_key_settle.sv']
    report={'date':'2026-11-25','iteration':'NET-15','scope':'Pin-derived quiet timer and extended access controller; fixed master/backend stimuli; no analog/physical contact or MTBF approval',
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+['tools/run_key_settle.py','tools/build_keyboard_access.py','tools/build_mmio_keyboard.py']],
      'runs':[],'negative':[],'failures':[]}
    def save():(OUT/'settling-results.json').write_text(json.dumps(report,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='isa1-key-settle-') as tmp:
        work=Path(tmp)
        for timed,bypass in [(0,0),(1,0),(1,1)]:
            cmd=['iverilog','-g2012','-Wall','-s','tb_key_settle',f'-Ptb_key_settle.TIMED={timed}',f'-Ptb_key_settle.BYPASS_READY={bypass}',
              '-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names]]
            row={'timed':timed,'bypass_ready':bypass,'compile':run(cmd,work)}
            if not row['compile']['exit']:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=180)
            if bypass:
                row['expected_rejection']=True
                row['passed']=row['compile']['exit']==0 and row.get('execution',{}).get('exit',0)!=0 and 'column read acknowledged before settling' in row['execution']['stdout'];report['negative'].append(row)
            else:
                row['passed']=row['compile']['exit']==0 and row.get('execution',{}).get('exit')==0 and 'transactions=11 long_column_reads=4 short_accesses=7 reset_pending=1' in row['execution']['stdout'];report['runs'].append(row)
            if not row['passed']:report['failures'].append([timed,bypass])
            save();print(json.dumps(row),flush=True)
            if report['failures']:return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
