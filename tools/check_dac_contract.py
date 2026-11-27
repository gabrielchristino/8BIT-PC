"""NET31 rational feasibility/counterexample audit, not electrical simulation."""
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'engineering/net31/dac_contract.json'


def expand(value, mapping):
    result = 0
    for bit in mapping:
        result = (result << 1) | ((value >> bit) & 1)
    return result


def main():
    c = json.loads(SOURCE.read_text())
    h, facts = c['hypotheses'], c['facts']
    q = lambda key: F(str(h[key]))
    parallel = lambda a, b: a * b / (a + b)
    load = parallel(q('local_shunt_ohm'), q('monitor_ohm'))
    white = q('white_v')
    code_scale = F(1023, 1024)
    ifs = white / load / code_scale
    nominal_r = 32 * F(str(facts['reference_nominal_v'])) / ifs
    assert F('0.002') <= ifs <= F('0.020')
    rows = []
    for pixel in range(256):
        inputs = [(pixel >> 5) & 7, (pixel >> 2) & 7, pixel & 3]
        widths = [7, 7, 3]
        maps = [h['r_g_db9_to_db0']] * 2 + [h['b_db9_to_db0']]
        codes = [expand(value, mapping) for value, mapping in zip(inputs, maps)]
        # Independent arithmetic endpoint mapping, including nearest integer.
        expected = [(2 * value * 1023 + limit) // (2 * limit)
                    for value, limit in zip(inputs, widths)]
        assert codes == expected, (pixel, codes, expected)
        volts = [ifs * F(code, 1024) * load for code in codes]
        assert all(0 <= value <= white for value in volts)
        rows.append({'pixel': pixel, 'codes_rgb10': codes,
                     'nominal_volts': [float(value) for value in volts]})
    for mapping, limit in [(h['r_g_db9_to_db0'], 7), (h['b_db9_to_db0'], 3)]:
        levels = [expand(value, mapping) for value in range(limit + 1)]
        assert levels[0] == 0 and levels[-1] == 1023
        assert all(a < b for a, b in zip(levels, levels[1:]))
    gains = [F('0.9'), F('1.1')]
    local_values = [q('local_shunt_ohm') * (1 + sign * q('local_tolerance_fraction')) for sign in [-1, 1]]
    monitor_values = [q('monitor_ohm') * (1 + sign * q('monitor_tolerance_fraction')) for sign in [-1, 1]]
    series_values = [q('trim_series_ohm') * (1 + sign * q('trim_series_tolerance_fraction')) for sign in [-1, 1]]
    trim_min = q('trim_total_ohm') * (1 - q('trim_total_tolerance_fraction'))
    # Calibrate with exactly 75 ohm monitor, then change its tolerance.
    corners = []
    for gain, local, series in itertools.product(gains, local_values, series_values):
        required = 32 * F('1.2') * gain * code_scale * parallel(local, q('monitor_ohm')) / white
        assert series <= required <= series + trim_min
        calibrated_ifs = 32 * F('1.2') * gain / required
        assert calibrated_ifs <= F('0.020')
        for monitor in monitor_values:
            v = calibrated_ifs * code_scale * parallel(local, monitor)
            assert abs(v / white - 1) < F('0.03')
            corners.append({'gain': float(gain), 'local_ohm': float(local),
                            'series_ohm': float(series), 'monitor_ohm': float(monitor),
                            'required_total_rset_ohm': float(required), 'white_v': float(v)})
    # Document rejected shortcuts, not successful physical operating cases.
    fixed_whites = [32 * F('1.2') * gain / q('fixed_rset_ohm') * code_scale * load for gain in gains]
    no_monitor = ifs * code_scale * q('local_shunt_ohm')
    minimum_setting_ifs = 32 * F('1.2') * max(gains) / min(series_values)
    start_max_ifs = minimum_setting_ifs * min(series_values) / (min(series_values) + trim_min)
    zeros_lsb_white = F(7 << 7, 1023) * white
    negative_checks = {
        'fixed_rset_fails_assumed_5pct_white_target': any(abs(v / white - 1) > F('0.05') for v in fixed_whites),
        'monitor_removed_exceeds_table_compliance': no_monitor > F(str(facts['compliance_upper_v_table'])),
        'minimum_trim_can_exceed_20ma': minimum_setting_ifs > F('0.020'),
        'zero_filling_low_bits_loses_white': zeros_lsb_white != white,
        'ths8136_direct_quarter_duty_fails_40pct': F(1, 4) < F('0.4')
    }
    assert all(negative_checks.values())
    assert start_max_ifs < F('0.020')
    report = {
        'date': c['date'], 'base_git_commit': c['base_git_commit'],
        'scope': 'Exact rational functional mapping and conditional DC arithmetic only; no HDL/native circuit/SPICE/physical approval.',
        'python': platform.python_version(), 'command': ['python3', 'tools/check_dac_contract.py'],
        'all_256_rgb332_codes': rows, 'calibration_corners': corners,
        'negative_checks': negative_checks, 'failures': [],
        'nominal_fullscale_ma': float(ifs * 1000), 'nominal_rset_ohm': float(nominal_r),
        'fixed_rset_white_range_v': [float(v) for v in fixed_whites],
        'unloaded_nominal_prediction_v': float(no_monitor),
        'minimum_trim_worst_current_ma': float(minimum_setting_ifs * 1000),
        'maximum_trim_start_worst_current_ma': float(start_max_ifs * 1000),
        'p3_to_next_p1_nominal_ns': float(F(2 * 10**9, h['master_hz'])),
        'p1_nominal_high_ns': float(F(10**9, h['master_hz'])),
        'timing_budget_is_not_global_sta': True,
        'sources': [{'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                    for path in [SOURCE, Path(__file__).resolve()]],
        'limitations': c['open'] + [
            'Multiplicative gain model at adjusted IFS is a hypothesis, not a new datasheet guarantee.',
            'Gain error already includes internal reference; its 1.08..1.32V range is not compounded.',
            'One-time calibration does not guarantee temperature/ripple/aging behavior.',
            'No-monitor voltage beyond compliance is a rejected linear extrapolation, not actual device voltage or damage prediction.',
            '3-percent post-calibration arithmetic and 5-percent rejected fixed-R target are engineering assumptions, not a VGA certification.'
        ]
    }
    output = ROOT / 'verification/net31'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'contract-results.json').write_text(json.dumps(report, indent=2) + '\n', newline='\n')
    print(json.dumps({'rgb_codes': len(rows), 'calibration_corners': len(corners),
                      'rejected_shortcuts': len(negative_checks), 'failures': report['failures'],
                      'nominal_fullscale_ma': report['nominal_fullscale_ma'],
                      'unloaded_v_not_qualified': report['unloaded_nominal_prediction_v']}))


if __name__ == '__main__':
    main()
