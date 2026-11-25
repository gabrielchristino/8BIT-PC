"""NET-09: registered original control lanes, microsequencer and CPU regressions."""
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from run_rtl import ROOT,BASE,fixtures,program_fixture,run
from make_stack_cpu import transform_bench
from build_x_register_bank import convert,definitions
from make_x_register_cpu import transform_bench as transform_x_bench
from make_execution_cpu import transform_bench as transform_execution_bench
from make_address_cpu import transform_bench as transform_address_bench
from make_register_cpu import transform_bench as transform_register_bench
OUT=ROOT/'verification/net09'


def prepare_guard(text):
    # Keep architectural guard checks, but establish the real registered word.
    text=text.replace('reg clk=0,reset_n=0,boot=0;', 'reg clk=0,reset_n=0,boot=0,run=0;')
    text=text.replace("dut(clk,reset_n,1'b1,1'b1,boot", "dut(clk,reset_n,1'b1,run,boot")
    text=text.replace('dut.fetch_bank=0;dut.ir=opcode;dut.microstep=which==0?4:0;',
      'dut.micro_bank.U2_0.q=1;dut.micro_bank.U4.q=opcode;dut.micro_bank.U1.q=which==0?4:0;')
    text=text.replace('reset_n=0;clk=0;boot=mode;', 'reset_n=0;clk=0;boot=mode;run=0;')
    text=text.replace('#1;clk=1;#1;\n       if(sp', '#1;clk=1;#1;clk=0;#1;run=1;#1;clk=1;#1;\n       if(sp')
    text=text.replace('if(req!==allowed','if(dut.bus_start!==allowed')
    return text


