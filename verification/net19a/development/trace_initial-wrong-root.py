"""Diagnostic re-run only; adds context to existing fatal timing checks."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'tools'))
import run_keyboard_cpu as adapter
from run_rtl import BASE, fixtures, run


def main():
    out = ROOT / 'verification/net19a/development'
    with tempfile.TemporaryDirectory(prefix='isa1-keyboard-trace-') as tmp:
        work = Path(tmp)
        for lane in range(4):
            data = (BASE / f'control_lane{lane}.bin').read_bytes()
            (work / f'control_lane{lane}.hex').write_text(''.join(f'{x:02x}\n' for x in data))
        rows, _ = fixtures(True)
        (work / 'vectors.hex').write_text(''.join(''.join(f'{x:08x}\n' for x in row) for row in rows))
        refs = json.loads((ROOT / 'hardware/cpu_global/design.json').read_text())['reference_map']
        text = adapter.fixture((ROOT / 'sim/tests/tb_rtl_cpu.sv').read_text(), True, refs)
        bench = work / 'bench.sv'
        bench.write_text(text)
        source = ROOT / 'sim/net03/package_models.sv'
        model = source.read_text()
        old = 'if($realtime-data_changed<25)$fatal(1,"DFF data setup violation");'
        assert model.count(old) == 1
        model = model.replace(old, '''if($realtime-data_changed<25)begin
       $display("TRACE case=%0d opcode=%h PC=%h phase=%h io_select=%b key_ready=%b data=%b delta=%0.3f data_changed=%0.3f clk=%0.3f",tb_rtl_cpu.case_id,tb_rtl_cpu.vectors[tb_rtl_cpu.base+11],tb_rtl_cpu.pc,tb_rtl_cpu.memory.phase,tb_rtl_cpu.memory.io_select,tb_rtl_cpu.memory.key_ready,d,$realtime-data_changed,data_changed,$realtime);
       $fatal(1,"DFF data setup violation");
     end''')
        debug = work / 'debug-model.sv'
        debug.write_text(model)
        (out / 'debug-model.sv').write_text(model)
        models = [debug if n == 'sim/net03/package_models.sv' else ROOT / n for n in adapter.MODELS]
        cmd = ['iverilog', '-g2012', '-Wall', '-s', 'tb_rtl_cpu', '-Ptb_rtl_cpu.CASES=' + str(len(rows)), '-o', str(work / 'test.vvp'), *map(str, models), str(bench)]
        report = {'scope': 'Unchanged functional timing model with fatal-context logging; diagnostic run, not acceptance',
                  'source': {'path': source.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()},
                  'debug_model_sha256': hashlib.sha256(model.encode()).hexdigest(), 'compile': run(cmd, work)}
        if not report['compile']['exit']:
            report['execution'] = run(['vvp', str(work / 'test.vvp')], work, timeout=600)
        (out / 'initial-setup-trace.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
