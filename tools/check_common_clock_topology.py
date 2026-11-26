"""Check native video clock/pin contracts, separately from HDL behavior."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inspect(design, definitions):
    parts = {p['reference']: p for p in design['parts']}
    functions = {ref: {definitions[p['part']]['pins'][pin]['name']: net
                      for pin, net in p['nets'].items()} for ref, p in parts.items()}
    expected = {'BUF_2_2': [('U8', 'CLK0'), ('U8', 'CLK1'), ('U9', 'CLK'), ('U11', 'CLK0')],
                'BUF_2_0': [('U1', 'CLK'), ('U2', 'CLK'), ('U11', 'CLK1'), ('U12', 'CLK1')],
                'BUF_2_1': [('U3', 'CLK'), ('U4', 'CLK'), ('U5', 'CLK')],
                'CAPTURE_CLOCK': [('U6', 'CLK'), ('U7', 'CLK'), ('U12', 'CLK0')]}
    errors = []
    for net, wanted in expected.items():
        actual = [(ref, fn) for ref, pins in functions.items() for fn, wire in pins.items()
                  if fn.startswith('CLK') and wire == net]
        if sorted(actual) != sorted(wanted):
            errors.append('clock group ' + net)
    contracts = [('U11', 'CLR0_N', '+5V'), ('U9', 'B', '+5V'), ('U9', 'A', 'PHASE_SERIAL'),
                 ('U9', 'CLR_N', 'BUF_1_1'), ('U10', 'Y', 'PHASE_SERIAL'),
                 ('U34', 'A3', 'P3'), ('U34', 'Y3', 'CAPTURE_CLOCK'),
                 ('U36', 'CLK0', 'P3'), ('U36', 'CLK1', 'P3'), ('U36', 'Q0', 'H_END_REG'),
                 ('U36', 'QB1', 'V_LOAD_REGISTERED_N')]
    contracts += [('U9', f'Q{i}', f'P{i}') for i in range(4)]
    contracts += [('U10', name, f'P{i}') for i, name in enumerate(['A', 'B', 'C'])]
    contracts += [(ref, fn, net) for ref in ['U3', 'U4', 'U5']
                  for fn, net in [('ENP', 'H_END_REG'), ('LOAD_N', 'V_LOAD_REGISTERED_N')]]
    for ref, fn, net in contracts:
        if functions[ref][fn] != net:
            errors.append(f'pin contract {ref}.{fn}')
    loads = {}
    for ref, part in parts.items():
        for pin, net in part['nets'].items():
            if definitions[part['part']]['pins'][pin]['type'] == 'input' and net not in (None, '+5V', 'GND'):
                loads.setdefault(net, []).append(f'{ref}.{pin}')
    for net in list(expected) + ['P3']:
        if len(loads[net]) > 4:
            errors.append('load budget ' + net)
    return errors, {net: {'input_pins': loads[net], 'conditional_capacitance_pf': 10 + 10 * len(loads[net])}
                    for net in list(expected) + ['P3']}


def main():
    names = ['hardware/video_common_clock/design.json', 'hardware/video_common_clock/package-functions.json',
             'hardware/video_system/design.json', 'tools/check_common_clock_topology.py']
    design, definitions, ancestor = [json.loads((ROOT / n).read_text()) for n in names[:3]]
    errors, groups = inspect(design, definitions)
    before = {p['reference']: p for p in ancestor['parts']}
    after = {p['reference']: p for p in design['parts']}
    changed = sorted(ref for ref in before if before[ref] != after[ref])
    allowed = {'U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U9', 'U10', 'U11', 'U12', 'U34'}
    # The repurposed RUN gate's package may be among U13..U33.
    gate_changes = [ref for ref in changed if ref not in allowed]
    if len(gate_changes) != 1 or after[gate_changes[0]]['part'] != 'SN74AHC08':
        errors.append('unexpected changed ancestor packages')
    if set(after) - set(before) != {'U36', 'C36'}:
        errors.append('unexpected added packages')
    negatives = []
    for ref, fn, net in [('U11', 'CLK1', 'BUF_2_1'), ('U3', 'ENP', 'G32'), ('U11', 'CLR0_N', 'BUF_1_1')]:
        mutant = copy.deepcopy(design)
        part = next(p for p in mutant['parts'] if p['reference'] == ref)
        pin = next(pin for pin, spec in definitions[part['part']]['pins'].items() if spec['name'] == fn)
        part['nets'][pin] = net
        rejected, _ = inspect(mutant, definitions)
        negatives.append({'mutation': [ref, fn, net], 'expected_rejection': True, 'reasons': rejected, 'passed': bool(rejected)})
    if not all(n['passed'] for n in negatives):
        errors.append('negative not detected')
    report = {'date': '2026-11-26', 'sources': [{'path': n, 'sha256': hashlib.sha256((ROOT / n).read_bytes()).hexdigest()} for n in names],
              'changed_ancestor_parts': changed, 'added_parts': ['U36', 'C36'], 'clock_loads': groups,
              'negatives': negatives, 'failures': errors,
              'scope': 'Native clock/reset/enable pin contracts and 10pF per input plus10pF trace budget. No PCB extraction, whole-tree STA or physical qualification.',
              'production_released': False}
    (ROOT / 'verification/net22/clock-topology.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