def main():
    OUT.mkdir(parents=True,exist_ok=True);quick='--quick' in sys.argv
    models=[ROOT/n for n in ('sim/hdl/hc_models.sv','sim/net04/counter_word_candidate.sv','sim/net02/package_models.sv',
      'hardware/stack_bank/stack_bank_netlist.sv','sim/net03/package_models.sv','hardware/transaction_bank/transaction_bank_netlist.sv',
      'sim/net04/package_models.sv','hardware/microcode_bank/microcode_bank_netlist.sv','hardware/alu_bank/alu_bank_netlist.sv','hardware/register_bank/register_bank_netlist.sv','hardware/address_bank/address_bank_netlist.sv','hardware/cpu_execution_glue/execution_bank_net09.sv','hardware/x_register_bank/x_register_bank_netlist.sv','sim/net09/isa1_cpu_pins.sv','sim/rtl/isa1_memory.sv')]
    benches=['tb_rtl_cpu','tb_rtl_safety','tb_stack_guards','tb_rtl_program']
    sources=[*models,Path(__file__),ROOT/'tools/run_rtl.py',ROOT/'tools/make_stack_cpu.py',ROOT/'tools/build_stack_bank.py',ROOT/'tools/build_transaction_bank.py',
      ROOT/'tools/build_microcode_bank.py',ROOT/'tools/make_microcode_cpu.py',ROOT/'tools/build_alu_bank.py',ROOT/'tools/make_alu_cpu.py',ROOT/'tools/build_register_bank.py',ROOT/'tools/make_register_cpu.py',ROOT/'tools/build_address_bank.py',ROOT/'tools/make_address_cpu.py',ROOT/'tools/build_execution_bank.py',ROOT/'tools/make_execution_cpu.py',ROOT/'tools/build_cpu_execution_glue.py',ROOT/'tools/build_x_register_bank.py',ROOT/'tools/make_x_register_cpu.py',ROOT/'sim/hdl/counter_load_candidate.sv',ROOT/'sim/net04/tb_microcode_bank.sv',ROOT/'hardware/microcode_bank/microcode_bank.kicad_sch',
      ROOT/'verification/net04/microcode_bank.xml',ROOT/'hardware/alu_bank/alu_bank.kicad_sch',ROOT/'verification/net05/alu_bank.xml',ROOT/'hardware/register_bank/register_bank.kicad_sch',ROOT/'verification/net06/register_bank.xml',ROOT/'hardware/address_bank/address_bank.kicad_sch',ROOT/'verification/net07/address_bank.xml',ROOT/'hardware/execution_bank/execution_bank.kicad_sch',ROOT/'verification/net08/execution_bank.xml',ROOT/'hardware/x_register_bank/x_register_bank.kicad_sch',OUT/'execution_glue.xml',ROOT/'hardware/cpu_execution_glue/execution_bank.kicad_sch',OUT/'x_register_bank.xml',ROOT/'sim/net09/tb_x_register_bank.sv',ROOT/'firmware/rtl01_diagnostic.asm']
    sources += [ROOT/'sim/tests'/(n+'.sv') for n in benches]
    sources += [BASE/f'control_lane{i}.bin' for i in range(4)]
    sources += [BASE/n for n in ('cpu.py','system.py','control.py','microcode.py','sequencer.py','assembler.py')]
    report={'iteration':'NET-09','date':'2026-11-25','quick':quick,'platform':platform.platform(),'python':platform.python_version(),
      'iverilog':subprocess.run(['iverilog','-V'],capture_output=True,text=True).stdout.splitlines()[0],
      'scope':'Main CPU state/control/datapath from package pin netlists; USE_HC191 alternative and memory/peripherals are separate reference models. Not complete-board release.',
      'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],'runs':[],'negative_checks':[]}
    def save():(OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='isa1-net09-') as temporary:
        work=Path(temporary)
        lanes=[(BASE/f'control_lane{i}.bin').read_bytes() for i in range(4)]
        words=[sum(lanes[l][a]<<(8*l) for l in range(4)) for a in range(8192)]
        from sequencer import ROM
        assert words==ROM
        (work/'control.hex').write_text(''.join(f'{w:08x}\n' for w in words))
        for i,lane in enumerate(lanes):(work/f'control_lane{i}.hex').write_text(''.join(f'{b:02x}\n' for b in lane))
        rows,report['opcode_cases']=fixtures(quick)
        vectors=''.join(''.join(f'{v:08x}\n' for v in row) for row in rows)
        (work/'vectors.hex').write_text(vectors);report['vector_sha256']=hashlib.sha256(vectors.encode()).hexdigest()
        report['program'],frame,png=program_fixture(work)
        for bench in benches:
            text=transform_bench((ROOT/'sim/tests'/(bench+'.sv')).read_text())
            if bench=='tb_stack_guards':text=prepare_guard(text)
            text=transform_x_bench(transform_execution_bench(transform_address_bench(transform_register_bench(text))))
            if '--trace' in sys.argv and bench=='tb_rtl_cpu':
                text=text.replace(' initial begin', ' always @(posedge clk)if(active && case_id==0)begin #0.003;$display("TRACE pc=%h ca=%h cw=%h ready=%b ep=%b state=%b q=%b req=%b start=%b",pc,ca,cw,dut.control_ready,dut.execute_pulse,dut.state,dut.execution_bank.U1.q,req,dut.bus_start);end\n initial begin',1)
            (work/(bench+'.sv')).write_text(text)
        shutil.copyfile(ROOT/'sim/net09/tb_x_register_bank.sv',work/'tb_x_register_bank.sv')
        configurations=[('tb_x_register_bank',0),('tb_x_register_bank',1),('tb_rtl_cpu',0),('tb_rtl_cpu',1),('tb_rtl_safety',0),('tb_rtl_safety',1)]
        if not quick:configurations += [('tb_stack_guards',0),('tb_rtl_program',0),('tb_rtl_program',1)]
        for bench,variant in configurations:
            cmd=['iverilog','-g2012','-Wall','-s',bench];cfg={}
            if bench=='tb_x_register_bank':cfg['timed']=variant;cmd += [f'-P{bench}.TIMED={variant}']
            if bench in ('tb_rtl_cpu','tb_rtl_safety','tb_rtl_program'):cfg['hc191']=variant;cmd += [f'-P{bench}.USE_HC191={variant}']
            if bench=='tb_rtl_cpu':cmd += [f'-P{bench}.CASES={len(rows)}']
            if bench=='tb_rtl_program':
                cmd += [f'-P{bench}.RETIREMENTS={report["program"]["retirements"]}',f'-P{bench}.BUS_COUNT={report["program"]["transactions"]}']
                if variant:cmd += [f'-P{bench}.CPU_HALF=7',f'-P{bench}.VIDEO_HALF=5']
            cmd += ['-o',str(work/'bench.vvp'),*map(str,models),str(work/(bench+'.sv'))]
            row={'bench':bench,'configuration':cfg,'compile':run(cmd,work)}
            if row['compile']['exit']==0:
                row['execution']=run(['vvp',str(work/'bench.vvp')],work,timeout=900)
                if bench=='tb_rtl_program' and row['execution']['exit']==0:
                    row['frame_matches_reference']=(work/'frame.ppm').read_bytes()==frame
                    if not row['frame_matches_reference']:row['execution']['exit']=1
                    else:shutil.copyfile(work/'frame.ppm',OUT/'frame.ppm');(OUT/'frame.png').write_bytes(png)
            report['runs'].append(row);save();print(json.dumps(row),flush=True)
            if row['compile']['exit'] or row.get('execution',{}).get('exit')!=0:return 1
        # Negative unit/connection tests are recorded separately for this control bank.
        save();print(json.dumps({'negative_checks':report['negative_checks']}),flush=True)
        return int(not all(r['passed'] for r in report['negative_checks']))


if __name__=='__main__':raise SystemExit(main())
