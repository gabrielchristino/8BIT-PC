"""Record tool versions and immutable shared firmware inputs for NET20."""
import hashlib
import json
from pathlib import Path
import subprocess
from build_cpu_global import KICAD
from run_rtl import BASE

ROOT = Path(__file__).resolve().parents[1]


def main():
    versions = []
    for command in [['python3', '--version'], ['iverilog', '-V'], ['ngspice', '--version'], [KICAD, 'version'], ['pdftotext', '-v']]:
        result = subprocess.run(command, capture_output=True, text=True)
        versions.append({'command': command, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    records = []
    baseline = '8af86e361e6eb510ff32c5f4c45cabc7ae633c85'
    for lane in range(4):
        path = BASE / f'control_lane{lane}.bin'
        name = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        original = subprocess.check_output(['git', 'show', baseline + ':' + name], cwd=ROOT)
        records.append({'path': name, 'sha256': hashlib.sha256(data).hexdigest(), 'unchanged_from_baseline': data == original})
    report = {'date': '2026-11-26', 'collected_after_initial_runs': True, 'versions': versions, 'shared_rom_inputs': records,
              'source': {'path': 'tools/record_reset_environment.py', 'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
              'scope': 'Supplementary tool environment; scan/memory runner did not individually record every version or shared ROM hash before execution.'}
    (ROOT / 'verification/net20/environment.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'versions': len(versions), 'roms': len(records), 'all_roms_unchanged': all(x['unchanged_from_baseline'] for x in records)}))


if __name__ == '__main__':
    main()
