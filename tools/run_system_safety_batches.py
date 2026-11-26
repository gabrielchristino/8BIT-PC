"""Complete delayed reset/PG cut coverage, partitioned across all 26 opcodes."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import run_system_vectors as adapter
from run_rtl import BASE,run

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net19a'


def main():
    names=adapter.MODELS
    sources=names+['tools/run_system_safety_batches.py','tools/run_system_vectors.py','tools/prepare_system_vectors.py','sim/tests/tb_rtl_safety.sv']
    refs=json.loads((ROOT/'hardware/cpu_global/design.json').read_text())['reference_map']
    text=adapter.fixture((ROOT/'sim/tests/tb_rtl_safety.sv').read_text(),True,refs)
    marker='for(oi=0;oi<26;oi=oi+1)begin';assert text.count(marker)==1
    intervals=[(i,min(i+4,26)) for i in range(0,26,4)]
    report={'date':'2026-11-26','scope':'All delayed CPU-edge reset/PG cuts of the legacy global-reset contract, partitioned across 26 opcodes, with native MMIO/keyboard/controller and binary raster reset boundaries. Not NET18 physical power sequencing, all-independent PVT or MTBF signoff',
            'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in sources],
            'iverilog':subprocess.run(['iverilog','-V'],capture_output=True,text=True).stdout.splitlines()[0],
            'runs':[],'covered_opcode_indices':[],'reset_power_cases':0,'failures':[],'production_released':False}
    def save():(OUT/'timed-safety-batches.json').write_text(json.dumps(report,indent=2)+'\n')
    def test(interval):
        lo,hi=interval
        with tempfile.TemporaryDirectory(prefix=f'isa1-system-safety-{lo:02d}-') as tmp:
            work=Path(tmp);bench=work/'bench.sv'
            data=text.replace(marker,f'for(oi={lo};oi<{hi};oi=oi+1)begin');bench.write_text(data)
            for lane in range(4):
                raw=(BASE/f'control_lane{lane}.bin').read_bytes();(work/f'control_lane{lane}.hex').write_text(''.join(f'{x:02x}\n' for x in raw))
            cmd=['iverilog','-g2012','-Wall','-s','tb_rtl_safety','-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names],str(bench)]
            row={'opcode_interval':[lo,hi],'adapted_bench_sha256':hashlib.sha256(data.encode()).hexdigest(),'compile':run(cmd,work)}
            if not row['compile']['exit']:
                try:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=1200)
                except subprocess.TimeoutExpired as exc:
                    def decoded(value):return value.decode(errors='replace') if isinstance(value,bytes) else value or ''
                    row['execution']={'exit':None,'timed_out':True,'stdout':decoded(exc.stdout),'stderr':decoded(exc.stderr),'timeout_seconds':1200}
            output=row.get('execution',{})
            match=re.search(r'reset_power_cases=(\d+) opcodes=26 failures=0',output.get('stdout',''))
            row['passed']=row['compile']['exit']==0 and output.get('exit')==0 and match is not None
            # "opcodes=26" is the legacy array length, NOT per-batch coverage.
            row['reset_power_cases']=int(match[1]) if match else 0
            return row
    OUT.mkdir(parents=True,exist_ok=True);save()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for future in concurrent.futures.as_completed([pool.submit(test,x) for x in intervals]):
            row=future.result();report['runs'].append(row);report['runs'].sort(key=lambda x:x['opcode_interval'])
            if row['passed']:
                report['covered_opcode_indices']+=list(range(*row['opcode_interval']));report['covered_opcode_indices'].sort();report['reset_power_cases']+=row['reset_power_cases']
            else:report['failures'].append(row['opcode_interval'])
            save();print(json.dumps({'interval':row['opcode_interval'],'passed':row['passed'],'cases':row['reset_power_cases'],'stdout':row.get('execution',{}).get('stdout','')}),flush=True)
    if report['covered_opcode_indices']!=list(range(26)):report['failures'].append('Incomplete/duplicate opcode coverage')
    save();return int(bool(report['failures']))


if __name__=='__main__':raise SystemExit(main())
