"""Conditional DC window, separate from regulator transient qualification."""
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net18'


def window(top, feedback):
    trips, releases, rails = [], [], []
    for rt, rb, accuracy, sense in itertools.product((-.001, .001), (-.001, .001), (-.01, .01), (-10e-6, 10e-6)):
        rtop, rbottom = top * (1 + rt), 100 * (1 + rb)
        trip = .47 * (1 + accuracy) * (1 + rtop / rbottom) + sense * rtop
        trips.append(trip)
        # Conservative bound: multiply the entire positive trip by max hyst.
        releases.append(trip * 1.007)
    for rt, rb, reference, leak in itertools.product((-.001, .001), (-.001, .001), (-.01, .01), (-100e-9, 100e-9)):
        rtop, rbottom = feedback * (1 + rt), 10000 * (1 + rb)
        value = .8 * (1 + reference) * (1 + rtop / rbottom) + leak * rtop
        rails.append(value)
    minimum = min(rails) - 1.5 * (.045 + .010) - .020
    maximum = max(rails) + .020
    qualified = min(trips) * .95
    hold_bank = qualified - .02 * (1.5 + .5) - (1.5 * 50.2e-6 + 50e-6) / .0044
    return {'monitor_divider_top_ohm': top, 'feedback_top_ohm': feedback,
            'monitor_corners': len(trips), 'regulator_corners': len(rails),
            'nominal_regulator_target_v': .8 * (1 + feedback / 10000),
            'trip_min_v': min(trips), 'release_max_v': max(releases),
            'qualified_detection_voltage_v': qualified,
            'rail_min_after_load_and_20mv_budget_v': minimum,
            'rail_max_with_20mv_budget_v': maximum,
            'release_margin_v': minimum - max(releases),
            'hold_bank_lower_v': hold_bank,
            'passed': minimum > max(releases) and maximum < 5.5 and hold_bank > 4.5}


def main():
    chosen = window(950, 55400)
    negative = [window(950, 52500), window(1000, 55400), window(950, 60000)]
    failures = [] if chosen['passed'] and all(not x['passed'] for x in negative) else ['Window acceptance']
    report = {'date': '2026-11-26', 'scope': 'DC corner arithmetic, not converter transient, source capability, thermal or PVT signoff',
              'sources': [{'path': n, 'sha256': hashlib.sha256((ROOT / n).read_bytes()).hexdigest()} for n in
                          ('tools/run_power_window.py', 'references/power-candidates/tps3703.pdf', 'references/power-candidates/tps63070.pdf', 'references/power-candidates/tps25947.pdf')],
              'conditional_budgets': {'sense_abs_current_a': 10e-6, 'load_a': 1.5,
                  'pcb_resistance_ohm': .010, 'regulation_and_ripple_allowance_v': .020,
                  'effective_resistor_tolerance': .001,
                  'note': 'Budgets requiring qualification. 1.5A is not the derived board consumption; resistor tolerance includes temperature/aging, not just initial tolerance. 20mV is not a guaranteed regulator transient limit.'},
              'candidate_limits': {'tps63070_forced_pwm_vfb_v': [.792, .808], 'feedback_abs_current_a': 100e-9,
                  'tps25947_on_resistance_max_ohm': .045,
                  'tps3703_f6050_nominal_uv_v': .47, 'threshold_accuracy': .01, 'max_hysteresis': .007},
              'chosen': chosen, 'negative': negative, 'failures': failures, 'production_released': False}
    (OUT / 'window-results.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'chosen': chosen, 'negative_rejected': sum(not x['passed'] for x in negative), 'failures': failures}))
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
