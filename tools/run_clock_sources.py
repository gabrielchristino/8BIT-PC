"""Clock/reset/raster source startup and missing-clock checks, no analog claim."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net23'


def main():
    names = ['sim/net14c/package_models_async.sv', 'sim/net22/phase_packages.sv',
             'sim/net22/video_common_async_netlist.sv', 'sim/net23/clock_models.sv',
             'hardware/clocked_reset/clocked_reset_netlist.sv', 'sim/net23/tb_clock_sources.sv']
    report = {'date': '2026-11-26', 'scope': 'Native configured oscillator/reset graph joined to NET22 raster. Behavioral startup/power-valid source and qualified RAW, conditional RC/binary reset boundary. No analog oscillator, supervisor/POR, jitter or physical release.',
              'sources': [{'path': n, 'sha256': hashlib.sha256((ROOT / n).read_bytes()).hexdigest()} for n in names +
                          ['tools/run_clock_sources.py', 'tools/build_clocked_reset.py', 'verification/net23/native/clocked_reset.xml', 'references/net22/abracon-ach.pdf']],
              'runs': [], 'failures': [], 'production_released': False}
    configs = [dict(POLICY=p, RELEASE_AT=release, DUTY=duty, CPU_PERIOD=10000/(1+ppm*1e-6), MASTER_PERIOD=39.721946/(1+ppm*1e-6))
               for p in (0, 1) for release, duty, ppm in [(12000000,.475,50),(1000,.525,-50)]]
    configs += [dict(POLICY=1, ABSENT=n, RELEASE_AT=1000, CPU_START=1000, MASTER_START=1000) for n in (1,2)]
    with tempfile.TemporaryDirectory(prefix='isa1-sources-') as tmp:
        work = Path(tmp)
        for index, config in enumerate(configs):
            command = ['iverilog', '-g2012', '-Wall', '-s', 'tb_clock_sources',
                       *[f'-Ptb_clock_sources.{key}={value}' for key, value in config.items()],
                       '-o', str(work / 'test.vvp'), *[str(ROOT / n) for n in names]]
            row = {'index': index, 'parameters': config, 'compile': run(command, work)}
            if row['compile']['exit'] == 0:
                row['execution'] = run(['vvp', str(work / 'test.vvp')], work, timeout=180)
            result = row.get('execution', {})
            expected = 'access_inhibited=1' if config.get('ABSENT') else 'starts=2 reset_cuts=3'
            row['passed'] = row['compile']['exit'] == 0 and not row['compile']['stderr'] and result.get('exit') == 0 and expected in result.get('stdout', '') and 'failures=0' in result['stdout']
            report['runs'].append(row)
            if not row['passed']:
                report['failures'].append(index)
            (OUT / 'clock-source-results.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps(row), flush=True)
            if not row['passed']:
                return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
