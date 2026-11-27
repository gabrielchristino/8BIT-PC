# GENERATED NET30 separate candidate; no qualification inherited.
"""Source-driven12-cut SRAM pin fixture, two RC bounds/policies and negatives."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run
from run_system_cpu import MODELS
from run_request_skew_probe import once

ROOT=Path(__file__).resolve().parents[1]

def main():
    source='sim/net21/tb_reset_memory.sv';text=(ROOT/source).read_text()
    old=''' reg clk=0,master=0,run_cpu=1,run_master=1,raw=1;
 always #5000 if(run_cpu)clk=~clk;
 always #19.860973 if(run_master)master=~master;'''
    text=once(text,old,' reg raw=1;\n wire clk=memory.cpu_source,master=memory.master_source;')
    text=once(text,'isa1_memory #','isa1_clocked_memory #')
    text=once(text,"   clk,master,raw,1'b1,request,wr,address,data", "   raw,1'b1,1'b1,request,wr,address,data")
    text=once(text,'run_cpu=0;', 'force memory.reset_domains.n_CPU_OSC=0;')
    text=once(text,'run_cpu=1;', '@(negedge memory.reset_domains.X1.phase);release memory.reset_domains.n_CPU_OSC;')
    text=once(text,'run_master=0;', 'force memory.reset_domains.n_MASTER=0;')
    text=once(text,'run_master=1;', '@(negedge memory.reset_domains.X2.phase);release memory.reset_domains.n_MASTER;')
    text=once(text,'#10000000;$fatal', '#30000000;$fatal')
    dest='sim/net30/tb_load_memory.sv';(ROOT/dest).write_text('// GENERATED source-driven memory pin test; watchdog30ms covers configured10ms source startup; all100ns/write/hold/reset assertions unchanged.\n'+text)
    names=[('hardware/common_request/common_request_netlist.sv' if p=='hardware/system_access/system_access_netlist.sv' else 'hardware/load_distributed_keyboard/load_distributed_keyboard_netlist.sv' if p=='hardware/keyboard_500/keyboard_500_netlist.sv' else p) for p in MODELS if p not in ('sim/net19a/isa1_memory_system.sv','sim/net14c/video_raster_async_netlist.sv')]+[
        'hardware/local_phase_reset/local_phase_reset_netlist.sv','sim/net23/clock_models.sv','sim/net30/isa1_memory_loads.sv','sim/net22/phase_packages.sv','sim/net25/warm_packages.sv','sim/net30/load_video_async.sv',dest]
    names = [('hardware/load_distributed_bus/load_distributed_bus_netlist.sv' if p=='hardware/memory_bus/memory_bus_netlist.sv' else p) for p in names]
    report={'date':'2026-11-26','scope':'Actual native SRAM pins under qualified digital VDD:12active cuts per RC/policy, retained payload, two edge-aligned source pauses; no CPU instruction execution here. Supervisor/RC/source/binary boundaries conditional, not analog/global timing/POR/MTBF proof.',
        'transformation':'External stimulus clocks replaced by native source outputs. Pauses force actual source output low on falling edge and resume on matching internal phase; no arbitrary pulse/slew restart guarantee. Watchdog10->30ms only for native10ms startup; original100ns WE and pin/hold assertions unchanged.',
        'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+['tools/build_distributed_loads.py', 'tools/prepare_distributed_load_checks.py', 'hardware/load_distributed_video/design.json', 'hardware/load_distributed_keyboard/design.json', 'hardware/load_distributed_bus/design.json', 'verification/net30/native/bus/load_distributed_bus.xml', source,'tools/run_distributed_load_memory.py','tools/prepare_local_phase_checks.py']],
        'runs':[],'negative':[],'failures':[],'production_released':False}
    configs=[(p,0,0,a) for p in [0,1] for a in [1000,19000]]+[(1,1,0,1000),(1,0,1,1000)]
    with tempfile.TemporaryDirectory(prefix='isa1-local-memory-') as tmp:
        work=Path(tmp)
        for policy,bank,address,assertion in configs:
            cmd=['iverilog','-g2012','-Wall','-s','tb_reset_memory',f'-Ptb_reset_memory.POLICY={policy}',f'-Ptb_reset_memory.FAULT_BANK={bank}',f'-Ptb_reset_memory.FAULT_ADDRESS={address}',f'-Ptb_reset_memory.ASSERT_NS={assertion}','-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names]]
            row={'policy':policy,'assertion_ns':assertion,'early_bank_fault':bank,'address_fault':address,'compile':run(cmd,work)}
            if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=240)
            r=row.get('execution',{});expected='memory bank reset before physical WE inhibition' if bank else 'independent RAM pin address changed while WE low'
            row['passed']=row['compile']['exit']==0 and not row['compile']['stderr'] and (r.get('exit') not in (None,0) and expected in r.get('stdout','') if bank or address else r.get('exit')==0 and 'active_write_cuts=12 stopped_clocks=2' in r.get('stdout','') and 'failures=0' in r.get('stdout',''))
            report['negative' if bank or address else 'runs'].append(row)
            if not row['passed']:report['failures'].append([policy,bank,address,assertion])
            (ROOT/'verification/net30/memory-pin-results.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(row),flush=True)
            if not row['passed']:return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
