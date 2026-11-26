"""Calibrate the behavioral source's power/startup bookkeeping and guards."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run

ROOT = Path(__file__).resolve().parents[1]


def main():
    names = ['sim/net23/clock_models.sv', 'sim/net23/tb_clock_model.sv']
    report = {'date': '2026-11-26', 'scope': 'Behavioral model calibration with enable held high as in native circuit. Power interruption during startup/repeated start and invalid parameter guards. Not analog startup/jitter, disabled Hi-Z timing or vendor model qualification.',
              'sources': [{'path': n, 'sha256': hashlib.sha256((ROOT / n).read_bytes()).hexdigest()} for n in names + ['tools/check_clock_model.py']],
              'runs': [], 'negative': [], 'failures': []}
    with tempfile.TemporaryDirectory(prefix='isa1-clock-model-') as tmp:
        work = Path(tmp)
        for mode, duty in [(0,.475),(0,.525),(1,.5),(2,.5),(3,.5)]:
            command = ['iverilog', '-g2012', '-Wall', '-s', 'tb_clock_model', f'-Ptb_clock_model.MODE={mode}',
                       f'-Ptb_clock_model.DUTY={duty}', '-o', str(work / 'test.vvp'), *[str(ROOT / n) for n in names]]
            row = {'mode': mode, 'duty': duty, 'compile': run(command, work)}
            if row['compile']['exit'] == 0:
                row['execution'] = run(['vvp', str(work / 'test.vvp')], work)
            result = row.get('execution', {})
            row['passed'] = row['compile']['exit'] == 0 and not row['compile']['stderr'] and (
                result.get('exit') not in (None,0) and 'invalid oscillator configuration' in result.get('stdout','') if mode else
                result.get('exit') == 0 and 'power_glitch_restart=1 repeated_start=1' in result.get('stdout','') and 'failures=0' in result['stdout'])
            if mode:
                row['expected_rejection'] = 'invalid oscillator configuration'
            report['negative' if mode else 'runs'].append(row)
            if not row['passed']:
                report['failures'].append([mode,duty])
            (ROOT / 'verification/net23/clock-model-calibration.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(row),flush=True)
            if not row['passed']:
                return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
