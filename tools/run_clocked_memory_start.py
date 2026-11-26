"""Observe real SRAM pins during source startup and missing-clock faults."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run
from run_system_cpu import MODELS

ROOT = Path(__file__).resolve().parents[1]


def main():
    names = [p for p in MODELS if p not in ('sim/net19a/isa1_memory_system.sv','sim/net14c/video_raster_async_netlist.sv')] + [
        'hardware/clocked_reset/clocked_reset_netlist.sv','sim/net23/clock_models.sv','sim/net23/isa1_clocked_memory.sv',
        'sim/net22/phase_packages.sv','sim/net22/video_common_async_netlist.sv','sim/net23/tb_clocked_memory_start.sv']
    report = {'date':'2026-11-26','scope':'Adversarial request master and independent physical WE/address monitors with native configured source/reset graph. No CPU execution in this bench; qualified VDD held valid until bank reset, analog/POR/jitter not qualified.',
              'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+['tools/run_clocked_memory_start.py']],
              'runs':[],'negative':[],'failures':[],'production_released':False}
    with tempfile.TemporaryDirectory(prefix='isa1-source-memory-') as tmp:
        work=Path(tmp)
        for absent,fault in [(0,0),(1,0),(2,0),(1,1)]:
            command=['iverilog','-g2012','-Wall','-s','tb_clocked_memory_start',
                     f'-Ptb_clocked_memory_start.ABSENT={absent}',f'-Ptb_clocked_memory_start.FAULT_SAFE={fault}',
                     '-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names]]
            row={'absent':absent,'force_safe_memory':bool(fault),'compile':run(command,work)}
            if row['compile']['exit']==0:
                row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=120)
            result=row.get('execution',{})
            expected='clock absence allowed physical SRAM WE' if fault else 'physical_we_inhibited=1' if absent else 'normal_sram_write=1 active_write_cut=1'
            row['passed']=row['compile']['exit']==0 and not row['compile']['stderr'] and (
                result.get('exit') not in (None,0) and expected in result.get('stdout','') if fault else
                result.get('exit')==0 and expected in result.get('stdout','') and 'failures=0' in result['stdout'])
            if fault:row['expected_rejection']=expected
            report['negative' if fault else 'runs'].append(row)
            if not row['passed']:report['failures'].append([absent,fault])
            (ROOT/'verification/net23/source-memory-results.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(row),flush=True)
            if not row['passed']:return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
