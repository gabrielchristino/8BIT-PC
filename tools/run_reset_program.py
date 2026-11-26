"""Execute the full boot/frame regression through the new reset domains."""
import hashlib
import json
from pathlib import Path
import sys
import run_system_cpu as base

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / 'verification/net20/program'
    folder.mkdir(parents=True, exist_ok=True)
    base.OUT = folder
    base.MODELS = [p for p in base.MODELS if p != 'sim/net19a/isa1_memory_system.sv'] + [
        'hardware/system_reset/system_reset_netlist.sv', 'sim/net20/isa1_memory_reset.sv']
    original = base.fixture

    def fixture(text, timed, refs):
        text = original(text, timed, refs)
        old = 'dut(clk,reset_n,power_good,run,boot'
        if text.count(old) != 1:
            raise ValueError('Unexpected program CPU reset wiring')
        text = text.replace(old, "dut(memory.cpu_core_clk,memory.cpu_reset_n,1'b1,run,boot")
        return text

    base.fixture = fixture
    sys.argv = [sys.argv[0], '--bench', 'program']
    result = base.main()
    report_path = folder / 'system-program-ideal.json'
    report = json.loads(report_path.read_text())
    report.update(scope='Full ideal boot/frame with initially unknown SRAM through native reset domains. Analog supervisor, physical clocks/PVT/skew and timed full program not qualified.',
                  supervisor_output_load_qualified=False)
    for name in ['tools/run_reset_program.py', 'tools/make_reset_system.py', 'tools/build_system_reset.py', 'verification/net20/native/system_reset.xml']:
        report['sources'].append({'path': name, 'sha256': hashlib.sha256((ROOT / name).read_bytes()).hexdigest()})
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    return result


if __name__ == '__main__':
    raise SystemExit(main())
