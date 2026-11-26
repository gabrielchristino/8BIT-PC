"""Physical SRAM pin checks through native reset distribution (qualified RAW)."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from run_rtl import run
from run_system_cpu import MODELS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net21'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = [p for p in MODELS if p != 'sim/net19a/isa1_memory_system.sv'] + [
        'hardware/schmitt_reset/schmitt_reset_netlist.sv', 'sim/net21/isa1_memory_schmitt.sv', 'sim/net21/tb_reset_memory.sv']
    sources = names + ['tools/run_schmitt_memory.py', 'tools/prepare_schmitt_checks.py', 'tools/build_schmitt_reset.py', 'verification/net21/native/schmitt_reset.xml']
    report = {'date': '2026-11-26', 'scope': 'Native SRAM pin address/WE ordering, fast CPU reset output, payload retention, stopped source clocks. Request master is a bench, not CPU instruction execution; scan report separately executes CPU. RAW/RC/binary resolution remain conditional, not analog/PVT/MTBF proof.',
              'iverilog': subprocess.run(['iverilog', '-V'], capture_output=True, text=True).stdout.splitlines()[0],
              'sources': [{'path': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest()} for p in sources],
              'runs': [], 'negative': [], 'failures': [], 'supervisor_output_load_qualified': False, 'production_released': False}
    with tempfile.TemporaryDirectory(prefix='isa1-reset-memory-') as tmp:
        work = Path(tmp)
        configs = [(p, 0, 0, a) for p in (0, 1) for a in (1000, 19000)] + [(1, 1, 0, 1000), (1, 0, 1, 1000)]
        for policy, bank, address, assertion in configs:
            command = ['iverilog', '-g2012', '-Wall', '-s', 'tb_reset_memory', f'-Ptb_reset_memory.POLICY={policy}',
                       f'-Ptb_reset_memory.FAULT_BANK={bank}', f'-Ptb_reset_memory.FAULT_ADDRESS={address}',
                       f'-Ptb_reset_memory.ASSERT_NS={assertion}',
                       '-o', str(work / 'test.vvp'), *[str(ROOT / p) for p in names]]
            row = {'policy': policy, 'assertion_ns': assertion, 'early_bank_fault': bank, 'address_fault': address, 'compile': run(command, work)}
            if row['compile']['exit'] == 0:
                row['execution'] = run(['vvp', str(work / 'test.vvp')], work, timeout=240)
            output = row.get('execution', {})
            expected = 'memory bank reset before physical WE inhibition' if bank else 'independent RAM pin address changed while WE low'
            row['passed'] = row['compile']['exit'] == 0 and (
                output.get('exit') not in (None, 0) and expected in output.get('stdout', '') if bank or address else
                output.get('exit') == 0 and 'active_write_cuts=12 stopped_clocks=2' in output.get('stdout', '') and 'failures=0' in output['stdout'])
            report['negative' if bank or address else 'runs'].append(row)
            if not row['passed']:
                report['failures'].append([policy, bank, address])
            (OUT / 'reset-memory-results.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps(row), flush=True)
            if not row['passed']:
                return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
