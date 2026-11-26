"""Conditional edge-arrival budgets, not full STA or oscillator qualification."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    # ACH option C includes initial/temperature only; jitter/aging/supply/load
    # frequency contributions are not provided here and are explicitly open.
    period = 1e9 / (25175000 * (1 + 50e-6))
    rows = [
        ('MASTER high/low after one buffer', .475 * period - (8.5 - 1), 5),
        ('Phase clock high after shift and buffer', period - (12.5 - 1) - (8.5 - 1), 5),
        ('Shift serial setup: CQ plus NOR plus setup', period - 12.5 - 3.6, 4.5),
        ('Shift serial hold: minimum CQ plus NOR', 1 + 1, .5),
        ('Backend D hold on common MASTER branch', 1, .5),
        ('Vertical enable/load before next P0 branch', period + 1 + 1 - 12.5 - 10.5, 6),
        ('Horizontal enable hold: RUN CQ plus AND', 1 + 1, 1),
    ]
    cases = [{'path': label, 'available_ns': available, 'required_ns': required,
              'conditional_margin_ns': available - required, 'arithmetic_passed': available >= required}
             for label, available, required in rows]
    names = ['tools/check_common_clock_budget.py', 'references/net22/abracon-ach.pdf',
             'references/net22/sn74ahc164.pdf', 'references/net22/sn74lvc1g27.pdf',
             'references/ti/sn74ahc125.pdf', 'references/ti/sn74ahc74.pdf', 'references/ti/sn74lv161a.pdf',
             'references/ti/sn74ahc08.pdf', 'verification/net22/research/sn74ahc08-budget.txt',
             'hardware/video_common_clock/design.json', 'sim/net14c/package_models_async.sv']
    report = {'date': '2026-11-26', 'sources': [{'path': n, 'sha256': hashlib.sha256((ROOT / n).read_bytes()).hexdigest()} for n in names],
              'period_at_initial_temperature_plus50ppm_ns': period, 'cases': cases,
              'reference_extraction': {'source': 'references/ti/sn74ahc08.pdf', 'revision': 'SCLS236L February2024',
                                       'transformation': 'pdftotext -layout; PDF bytes unchanged',
                                       'command': ['pdftotext', '-layout', 'references/ti/sn74ahc08.pdf', 'verification/net22/research/sn74ahc08-budget.txt']},
              'assumptions': ['ACH duty option T47.5/52.5%, option C50ppm, loading option50pF; configuration only, no full PN approved',
                              'Zero cycle jitter and zero extracted within-branch PCB skew are assumptions, not guarantees',
                              'Digital timing-reference edges, not analog slew/threshold conversion or ringing model',
                              'Selected datasheet/model limits at5V+/-0.5V,CL50pF,-40..85C',
                              'Clock-buffer rise/fall can independently span1..8.5ns; shift output edges1..12.5ns',
                              'Other gate/counter/data/cascade/reset paths are not all included in this selected-path calculation'],
              'failures': [c['path'] for c in cases if not c['arithmetic_passed']],
              'all_clock_paths_qualified': False, 'oscillator_qualified': False, 'production_released': False}
    (ROOT / 'verification/net22/clock-budget.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'conditional_paths': len(cases), 'minimum_margin_ns': min(c['conditional_margin_ns'] for c in cases),
                      'failures': report['failures'], 'all_clock_paths_qualified': False}))
    return int(bool(report['failures']))


if __name__ == '__main__':
    raise SystemExit(main())
