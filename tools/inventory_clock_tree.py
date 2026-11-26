"""Inventory actual clock pins and split direct FF feedback, before choosing XOs."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net22'


def main():
    names = ['cpu_global', 'video_system', 'system_access', 'keyboard_500', 'schmitt_reset']
    reports = []
    sources = [Path(__file__)]
    for name in names:
        folder = ROOT / 'hardware' / name
        paths = [folder / 'design.json', folder / 'package-functions.json']
        sources.extend(paths)
        parts = json.loads(paths[0].read_text())['parts']
        defs = json.loads(paths[1].read_text())
        clock_loads = {}
        buffer_edges = {}
        sequential = []
        for part in parts:
            functions = {defs[part['part']]['pins'][pin]['name']: net for pin, net in part['nets'].items()}
            clocks = {fn: net for fn, net in functions.items() if fn.startswith('CLK') and net not in ('GND', '+5V', None)}
            if clocks:
                sequential.append((part, functions, clocks))
            for function, net in clocks.items():
                clock_loads.setdefault(net, []).append({'reference': part['reference'], 'part': part['part'], 'function': function})
            if part['part'].endswith('125'):
                for index in range(4):
                    a, y, oe = (functions.get(prefix + str(index) + suffix) for prefix, suffix in [('A', ''), ('Y', ''), ('OE', '_N')])
                    if a is not None and y is not None and oe == 'GND':
                        buffer_edges.setdefault(a, []).append({'reference': part['reference'], 'part': part['part'], 'channel': index, 'output': y})
        routes = []

        def trace(net, path, seen):
            if net in seen:
                raise ValueError('Clock buffer cycle ' + name + '/' + net)
            for load in clock_loads.get(net, []):
                routes.append({'root': path[0] if path else net, 'clock_net': net, 'buffers': path[1:] if path else [], 'load': load})
            for edge in buffer_edges.get(net, []):
                trace(edge['output'], path + [edge], seen | {net})

        produced = {edge['output'] for edges in buffer_edges.values() for edge in edges}
        for root in sorted((set(buffer_edges) | set(clock_loads)) - produced - {'GND', '+5V'}):
            trace(root, [root], set())
        # Only direct D<-Q edges are enumerated here. Combinational feedback,
        # enables, clear and cascade paths need a subsequent timing graph.
        ff_bits = []
        for part, functions, clocks in sequential:
            if 'CLK0' in clocks or 'CLK1' in clocks:
                for index in range(2):
                    if f'CLK{index}' in clocks:
                        ff_bits.append({'reference': part['reference'], 'bit': index, 'clock': clocks[f'CLK{index}'],
                                        'd': functions.get(f'D{index}'), 'q': functions.get(f'Q{index}')})
        cross = []
        for source in ff_bits:
            for target in ff_bits:
                if source['q'] is not None and source['q'] == target['d'] and source['clock'] != target['clock']:
                    cross.append({'source': source, 'target': target, 'clock_skew_bound_ns': None,
                                  'status': 'OPEN: nominal equal buffer delays do not bound independent branch skew'})
        reports.append({'module': name, 'clock_load_nets': clock_loads, 'routes': routes,
                        'direct_ff_feedback_across_clock_branches': cross})
    OUT.mkdir(parents=True, exist_ok=True)
    report = {'date': '2026-11-26', 'base_git_commit': '03e224b48ec1657ea2adfd8330c9d3bf4d262255',
              'scope': 'Read-only clock pin/buffer topology audit. Direct D-Q split branches identified, not yet a reproduced timing failure or complete STA.',
              'modules': reports, 'sources': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],
              'all_clock_paths_qualified': False, 'physical_oscillators_selected': False, 'production_released': False}
    (OUT / 'clock-tree.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'modules': len(reports), 'clock_pin_routes': sum(len(row['routes']) for row in reports),
                      'direct_split_feedback_edges': sum(len(row['direct_ff_feedback_across_clock_branches']) for row in reports),
                      'all_clock_paths_qualified': False}))


if __name__ == '__main__':
    main()
