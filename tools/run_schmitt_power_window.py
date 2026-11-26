"""NET21 research: supervisor CL50pF, Schmitt receiver and revised DC window.

Arithmetic proposal only; does not modify NET20 or approve regulator hardware.
"""
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net21'


def window(top, feedback, input_pf=10, routing_pf=10):
    trips, releases, rails = [], [], []
    for rt, rb, accuracy, current in itertools.product((-.001, .001), (-.001, .001), (-.02, .02), (-25e-9, 25e-9)):
        rtop, rbottom = top * (1 + rt), 100 * (1 + rb)
        trip = .405 * (1 + accuracy) * (1 + rtop / rbottom) + current * rtop
        trips.append(trip)
        releases.append(trip * 1.03)
    for rt, rb, reference, leak in itertools.product((-.001, .001), (-.001, .001), (-.01, .01), (-100e-9, 100e-9)):
        rtop, rbottom = feedback * (1 + rt), 10000 * (1 + rb)
        rails.append(.8 * (1 + reference) * (1 + rtop / rbottom) + leak * rtop)
    minimum = min(rails) - 1.5 * (.045 + .010) - .020
    maximum = max(rails) + .020
    qualified = min(trips) * .95
    we = 20e-6 + 1e-6 + 100e-9
    bank = we + 20e-6
    hold = qualified - .02 * (1.5 + .5) - (1.5 * bank + 50e-6) / .0044
    cap = input_pf + routing_pf
    return {'sense_top_ohm': top, 'sense_bottom_ohm': 100, 'regulator_feedback_top_ohm': feedback,
            'nominal_rail_v': .8 * (1 + feedback / 10000), 'trip_min_v': min(trips), 'release_max_v': max(releases),
            'rail_min_v': minimum, 'rail_max_v': maximum, 'release_margin_v': minimum - max(releases),
            'qualified_detection_v': qualified, 'hold_bank_lower_v': hold, 'bank_completion_s': bank,
            'supervisor_cl_budget_pf': cap, 'supervisor_timing_test_cl_pf': 50,
            'monitor_corner_count': len(trips), 'regulator_corner_count': len(rails),
            'passed': minimum > max(releases) and maximum < 5.5 and hold > 4.5 and cap <= 50}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    chosen = window(1120, 57400)
    negative = [window(1120, 55400), window(1120, 60000), window(1180, 57400), window(1120, 57400, 50, 10)]
    failures = [] if chosen['passed'] and all(not item['passed'] for item in negative) else ['Candidate window']
    names = ['tools/run_schmitt_power_window.py', 'references/net20/tps3808.pdf', 'references/ti/sn74ahc14.pdf',
             'references/power-candidates/tps63070.pdf', 'references/power-candidates/tps25947.pdf']
    report = {'date': '2026-11-26', 'scope': 'Arithmetic for TPS3808G01DBVR, 100k pullup and two AHC14 inverters. Native graph and digital tests have separate reports; no regulator, USB-C, POR or physical approval.',
              'chosen': chosen, 'negative': negative,
              'candidate_limits': {'supervisor_threshold_v': .405, 'threshold_accuracy': .02, 'hysteresis_max': .03,
                  'sense_abs_current_at_threshold_a': 25e-9, 'supervisor_reset_pullup_ohm': 100000,
                  'reset_delay_ct_open_ms': [12, 28], 'detect_delay_max_s': 20e-6, 'test_input_overdrive': .05,
                  'reset_cl_test_pf': 50, 'schmitt_input_cap_at_5v_max_pf': 10},
              'conditional_budgets': {'effective_resistor_tolerance': .001, 'load_a': 1.5, 'trace_resistance_ohm': .01,
                  'ripple_and_regulation_allowance_v': .020, 'effective_bulk_cap_f': .0044, 'bulk_esr_ohm': .02,
                  'reverse_peak_a': .5, 'reverse_charge_c': 50e-6, 'sense_filter_s': 1e-6, 'routing_cap_pf': 10,
                  'logic_after_qualified_reset_s': 100e-9, 'memory_bank_settling_s': 20e-6},
              'sources': [{'path': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest()} for p in names],
              'failures': failures, 'native_circuit_report': 'verification/net21/native/schematic-check.json', 'production_released': False}
    (OUT / 'research-window.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'chosen': chosen, 'negative_rejected': sum(not row['passed'] for row in negative), 'failures': failures}))
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
