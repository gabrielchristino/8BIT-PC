"""Join source consumer pins across reset/video/CPU partial sheets."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def functions(design, defs):
    return {p['reference']: {defs[p['part']]['pins'][pin]['name']: net for pin, net in p['nets'].items()}
            for p in design['parts']}


def inspect(design, defs, video, video_defs):
    ff = functions(design, defs)
    errors = []
    if ff['X1']['ENABLE'] != '+5V' or ff['X2']['ENABLE'] != '+5V':
        errors.append('Oscillator enable must remain VDD, never RAW-gated')
    if (ff['U1']['A0'], ff['U1']['OE0_N'], ff['U1']['Y0']) != ('CPU_OSC', 'GND', 'CPU_CLK'):
        errors.append('Reuse CPU prebuffer contract')
    loads = {}
    for design_name, data, specs in [('reset', design, defs), ('video', video, video_defs)]:
        for p in data['parts']:
            for pin, net in p['nets'].items():
                if specs[p['part']]['pins'][pin]['type'] == 'input':
                    loads.setdefault(net, []).append(f'{design_name}/{p["reference"]}.{pin}')
    rows = []
    for net, max_cl, trace in [('CPU_OSC', 15, 5), ('MASTER', 15, 5), ('CPU_CLK', 50, 10)]:
        # Same signal names occur only for the intentionally joined nets.
        pins = loads.get(net, [])
        total = 10 * len(pins) + trace
        rows.append({'net': net, 'input_pins': pins, 'input_budget_pf_each': 10,
                     'routing_budget_pf': trace, 'total_budget_pf': total,
                     'selected_source_cl_pf': max_cl, 'budget_fits': total <= max_cl})
        if not pins or total > max_cl:
            errors.append('Load budget ' + net)
    return errors, rows


def main():
    names = ['hardware/clocked_reset/design.json', 'hardware/clocked_reset/package-functions.json',
             'hardware/video_common_clock/design.json', 'hardware/video_common_clock/package-functions.json']
    design, defs, video, video_defs = [json.loads((ROOT / n).read_text()) for n in names]
    errors, rows = inspect(design, defs, video, video_defs)
    negatives = []
    for mode in ['bypass_cpu_prebuffer', 'raw_gated_enable']:
        mutant = copy.deepcopy(design)
        if mode == 'bypass_cpu_prebuffer':
            part = next(p for p in mutant['parts'] if p['reference'] == 'U7')
            part['nets']['9'] = part['nets']['12'] = 'CPU_OSC'
        else:
            next(p for p in mutant['parts'] if p['reference'] == 'X2')['nets']['1'] = 'RAW_SAFE_N'
        rejected, _ = inspect(mutant, defs, video, video_defs)
        negatives.append({'mutation': mode, 'expected_rejection': True, 'reasons': rejected, 'passed': bool(rejected)})
        if not rejected:
            errors.append('Negative missed ' + mode)
    report = {'date': '2026-11-26', 'sources': [{'path': n, 'sha256': hashlib.sha256((ROOT / n).read_bytes()).hexdigest()} for n in names +
                   ['tools/check_clock_source_loads.py', 'references/net22/abracon-ach.pdf', 'references/ti/sn74ahc125.pdf']],
              'nets': rows, 'negative': negatives, 'failures': errors,
              'scope': 'Joined source consumer pin budgets: AHC125 Ci max10pF at5V plus explicit trace allowance. Not extracted capacitance or all-VDD/temperature/transition qualification. Standard ACH15pF timing configuration, full ordering PN open.',
              'oscillator_output_load_qualified': False, 'production_released': False}
    (ROOT / 'verification/net23/clock-loads.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
