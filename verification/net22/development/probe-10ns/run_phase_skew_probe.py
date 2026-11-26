"""Probe independently delayed existing clock branches and a wiring hypothesis.

The FIX_GROUP branch is a simulation hypothesis, not yet a native KiCad variant.
"""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net22'


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('Unexpected predecessor ' + old)
    return text.replace(old, new)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'sim/net14c/video_raster_async_netlist.sv'
    text = source.read_text()
    text = once(text, 'EARLY_CAPTURE=0,RESOLVE_LATE=1)',
                'EARLY_CAPTURE=0,RESOLVE_LATE=1,FIX_GROUP=0,parameter realtime CLOCK_A_NS=10,CLOCK_B_NS=10)')
    for suffix, parameter in [('2', 'CLOCK_A_NS'), ('3', 'CLOCK_B_NS')]:
        text = once(text, f'assign #GATE_T n_BUF_2_{suffix}=', f'assign #(TIMED?{parameter}:0) n_BUF_2_{suffix}=')
    for instance in ['U9_0', 'U9_1']:
        text = once(text, f'{instance}(n_BUF_2_2,', f'{instance}(FIX_GROUP ? n_BUF_2_3 : n_BUF_2_2,')
    text = once(text, 'U11_0(n_BUF_2_3,', 'U11_0(FIX_GROUP ? n_BUF_2_2 : n_BUF_2_3,')
    probe = ROOT / 'sim/net22/video_skew_probe.sv'
    probe.write_text(text)
    names = ['sim/net14c/package_models_async.sv', 'sim/net22/video_skew_probe.sv', 'sim/net22/tb_phase_skew.sv']
    reports = {'date': '2026-11-26', 'scope': 'Adversarial branch delay probe, then simulation-only phase-clock regrouping. Selected AHC model, not complete min/max/PVT or native changed schematic.',
        'sources': [{'path': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest()} for p in names + ['tools/run_phase_skew_probe.py', 'sim/net14c/video_raster_async_netlist.sv']],
        'runs': [], 'investigations': [], 'failures': [], 'production_released': False}
    with tempfile.TemporaryDirectory(prefix='isa1-phase-skew-') as tmp:
        work = Path(tmp)
        configs = [(0, 1, 10, 10), (0, 1, 10, 1), (0, 1, 1, 10)] + [(1, p, a, b) for p in (0, 1) for a, b in [(10, 10), (10, 1), (1, 10)]]
        for fix, policy, a, b in configs:
            command = ['iverilog', '-g2012', '-Wall', '-s', 'tb_phase_skew', f'-Ptb_phase_skew.FIX_GROUP={fix}',
                f'-Ptb_phase_skew.POLICY={policy}', f'-Ptb_phase_skew.CLOCK_A_NS={a}', f'-Ptb_phase_skew.CLOCK_B_NS={b}',
                '-o', str(work / 'test.vvp'), *[str(ROOT / p) for p in names]]
            row = {'fix_group_hypothesis': fix, 'policy': policy, 'clock_a_ns': a, 'clock_b_ns': b, 'compile': run(command, work)}
            if row['compile']['exit'] == 0:
                row['execution'] = run(['vvp', str(work / 'test.vvp')], work, timeout=60)
            result = row.get('execution', {})
            row['execution_completed'] = result.get('exit') == 0 and 'phase_samples=10000 each_phase=2500 failures=0' in result.get('stdout', '')
            row['rejection'] = result.get('exit') not in (None, 0) and any(marker in result.get('stdout', '') for marker in ['video phase token lost or duplicated', 'AHC74 setup violation', 'AHC74 hold violation'])
            if not fix and a != b:
                reports['investigations'].append(row)
            else:
                row['passed'] = row['compile']['exit'] == 0 and row['execution_completed']
                reports['runs'].append(row)
                if not row['passed']:
                    reports['failures'].append([fix, policy, a, b])
            (OUT / 'phase-skew-probe.json').write_text(json.dumps(reports, indent=2) + '\n')
            print(json.dumps({'configuration': [fix, policy, a, b], 'compile_exit': row['compile']['exit'], 'execution': result}), flush=True)
    return int(bool(reports['failures']))


if __name__ == '__main__':
    raise SystemExit(main())
