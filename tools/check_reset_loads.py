"""Count actual joined reset/clock input pins; explicit CL budgets, not PVT."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net20'


def main():
    bindings = {
        'cpu_global': {'CLK': 'CPU_CORE_CLK', 'RESET_N': 'CPU_RESET_N'},
        'system_access': {'CLK': 'ACCESS_CLK', 'RESET_N': 'BANK_MEMORY_N'},
        'keyboard_500': {'CLK': 'KEYBOARD_CLK', 'BANK_RESET_N': 'BANK_KEYBOARD_N', 'ACCESS_SAFE': 'SAFE_KEYBOARD'},
        'memory_bus': {'RESET_N': 'BANK_MEMORY_N', 'POWER_GOOD': 'SAFE_MEMORY'},
        'memory_decode': {'SAFE': 'BANK_DECODE_N'},
    }
    files = [Path(__file__)]
    joined = {}
    for block, nets in {'system_reset': {}, **bindings}.items():
        folder = ROOT / 'hardware' / block
        paths = [folder / 'design.json', folder / 'package-functions.json']
        files.extend(paths)
        parts = json.loads(paths[0].read_text())['parts']
        defs = json.loads(paths[1].read_text())
        for part in parts:
            if part['part'] in ('R', 'C', 'TPS3703F6050DSER'):
                continue
            for pin, net in part['nets'].items():
                if net is None or net in ('GND', '+5V'):
                    continue
                if block != 'system_reset' and net not in nets:
                    continue
                spec = defs[part['part']]['pins'][pin]
                if spec['type'] != 'input':
                    continue
                global_net = nets.get(net, net)
                joined.setdefault(global_net, []).append({'block': block, 'reference': part['reference'], 'pin': pin,
                                                        'function': spec['name'], 'part': part['part']})
    selected = ['CPU_RESET_N', 'CPU_CORE_CLK', 'ACCESS_CLK', 'KEYBOARD_CLK', 'BANK_RESET_N',
                'BANK_MEMORY_N', 'BANK_KEYBOARD_N', 'BANK_DECODE_N', 'SAFE_MEMORY', 'SAFE_KEYBOARD',
                'ACCESS_SAFE', 'BACKEND_ROOT', 'BANK_RESET_CLK', 'CPU_RESET_CLK']
    rows = [{'net': net, 'inputs': joined.get(net, []), 'input_count': len(joined.get(net, [])),
             'input_capacitance_budget_pf': 10 * len(joined.get(net, [])), 'routing_budget_pf': 10,
             'cl_budget_pf': 10 * len(joined.get(net, [])) + 10,
             'within_50pf_budget': 10 * len(joined.get(net, [])) + 10 <= 50} for net in selected]
    if any(row['input_count'] == 0 for row in rows):
        raise ValueError('Binding missed all inputs on a selected distribution net')
    # Mandatory negative: the unbuffered shared clock would drive three
    # controller + three keyboard + two reset clock pins (80pF budget).
    negative = {'name': 'one_backend_net_without_distribution', 'input_count': 8,
                'cl_budget_pf': 8 * 10 + 10, 'within_50pf_budget': False}
    report = {'date': '2026-11-26', 'scope': 'Actual selected joined pin fanout with explicit 10pF/input and 10pF/routing budgets. Not extracted PCB capacitance or a per-family PVT/current/clock-skew qualification.',
              'bindings': bindings, 'nets': rows, 'negative': negative,
              'supervisor_interface': {'part': 'TPS3703F6050DSER', 'buffer': 'SN74AHC125', 'input_max_pf': 10,
                  'supervisor_timing_test_cl_pf': 10, 'routing_allowance_pf': 0,
                  'example_routing_budget_pf': 2, 'example_total_pf': 12,
                  'guaranteed_test_load_budget_closed': False,
                  'meaning': 'Even one max-Ci AHC125 consumes all 10pF. NET18/20 hold-up cannot be promoted to a guaranteed physical shutdown bound. Digital RAW tests remain independent.'},
              'sources': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
              'failures': [row['net'] for row in rows if not row['within_50pf_budget']],
              'global_clock_skew_qualified': False, 'production_released': False}
    (OUT / 'load-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'selected_nets': len(rows), 'max_input_count': max(row['input_count'] for row in rows),
                      'supervisor_interface_qualified': False, 'failures': report['failures']}))
    return int(bool(report['failures']))


if __name__ == '__main__':
    raise SystemExit(main())
