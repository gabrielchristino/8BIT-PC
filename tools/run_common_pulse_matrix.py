"""Extend NET22 with independently selected digital rise/fall propagation."""
import hashlib
import itertools
import json
from pathlib import Path
import tempfile
from run_rtl import run
from run_common_phase_matrix import once

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net22'


def main():
    ancestor = ROOT / 'sim/net22/video_common_probe.sv'
    text = once(ancestor.read_text(), 'NOR_T=3.6)', 'NOR_T=3.6,SHIFT_RISE=1,SHIFT_FALL=12.5)')
    for parameter in ['MASTER_T', 'H_T', 'V_T', 'CAP_T']:
        text = once(text, f'#(TIMED?{parameter}:0)', f'#(TIMED?{parameter}:0,TIMED?(9.5-{parameter}):0)')
    text = once(text, 'net22_ahc164 #(', 'net22_ahc164_asymmetric #(')
    text = once(text, '.EARLY_ALL(EARLY_ALL)) U9', '.EARLY_ALL(EARLY_ALL),.Q_RISE(SHIFT_RISE),.Q_FALL(SHIFT_FALL)) U9')
    projection = ROOT / 'sim/net22/video_common_pulse_probe.sv'
    projection.write_text(text)
    model_source = ROOT / 'sim/net22/phase_packages.sv'
    model = model_source.read_text().replace('module net22_ahc164 #', 'module net22_ahc164_asymmetric #')
    model = once(model, 'EARLY_ALL=0)', 'EARLY_ALL=0,parameter realtime Q_RISE=1,Q_FALL=12.5)')
    model = once(model, '#((TIMED && EARLY_CAPTURE && i==3)?1:CQ)',
                 '#(TIMED?((i==0 ? (a&b) : state[i-1]) ? Q_RISE:Q_FALL):0)')
    model_path = ROOT / 'sim/net22/phase_packages_asymmetric.sv'
    model_path.write_text('// GENERATED probe: only output transition delays changed; internal shift/monitors preserved.\n' + model)
    names = ['sim/net14c/package_models_async.sv', 'sim/net22/phase_packages_asymmetric.sv',
             'sim/net22/video_common_pulse_probe.sv', 'sim/net22/tb_common_phase_matrix.sv']
    sources = names + ['tools/run_common_pulse_matrix.py', 'tools/run_common_phase_matrix.py',
                      'sim/net22/video_common_probe.sv', 'sim/net22/phase_packages.sv',
                      'references/ti/sn74ahc125.pdf', 'references/net22/sn74ahc164.pdf']
    report = {'date': '2026-11-26', 'scope': 'Independent digital rise/fall propagation extrema per clock-buffer branch1/8.5ns and shift pins1/12.5ns, two NOR/duty/reset choices. No electrical transition/slew, jitter or complete PVT claim; other package delays remain fixed.',
              'sources': [{'path': n, 'sha256': hashlib.sha256((ROOT / n).read_bytes()).hexdigest()} for n in sources],
              'runs': [], 'failures': [], 'production_released': False}
    configs = list(itertools.product(itertools.product((1, 8.5), repeat=4), (0, 1), (1, 12.5), (1, 3.6), (.475, .525)))
    with tempfile.TemporaryDirectory(prefix='isa1-pulse-matrix-') as tmp:
        work = Path(tmp)
        for index, (delays, policy, rise, nor, duty) in enumerate(configs):
            parameters = dict(zip(['MASTER_T', 'H_T', 'V_T', 'CAP_T'], delays))
            parameters.update(POLICY=policy, SHIFT_RISE=rise, SHIFT_FALL=13.5-rise, NOR_T=nor, DUTY=duty)
            command = ['iverilog', '-g2012', '-Wall', '-s', 'tb_common_phase_matrix',
                       *[f'-Ptb_common_phase_matrix.{key}={value}' for key, value in parameters.items()],
                       '-o', str(work / 'test.vvp'), *[str(ROOT / p) for p in names]]
            # New projection parameters need forwarding by a separate bench.
            bench_text = (ROOT / names[-1]).read_text()
            bench_text = once(bench_text, 'DUTY=0.5;', 'DUTY=0.5,SHIFT_RISE=1,SHIFT_FALL=12.5;')
            bench_text = once(bench_text, '.EARLY_ALL(EARLY_ALL),', '.SHIFT_RISE(SHIFT_RISE),.SHIFT_FALL(SHIFT_FALL),.EARLY_ALL(EARLY_ALL),')
            bench = work / 'tb_pulse.sv'
            bench.write_text(bench_text)
            command[-1] = str(bench)
            row = {'index': index, 'parameters': parameters, 'compile': run(command, work)}
            if row['compile']['exit'] == 0:
                row['execution'] = run(['vvp', str(work / 'test.vvp')], work, timeout=30)
            result = row.get('execution', {})
            row['passed'] = row['compile']['exit'] == 0 and not row['compile']['stderr'] and result.get('exit') == 0 and 'phase_samples=2000 each_phase=500' in result.get('stdout', '') and 'failures=0' in result['stdout']
            report['runs'].append(row)
            if not row['passed']:
                report['failures'].append(index)
            if (index + 1) % 32 == 0 or not row['passed'] or index + 1 == len(configs):
                report['compiled_bench_sha256'] = hashlib.sha256(bench.read_bytes()).hexdigest()
                (OUT / 'pulse-matrix.json').write_text(json.dumps(report, indent=2) + '\n')
                print(json.dumps({'completed': index + 1, 'planned': len(configs), 'failures': report['failures'],
                                  'last_execution': result if not row['passed'] else None}), flush=True)
            if not row['passed']:
                (OUT / 'development/pulse-failed-bench.sv').write_bytes(bench.read_bytes())
                return 1
        (ROOT / 'sim/net22/tb_common_pulse_matrix.sv').write_bytes(bench.read_bytes())
        report['sources'].append({'path': 'sim/net22/tb_common_pulse_matrix.sv', 'sha256': report['compiled_bench_sha256']})
        (OUT / 'pulse-matrix.json').write_text(json.dumps(report, indent=2) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
