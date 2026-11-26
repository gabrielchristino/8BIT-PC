"""Calibrate the new AHC164 pin timing model, including expected rejections."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net22'


def main():
    names = ['sim/net22/phase_packages.sv', 'sim/net22/tb_ahc164_limits.sv']
    report = {'date': '2026-11-26', 'scope': 'Selected SCAS970 timing/delay monitor calibration; negatives exceed qualification limits, not measured silicon failures.',
        'sources': [{'path': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest()} for p in names + ['tools/check_ahc164_limits.py', 'references/net22/sn74ahc164.pdf']],
        'runs': [], 'negative': [], 'failures': [], 'production_released': False}
    expectations = {1: 'AHC164 data setup violation', 2: 'AHC164 data hold violation', 3: 'AHC164 clock pulse violation',
                    4: 'AHC164 reset recovery violation', 5: 'AHC164 clear pulse violation', 6: 'AHC164 clock outside95MHz qualification envelope'}
    with tempfile.TemporaryDirectory(prefix='isa1-ahc164-limits-') as tmp:
        work = Path(tmp)
        for mode in [0, 7, 8, 1, 2, 3, 4, 5, 6]:
            command = ['iverilog', '-g2012', '-Wall', '-s', 'tb_ahc164_limits', f'-Ptb_ahc164_limits.MODE={mode}',
                       '-o', str(work / 'test.vvp'), *[str(ROOT / p) for p in names]]
            row = {'mode': mode, 'compile': run(command, work)}
            if row['compile']['exit'] == 0:
                row['execution'] = run(['vvp', str(work / 'test.vvp')], work)
            output = row.get('execution', {})
            row['passed'] = row['compile']['exit'] == 0 and not row['compile']['stderr'] and (
                output.get('exit') not in (None, 0) and expectations[mode] in output.get('stdout', '') if mode in expectations else
                output.get('exit') == 0 and 'ahc164_shift_and_delay=1 failures=0' in output.get('stdout', ''))
            if mode in expectations:
                row['expected_rejection'] = expectations[mode]
            report['negative' if mode in expectations else 'runs'].append(row)
            if not row['passed']:
                report['failures'].append(mode)
            (OUT / 'ahc164-limits.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps({'mode': mode, 'passed': row['passed'], 'execution': output}), flush=True)
            if not row['passed']:
                return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
