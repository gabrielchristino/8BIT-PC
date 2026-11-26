"""Trace the original level-based MMIO monitor around real FF sampling."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
import run_system_cpu as adapter
from run_rtl import BASE,fixtures,run


def main():
    out=ROOT/'verification/net19a/development'
    rows,_=fixtures(False);indices=list(range(len(rows)));rows=[rows[i] for i in indices]
    refs=json.loads((ROOT/'hardware/cpu_global/design.json').read_text())['reference_map']
    text=adapter.fixture((ROOT/'sim/tests/tb_rtl_cpu.sv').read_text(),False,refs)
    extra='''
 reg captured_commit=0;realtime captured_at=0;
 always @(posedge memory.peripheral.U1.clk)begin
   captured_commit=memory.io_commit;captured_at=$realtime;
 end
'''
    text=text.replace('endmodule',extra+'endmodule')
    old='$fatal(1,"MMIO change outside physical commit");'
    assert text.count(old)==1
    text=text.replace(old,'''begin
     $display("TRACE vector=%0d PC=%h address=%h row=%d q=%b io_commit_now=%b captured_commit=%b sampled_at=%0.3f now=%0.3f",case_id,pc,address,row,memory.peripheral.U1.q,memory.io_commit,captured_commit,captured_at,$realtime);
     $fatal(1,"MMIO change outside physical commit");
   end''')
    (out/'commit-trace-bench.sv').write_text(text)
    with tempfile.TemporaryDirectory(prefix='isa1-commit-trace-') as tmp:
        work=Path(tmp)
        for lane in range(4):
            data=(BASE/f'control_lane{lane}.bin').read_bytes();(work/f'control_lane{lane}.hex').write_text(''.join(f'{x:02x}\n' for x in data))
        (work/'vectors.hex').write_text(''.join(''.join(f'{x:08x}\n' for x in row) for row in rows))
        p=work/'bench.sv';p.write_text(text)
        cmd=['iverilog','-g2012','-Wall','-s','tb_rtl_cpu',f'-Ptb_rtl_cpu.CASES={len(rows)}','-o',str(work/'test.vvp'),*[str(ROOT/n) for n in adapter.MODELS],str(p)]
        report={'scope':'Diagnostic trace, not acceptance','original_vector_indices':indices,'adapted_bench_sha256':hashlib.sha256(text.encode()).hexdigest(),'compile':run(cmd,work)}
        if not report['compile']['exit']:report['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=180)
        (out/'commit-trace.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
