"""NET-14A pre-design contract: selected timing budgets and two-frame simulation.

Not a KiCad netlist for the raster, oscillator or capture register; those remain
open. Connects the executable phase contract to preserved NET-13 pin netlists.
"""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import tempfile
from run_rtl import run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net14a'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = ['sim/hdl/hc_models.sv', 'sim/net03/package_models.sv',
             'sim/net04/package_models.sv', 'sim/net13/memory_devices.sv',
             'hardware/memory_decode/memory_decode_netlist.sv',
             'hardware/memory_bus_access/memory_access_netlist.sv',
             'hardware/memory_bus/memory_bus_netlist.sv',
             'sim/net14a/video_contract.sv', 'sim/net14a/tb_video_contract.sv']
    sources = names + ['tools/run_video_contract.py', 'tools/run_rtl.py',
                        'references/ti/sn74lv163a.pdf', 'references/ti/sn74hct574.pdf',
                        'references/ti/sn74hc74.pdf', 'docs/engineering/NET13.md']
    period = 1e9 / 25175000
    pixel = 4 * period
    # SN74LV163A SCLS405G 4.11: 11.5 ns CLK->Q, 4.5..5.5 V,
    # CL=50 pF, recommended temperature range. Memory path from NET-13.
    # HCT574 SCLS177H 4.5: setup 25 ns, hold 5 ns at 4.5 V.
    # 5 ns is a proposed combined uncertainty budget, NOT extracted skew.
    rows = []
    for phase in (2, 3):
        for cq in (11.5, 20, 30):
            margin = phase * period - (cq + 12 + 20 + 42 + 25 + 5)
            hold = pixel - phase * period - 5 - 5  # zero contamination minimum
            rows.append({'capture_phase': phase, 'counter_q_ns': cq,
                         'setup_margin_ns': margin, 'hold_margin_ns': hold,
                         'conditional_budget_passed': margin >= 0 and hold >= 0})
    # HC74 at 4.5V -40..85C: fclock <=25 MHz, CLK high/low >=20 ns.
    # HCT574 at 4.5V: fclock <=24 MHz, pulse >=20 ns. Neither is
    # qualified to clock directly at 25.175 MHz. A divided capture strobe
    # still needs a hazard-free physical implementation and pulse analysis.
    clock_checks = [
        {'candidate': 'SN74HC74 direct master', 'frequency_limit_mhz': 25,
         'frequency_passed': 25.175 <= 25, 'pulse_passed': period / 2 >= 20},
        {'candidate': 'SN74HCT574 direct master', 'frequency_limit_mhz': 24,
         'frequency_passed': 25.175 <= 24, 'pulse_passed': period / 2 >= 20},
        {'candidate': 'SN74HCT574 divided capture, proposed one-master-period pulse',
         'frequency_mhz': 25.175 / 4, 'frequency_passed': 25.175 / 4 <= 24,
         'pulse_passed': period >= 20, 'physical_implementation_approved': False}]
    report = {'iteration': 'NET-14A', 'date': '2026-11-25',
              'base_git_commit': '9fae1298a3cd74844d294464bfdd0541241815af',
              'scope': 'Pre-design phase/raster contract attached to NET-13 component models; no raster KiCad, full PVT, oscillator/DAC or fabrication approval',
              'python': platform.python_version(),
              'iverilog': subprocess.run(['iverilog', '-V'], capture_output=True, text=True).stdout.splitlines()[0],
              'sources': [{'path': n, 'sha256': hashlib.sha256((ROOT / n).read_bytes()).hexdigest()} for n in sources],
              'timing': {'master_hz': 25175000, 'master_period_ns': period,
                         'logical_pixel_period_ns': pixel, 'line_hz': 25175000 / 800,
                         'frame_hz': 25175000 / (800 * 525),
                         'uncertainty_budget_ns': 5, 'budget_is_measured': False,
                         'rows': rows, 'clock_checks': clock_checks},
              'runs': [], 'negative': [], 'failures': [], 'production_released': False}

    def save():
        (OUT / 'results.json').write_text(json.dumps(report, indent=2) + '\n')

    with tempfile.TemporaryDirectory(prefix='isa1-video-contract-') as tmp:
        work = Path(tmp)
        for phase, cq, inject_hold, expected in [(3, 11.5, 0, None),
                                                (2, 11.5, 0, 'pixel data/address mismatch'),
                                                (3, 25, 0, 'pixel setup violation'),
                                                (3, 11.5, 1, 'pixel hold violation')]:
            cmd = ['iverilog', '-g2012', '-Wall', '-s', 'tb_video_contract',
                   f'-Ptb_video_contract.CAPTURE_PHASE={phase}', f'-Ptb_video_contract.COUNTER_Q={cq}',
                   f'-Ptb_video_contract.INJECT_HOLD={inject_hold}',
                   '-o', str(work / 'test.vvp'), *[str(ROOT / n) for n in names]]
            row = {'capture_phase': phase, 'counter_q_ns': cq, 'injected_hold_fault': bool(inject_hold), 'compile': run(cmd, work)}
            if row['compile']['exit'] == 0:
                row['execution'] = run(['vvp', str(work / 'test.vvp')], work, timeout=300)
            if expected is None:
                row['passed'] = row['compile']['exit'] == 0 and row.get('execution', {}).get('exit') == 0 and 'frames=2 samples=210000 visible=153600' in row['execution']['stdout']
                report['runs'].append(row)
            else:
                row['expected_rejection'] = True
                row['passed'] = row['compile']['exit'] == 0 and row.get('execution', {}).get('exit', 0) != 0 and expected in row['execution']['stdout']
                report['negative'].append(row)
            if not row['passed']:
                report['failures'].append(f'phase={phase}, cq={cq}')
            save()
            print(json.dumps(row), flush=True)
            if report['failures']:
                return 1
    save()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
