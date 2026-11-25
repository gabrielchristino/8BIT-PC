"""Same delayed safety cuts split across opcode intervals, with full coverage.

No safety cuts are skipped; separate temporary simulations avoid per-process
timeout loss. Binary resolution at the external reset boundary remains an
explicit verification assumption, not analog metastability approval.
"""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import tempfile
import run_video_cpu_async as adapter
from run_rtl import run,BASE

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net14c'


def main():
    names=['sim/hdl/hc_models.sv','sim/net02/package_models.sv','sim/net03/package_models.sv','sim/net04/package_models.sv',
      'hardware/cpu_global/cpu_global_netlist.sv','hardware/memory_decode/memory_decode_netlist.sv',
      'hardware/memory_bus_access/memory_access_netlist.sv','sim/net13/memory_devices.sv','hardware/memory_bus/memory_bus_netlist.sv',
      'sim/net14c/package_models_async.sv','sim/net14c/video_raster_async_netlist.sv','sim/net14c/isa1_memory_video.sv']
    sources=names+['sim/tests/tb_rtl_safety.sv','tools/run_video_safety_batches.py','tools/run_video_cpu_async.py','tools/make_video_cpu.py','tools/make_video_reset_model.py']
    intervals=[(i,min(i+4,26)) for i in range(0,26,4)]
    refs=json.loads((ROOT/'hardware/cpu_global/design.json').read_text())['reference_map']
    text=adapter.fixture((ROOT/'sim/tests/tb_rtl_safety.sv').read_text(),True,refs)
    marker='for(oi=0;oi<26;oi=oi+1)begin';assert text.count(marker)==1
    report={'date':'2026-11-25','iteration':'NET-14C','python':platform.python_version(),
      'iverilog':subprocess.run(['iverilog','-V'],capture_output=True,text=True).stdout.splitlines()[0],
      'scope':'All opcode/reset/PG/CPU-edge cuts of adapted delayed safety bench, partitioned by opcode index; bounded external reset resolution, no analog/PVT/MTBF approval',
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in sources],
      'intervals':[list(x) for x in intervals],'runs':[],'failures':[],'covered_opcode_indices':[],'reset_power_cases':0,'analog_metastability_approved':False}
    def save():(OUT/'timed-safety-batches.json').write_text(json.dumps(report,indent=2)+'\n')
    def test(interval):
        lo,hi=interval
        with tempfile.TemporaryDirectory(prefix=f'isa1-video-safety-{lo:02d}-') as tmp:
            work=Path(tmp);bench=work/'tb_rtl_safety.sv'
            data=text.replace(marker,f'for(oi={lo};oi<{hi};oi=oi+1)begin')
            bench.write_text(data)
            for lane in range(4):
                raw=(BASE/f'control_lane{lane}.bin').read_bytes()
                (work/f'control_lane{lane}.hex').write_text(''.join(f'{x:02x}\n' for x in raw))
            cmd=['iverilog','-g2012','-Wall','-s','tb_rtl_safety','-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names],str(bench)]
            row={'opcode_interval':[lo,hi],'adapted_bench_sha256':hashlib.sha256(data.encode()).hexdigest(),'compile':run(cmd,work)}
            if not row['compile']['exit']:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=1200)
            match=re.search(r'reset_power_cases=(\d+) opcodes=26 failures=0',row.get('execution',{}).get('stdout',''))
            # The preserved bench prints its fixed ops-array length, 26; the
            # actual loop interval is recorded separately, never 26 per batch.
            row['passed']=row['compile']['exit']==0 and row.get('execution',{}).get('exit')==0 and match is not None
            row['reset_power_cases']=int(match.group(1)) if match else 0
            return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        pending=[pool.submit(test,x) for x in intervals]
        for future in concurrent.futures.as_completed(pending):
            row=future.result();report['runs'].append(row);report['runs'].sort(key=lambda x:x['opcode_interval'])
            if row['passed']:
                report['covered_opcode_indices']+=list(range(*row['opcode_interval']))
                report['covered_opcode_indices'].sort();report['reset_power_cases']+=row['reset_power_cases']
            else:report['failures'].append(row['opcode_interval'])
            save();print(json.dumps(row),flush=True)
    if report['covered_opcode_indices']!=list(range(26)):report['failures'].append('Incomplete/duplicate opcode coverage')
    save();return int(bool(report['failures']))


if __name__=='__main__':raise SystemExit(main())
