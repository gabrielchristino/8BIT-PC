"""Selected independent clock-buffer, phase-CQ, NOR and duty extremes."""
import hashlib
import itertools
import json
from pathlib import Path
import tempfile
from run_rtl import run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net22'


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('Unexpected native projection ' + old)
    return text.replace(old, new)


def main():
    source = ROOT / 'sim/net22/video_common_async_netlist.sv'
    text = once(source.read_text(), 'RESOLVE_LATE=1)',
        'RESOLVE_LATE=1,EARLY_ALL=0,parameter realtime MASTER_T=8.5,H_T=8.5,V_T=8.5,CAP_T=8.5,NOR_T=3.6)')
    for net, parameter in [('BUF_2_2', 'MASTER_T'), ('BUF_2_0', 'H_T'), ('BUF_2_1', 'V_T'), ('CAPTURE_CLOCK', 'CAP_T')]:
        text = once(text, f'assign #GATE_T n_{net}=', f'assign #(TIMED?{parameter}:0) n_{net}=')
    text = once(text, 'assign #(TIMED?3.6:0)', 'assign #(TIMED?NOR_T:0)')
    text = once(text, '.EARLY_CAPTURE(EARLY_CAPTURE)) U9', '.EARLY_CAPTURE(EARLY_CAPTURE),.EARLY_ALL(EARLY_ALL)) U9')
    probe = ROOT / 'sim/net22/video_common_probe.sv'
    probe.write_text(text)
    names = ['sim/net14c/package_models_async.sv', 'sim/net22/phase_packages.sv',
             'sim/net22/video_common_probe.sv', 'sim/net22/tb_common_phase_matrix.sv']
    report = {'date': '2026-11-26', 'scope': 'Selected combinations of four output-buffer delays1/8.5ns, shift CQ min/max/earlyP3, NOR1/3.6ns, source duty47.5/52.5%, and binary reset policy. Other package delays remain selected maxima; no complete PVT/minmax/MTBF or extracted PCB claim.',
        'sources': [{'path': name, 'sha256': hashlib.sha256((ROOT / name).read_bytes()).hexdigest()} for name in names + [
            'tools/run_common_phase_matrix.py', 'sim/net22/video_common_async_netlist.sv', 'references/ti/sn74ahc125.pdf',
            'references/net22/sn74ahc164.pdf', 'references/net22/sn74lvc1g27.pdf']],
        'runs': [], 'failures': [], 'production_released': False}
    configs = list(itertools.product(itertools.product((1, 8.5), repeat=4), (0, 1), [(0, 0), (1, 0), (0, 1)], (1, 3.6), (.475, .525)))
    with tempfile.TemporaryDirectory(prefix='isa1-common-phase-') as tmp:
        work = Path(tmp)
        for index, (delays, policy, early, nor, duty) in enumerate(configs):
            parameters = dict(zip(['MASTER_T', 'H_T', 'V_T', 'CAP_T'], delays))
            parameters.update(POLICY=policy, EARLY_CAPTURE=early[0], EARLY_ALL=early[1], NOR_T=nor, DUTY=duty)
            command = ['iverilog', '-g2012', '-Wall', '-s', 'tb_common_phase_matrix',
                *[f'-Ptb_common_phase_matrix.{key}={value}' for key, value in parameters.items()],
                '-o', str(work / 'test.vvp'), *[str(ROOT / p) for p in names]]
            row = {'index': index, 'parameters': parameters, 'compile': run(command, work)}
            if row['compile']['exit'] == 0:
                row['execution'] = run(['vvp', str(work / 'test.vvp')], work, timeout=30)
            result = row.get('execution', {})
            row['passed'] = row['compile']['exit'] == 0 and not row['compile']['stderr'] and result.get('exit') == 0 and 'phase_samples=2000 each_phase=500' in result.get('stdout', '') and 'failures=0' in result['stdout']
            report['runs'].append(row)
            if not row['passed']:
                report['failures'].append(index)
            if (index + 1) % 32 == 0 or not row['passed'] or index + 1 == len(configs):
                (OUT / 'common-phase-matrix.json').write_text(json.dumps(report, indent=2) + '\n')
                print(json.dumps({'completed': index + 1, 'planned': len(configs), 'failures': report['failures'],
                                  'last_execution': result if not row['passed'] else None}), flush=True)
            if not row['passed']:
                return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
