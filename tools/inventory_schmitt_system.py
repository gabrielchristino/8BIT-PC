"""Inventory candidate packages; do not infer board current from a part count."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    modules = ['cpu_global', 'memory_decode', 'system_access', 'memory_bus', 'video_system', 'keyboard_500', 'schmitt_reset']
    totals = Counter()
    sources = []
    records = []
    for name in modules:
        path = ROOT / 'hardware' / name / 'design.json'
        parts = json.loads(path.read_text())['parts']
        counts = Counter(p['part'] for p in parts)
        totals.update(counts)
        records.append({'module': name, 'counts': dict(counts), 'components': len(parts)})
        sources.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    sources.append({'path': 'tools/inventory_schmitt_system.py', 'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    passive = {'R', 'C', 'J8'}
    ics = sum(n for name, n in totals.items() if name not in passive)
    assert ics == 458 and totals['TPS3808G01DBVR'] == 1 and totals['C'] == 460
    report = {'date': '2026-11-26', 'modules': records, 'totals': dict(totals), 'candidate_union_ic_count': ics,
              'sources': sources, 'global_board_integrated': False,
              'power_budget': [{'family': name, 'count': count, 'board_icc_upper_bound_a': None,
                               'dynamic_current_upper_bound_a': None} for name, count in sorted(totals.items()) if name not in passive],
              'notes': ['Two more clock/reset buffer packages than NET19. Same eight packages as NET20; one supervisor replaced and spare gates reused.',
                        'USB-C/regulator/isolation/clock-source/DAC hardware not included. 1.5A is a conditional budget, not derived current.'],
              'production_released': False}
    (ROOT / 'verification/net21/load-inventory.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'candidate_ics': ics, 'families_with_open_board_current': len(report['power_budget']), 'production_released': False}))


if __name__ == '__main__':
    main()
