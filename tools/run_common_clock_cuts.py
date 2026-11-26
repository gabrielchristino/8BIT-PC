"""NET22 reset cuts, preserving the independent backend pulse monitor."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net22'


def main():
    ancestor = ROOT / 'sim/net14c/tb_video_clock_cuts.sv'
    text = ancestor.read_text().replace('video_system_netlist', 'video_common_clock_netlist')
    bench = ROOT / 'sim/net22/tb_common_clock_cuts.sv'
    bench.write_text(text)
    native = ROOT / 'sim/net22/video_common_async_netlist.sv'
    original = native.read_text()
    lines = original.splitlines()
    changed = 0
    for i, line in enumerate(lines):
        if ') U11_0(' in line:
            start = line.index(') U11_0(') + len(') U11_0(')
            args = line[start:-2].split(',')
            assert args[1] == "1'b1"
            args[1] = 'n_BUF_1_1'
            lines[i] = line[:start] + ','.join(args) + ');'
            changed += 1
    assert changed == 1
    names = ['sim/net14c/package_models_async.sv', 'sim/net22/phase_packages.sv']
    paths = [ROOT / p for p in names] + [native, bench, ancestor, Path(__file__)]
    report = {'date': '2026-11-26', 'scope': '80 reset/power-good phase cuts per binary policy; free-running master, strict downstream monitors, no analog metastability/MTBF qualification',
              'sources': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
              'runs': [], 'negative': [], 'failures': [], 'production_released': False}
    with tempfile.TemporaryDirectory(prefix='isa1-common-cuts-') as tmp:
        work = Path(tmp)
        fault = work / 'asynchronous-backend-clear.sv'
        fault.write_text('\n'.join(lines) + '\n')
        for negative, graph, policy in [(False, native, 0), (False, native, 1), (True, fault, 1)]:
            cmd = ['iverilog', '-g2012', '-Wall', '-s', 'tb_video_clock_cuts',
                   f'-Ptb_video_clock_cuts.RESOLVE_LATE={policy}', '-o', str(work / 'test.vvp'),
                   *[str(ROOT / p) for p in names], str(graph), str(bench)]
            row = {'asynchronous_backend_clear': negative, 'policy': policy, 'compile': run(cmd, work)}
            if row['compile']['exit'] == 0:
                row['execution'] = run(['vvp', str(work / 'test.vvp')], work, timeout=90)
            result = row.get('execution', {})
            compiled = row['compile']['exit'] == 0 and not row['compile']['stderr']
            if negative:
                row['expected_rejection'] = True
                row['mutated_netlist_sha256'] = hashlib.sha256(fault.read_bytes()).hexdigest()
                row['passed'] = compiled and result.get('exit', 0) != 0 and 'backend truncated pulse' in result.get('stdout', '')
                report['negative'].append(row)
            else:
                row['passed'] = compiled and result.get('exit') == 0 and 'reset_cuts=80 captured_pixels=2560' in result.get('stdout', '')
                report['runs'].append(row)
            if not row['passed']:
                report['failures'].append([negative, policy])
            (OUT / 'clock-cuts.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps(row), flush=True)
    return int(bool(report['failures']))


if __name__ == '__main__':
    raise SystemExit(main())
