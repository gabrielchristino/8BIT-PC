"""NET-04: registered original control lanes, microsequencer and CPU regressions."""
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
from build_microcode_bank import convert,definitions
OUT=ROOT/'verification/net04'


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
      'sim/net04/package_models.sv','hardware/microcode_bank/microcode_bank_netlist.sv','sim/net04/isa1_cpu_microcode.sv','sim/rtl/isa1_memory.sv')]
    benches=['tb_rtl_cpu','tb_rtl_safety','tb_stack_guards','tb_rtl_program']
    sources=[*models,Path(__file__),ROOT/'tools/run_rtl.py',ROOT/'tools/make_stack_cpu.py',ROOT/'tools/build_stack_bank.py',ROOT/'tools/build_transaction_bank.py',
      ROOT/'tools/build_microcode_bank.py',ROOT/'tools/make_microcode_cpu.py',ROOT/'sim/hdl/counter_load_candidate.sv',ROOT/'sim/net04/tb_microcode_bank.sv',ROOT/'hardware/microcode_bank/microcode_bank.kicad_sch',
      OUT/'microcode_bank.xml',ROOT/'firmware/rtl01_diagnostic.asm']
    sources += [ROOT/'sim/tests'/(n+'.sv') for n in benches]
    sources += [BASE/f'control_lane{i}.bin' for i in range(4)]
    sources += [BASE/n for n in ('cpu.py','system.py','control.py','microcode.py','sequencer.py','assembler.py')]
    report={'iteration':'NET-04','date':'2026-11-25','quick':quick,'platform':platform.platform(),'python':platform.python_version(),
      'iverilog':subprocess.run(['iverilog','-V'],capture_output=True,text=True).stdout.splitlines()[0],
      'scope':'Pin-connected microsequencer, read-only control EEPROMs, held control word and field decoders; integrated CPU. Not complete-board release.',
      'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],'runs':[],'negative_checks':[]}
    def save():(OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='isa1-net04-') as temporary:
        work=Path(temporary)
        lanes=[(BASE/f'control_lane{i}.bin').read_bytes() for i in range(4)]
        words=[sum(lanes[l][a]<<(8*l) for l in range(4)) for a in range(8192)]
        from sequencer import ROM
        from control import FETCH,TABLE
        assert words==ROM
        (work/'control.hex').write_text(''.join(f'{w:08x}\n' for w in words))
        for i,lane in enumerate(lanes):(work/f'control_lane{i}.hex').write_text(''.join(f'{b:02x}\n' for b in lane))
        sequences=[]
        for op in range(256):
            entries=[(4096+i,w) for i,w in enumerate(FETCH)]+[(op*16+i,w) for i,w in enumerate(TABLE.get(op,[1<<25]))]
            cutoff=next((i+1 for i,(_,w) in enumerate(entries) if w&(1<<25)),len(entries));entries=entries[:cutoff]
            row=[len(entries)]+[value for pair in entries for value in pair];assert len(row)<=64
            sequences += row+[0]*(64-len(row))
        (work/'sequences.hex').write_text(''.join(f'{n:08x}\n' for n in sequences))
        rows,report['opcode_cases']=fixtures(quick)
        vectors=''.join(''.join(f'{v:08x}\n' for v in row) for row in rows)
        (work/'vectors.hex').write_text(vectors);report['vector_sha256']=hashlib.sha256(vectors.encode()).hexdigest()
        report['program'],frame,png=program_fixture(work)
        for bench in benches:
            text=transform_bench((ROOT/'sim/tests'/(bench+'.sv')).read_text())
            if bench=='tb_stack_guards':text=prepare_guard(text)
            (work/(bench+'.sv')).write_text(text)
        shutil.copyfile(ROOT/'sim/net04/tb_microcode_bank.sv',work/'tb_microcode_bank.sv')
        configurations=[('tb_microcode_bank',0),('tb_microcode_bank',1),('tb_rtl_cpu',0),('tb_rtl_cpu',1),('tb_rtl_safety',0),('tb_rtl_safety',1)]
        if not quick:configurations += [('tb_stack_guards',0),('tb_rtl_program',0),('tb_rtl_program',1)]
        for bench,variant in configurations:
            cmd=['iverilog','-g2012','-Wall','-s',bench];cfg={}
            if bench=='tb_microcode_bank':cfg['timed']=variant;cmd += [f'-P{bench}.TIMED={variant}']
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
        # Word-enable stuck active must expose corrupted raw ROM during WAIT.
        tree=ET.parse(OUT/'microcode_bank.xml')
        ground=next(n for n in tree.getroot().findall('./nets/net') if n.get('name').removeprefix('/')=='GND')
        for net in tree.getroot().findall('./nets/net'):
            for node in list(net.findall('node')):
                if node.get('ref')=='U7' and node.get('pin')=='1':net.remove(node);ground.append(node)
        tree.write(work/'bad-word.xml');convert(work/'bad-word.xml',definitions(),work/'bad-bank.sv')
        badmodels=[p for p in models if p.name!='microcode_bank_netlist.sv']+[work/'bad-bank.sv']
        compiled=run(['iverilog','-g2012','-Wall','-s','tb_microcode_bank','-o',str(work/'bad.vvp'),*map(str,badmodels),str(work/'tb_microcode_bank.sv')],work)
        executed=run(['vvp',str(work/'bad.vvp')],work) if compiled['exit']==0 else None
        report['negative_checks'].append({'case':'Control word enable stuck active','expected_rejection':True,'passed':executed is not None and executed['exit']!=0 and 'ROM outputs leaked' in executed['stdout'],'compile':compiled,'execution':executed})
        tree=ET.parse(OUT/'microcode_bank.xml')
        for net in tree.getroot().findall('./nets/net'):
            for node in list(net.findall('node')):
                if node.get('ref')=='U11' and node.get('pin')=='27':net.remove(node)
        tree.write(work/'floating.xml')
        try:convert(work/'floating.xml',definitions(),work/'floating.sv')
        except ValueError as error:message=str(error)
        else:message='No rejection'
        report['negative_checks'].append({'case':'Floating control EEPROM WE','expected_rejection':True,'passed':'Floating input U11/27' in message,'message':message})
        save();print(json.dumps({'negative_checks':report['negative_checks']}),flush=True)
        return int(not all(r['passed'] for r in report['negative_checks']))


if __name__=='__main__':raise SystemExit(main())
