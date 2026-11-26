"""Conditional RESET pullup/Schmitt RC envelope; not a vendor supervisor model."""
import hashlib
import itertools
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net21'


def main():
    folder = OUT / 'reset-line'
    folder.mkdir(parents=True, exist_ok=True)
    report = {'date': '2026-11-26', 'scope': 'Conditional pullup/trace/input-C RC model after supervisor sink command. Ron400ohm is an engineering proxy from DC VOL=.4V/1mA, NOT a guaranteed transient output impedance or vendor analog model. Leakage across intermediate VI is a qualification budget.',
        'assumptions': {'supply_v': [4.5, 5.5], 'pullup_ohm': 100000, 'pullup_tolerance': .01,
            'receiver_leak_abs_a': 1e-6, 'supervisor_off_leak_max_a': .3e-6,
            'sink_ron_proxy_ohm': 400, 'input_cap_max_at_5v_pf': 10,
            'candidate_routing_budget_pf': 10, 'maximum_test_load_pf': 50,
            'schmitt_rising_threshold_global_max_v': 3.85, 'schmitt_falling_threshold_global_min_v': 1.35},
        'sources': [{'path': name, 'sha256': hashlib.sha256((ROOT / name).read_bytes()).hexdigest()} for name in
                    ['tools/check_schmitt_interface.py', 'references/net20/tps3808.pdf', 'references/ti/sn74ahc14.pdf']],
        'ngspice': subprocess.run(['ngspice', '--version'], capture_output=True, text=True).stdout,
        'runs': [], 'negative': [], 'failures': [], 'production_released': False}
    specs = list(itertools.product((4.5, 5.5), (.99, 1.01), (-1e-6, 1e-6), (10, 20, 50)))
    specs.append((4.5, 10, 1e-6, 20))  # 1Mohm loses high-level margin under the same leakage budget.
    for index, (supply, ratio, leak, cap) in enumerate(specs):
        negative = index == len(specs) - 1
        resistance = 100000 * ratio
        deck = f'''NET21 conditional supervisor output RC {index}
VSUP vdd 0 {supply}
RPULL vdd raw {resistance}
CLOAD raw 0 {cap}p
IINPUT raw 0 {leak}
IOFF raw 0 0.3u
VCONTROL control 0 PWL(0 0 19.999u 0 20u 1 99.999u 1 100u 0)
SSINK raw 0 control 0 SINK
.model SINK SW(Ron=400 Roff=1e15 Vt=0.5 Vh=0)
.tran .002u .2m
.measure tran high FIND V(raw) AT=190u
.measure tran low FIND V(raw) AT=90u
.measure tran fall WHEN V(raw)=1.35 FALL=1
'''
        if not negative:
            deck += '.measure tran rise WHEN V(raw)=3.85 RISE=1\n'
        deck += '.end\n'
        path = folder / f'line-{index:03d}.cir'
        path.write_text(deck)
        command = ['ngspice', '-b', str(path)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        path.with_suffix('.log').write_text(output)
        values = {key: float(value) for key, value in re.findall(r'^(high|low|fall|rise)\s*=\s*([-+\d.eE]+)', output, re.M)}
        complete = result.returncode == 0 and len(values) == (3 if negative else 4)
        levels = complete and values['high'] > 3.85 and values['low'] < 1.35
        expected_high = supply - resistance * (leak + .3e-6)
        residual = complete and abs(values['high'] - expected_high) < .0001
        passed = complete and residual and (not levels if negative else levels)
        row = {'index': index, 'supply_v': supply, 'pullup_ohm': resistance, 'receiver_leak_a': leak,
               'cap_pf': cap, 'command': command, 'exit': result.returncode, 'deck': path.relative_to(ROOT).as_posix(),
               'log': path.with_suffix('.log').relative_to(ROOT).as_posix(), 'measures': values,
               'analytic_high_v': expected_high, 'passed': passed}
        report['negative' if negative else 'runs'].append(row)
        if not passed:
            report['failures'].append(index)
    report['summary'] = {'cases': len(report['runs']), 'minimum_high_v': min(r['measures'].get('high', 0) for r in report['runs']),
                         'maximum_low_v': max(r['measures'].get('low', 100) for r in report['runs']),
                         'max_conditional_fall_after_sink_s': max(r['measures'].get('fall', 1) - 20e-6 for r in report['runs']),
                         'max_conditional_rise_after_release_s': max(r['measures'].get('rise', 1) - 100e-6 for r in report['runs'])}
    (OUT / 'reset-line-results.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'summary': report['summary'], 'negative_cases': len(report['negative']), 'failures': report['failures']}))
    return int(bool(report['failures']))


if __name__ == '__main__':
    raise SystemExit(main())
