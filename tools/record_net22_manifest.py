"""Require complete NET22 runs and audit immutable predecessor Git snapshots."""
import hashlib
import inspect
import json
from pathlib import Path
import re
import subprocess
import sys
import record_net14a_manifest as original

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net22'
BASE = '03e224b48ec1657ea2adfd8330c9d3bf4d262255'
MANIFEST = OUT / 'manifest.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


exec(inspect.getsource(original.audit_history).replace('verification/net13/', 'verification/net21/'), globals())


def main():
    failures = []

    def hashed(item):
        path = (ROOT / item['path']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or digest(path) != item['sha256']:
            failures.append('Changed source ' + item['path'])

    def read(name):
        path = OUT / name
        if not path.is_file():
            failures.append('Missing completed report ' + name)
            return {}
        data = json.loads(path.read_text())
        if data.get('failures'):
            failures.append('Failed report ' + name)
        for item in data.get('sources', []):
            hashed(item)
        return data

    def complete(row, label, negative=None):
        result = row.get('execution', {})
        output = result.get('stdout', '')
        if row.get('compile', {}).get('exit') != 0 or row.get('compile', {}).get('stderr') or not row.get('passed', True):
            failures.append('Compile/acceptance ' + label)
        if negative:
            if result.get('exit') in (None, 0) or negative not in output:
                failures.append('Negative not detected ' + label)
        elif result.get('exit') != 0 or 'RESULT ' not in output or 'failures=0' not in output:
            failures.append('Incomplete execution ' + label)
        return output

    graph = read('native/schematic-check.json')
    if tuple(graph.get(k) for k in ['components', 'ics', 'pins', 'no_connects', 'max_signal_input_loads']) != (72, 36, 590, 31, 4):
        failures.append('Native graph counts')
    topology = read('clock-topology.json')
    budget = read('clock-budget.json')
    if len(budget.get('cases', [])) != 7 or budget.get('all_clock_paths_qualified') is not False:
        failures.append('Conditional clock budget scope')
    if len(topology.get('negatives', [])) != 3 or not all(r['passed'] for r in topology.get('negatives', [])):
        failures.append('Topology negatives')
    erc = read('native/erc-summary.json')
    if erc.get('exit') != 5 or erc.get('erc_passed') is not False or sum(erc.get('violation_counts', {}).values()) != 44:
        failures.append('Partial ERC scope')
    frames = read('native/results.json')
    if [(r['timed'], r['early_capture']) for r in frames.get('runs', [])] != [(0, 0), (1, 0), (1, 1)]:
        failures.append('Frame coverage')
    for row in frames.get('runs', []):
        if 'frames=2' not in complete(row, 'frame'):
            failures.append('Frame count')
    matrix = read('common-phase-matrix.json')
    if len(matrix.get('runs', [])) != 384:
        failures.append('Phase matrix coverage')
    for row in matrix.get('runs', []):
        if 'phase_samples=2000 each_phase=500' not in complete(row, 'phase matrix'):
            failures.append('Phase sample count')
    pulse = read('pulse-matrix.json')
    if len(pulse.get('runs', [])) != 256:
        failures.append('Pulse matrix coverage')
    for row in pulse.get('runs', []):
        if 'phase_samples=2000 each_phase=500' not in complete(row, 'pulse matrix'):
            failures.append('Pulse sample count')
    limits = read('ahc164-limits.json')
    if len(limits.get('runs', [])) != 3 or len(limits.get('negative', [])) != 6:
        failures.append('AHC164 calibration count')
    for row in limits.get('runs', []):
        complete(row, 'AHC164 calibration', row.get('expected_rejection'))
    for row in limits.get('negative', []):
        complete(row, 'AHC164 negative', row['expected_rejection'])
    cuts = read('clock-cuts.json')
    if [r['policy'] for r in cuts.get('runs', [])] != [0, 1] or len(cuts.get('negative', [])) != 1:
        failures.append('Clock cut matrix')
    for row in cuts.get('runs', []):
        if 'reset_cuts=80 captured_pixels=2560' not in complete(row, 'clock reset'):
            failures.append('Clock cut coverage')
    for row in cuts.get('negative', []):
        complete(row, 'clock negative', 'backend truncated pulse')
    probe = read('phase-skew-probe.json')
    if len(probe.get('runs', [])) != 7 or len(probe.get('investigations', [])) != 2 or sum(bool(r['rejection']) for r in probe.get('investigations', [])) != 1:
        failures.append('Baseline skew reproduction coverage')
    for row in probe.get('runs', []):
        complete(row, 'skew probe')
    memory = read('reset-memory-results.json')
    if [(r['policy'], r['assertion_ns']) for r in memory.get('runs', [])] != [(p, a) for p in (0, 1) for a in (1000, 19000)] or len(memory.get('negative', [])) != 2:
        failures.append('Memory cut coverage')
    for row in memory.get('runs', []):
        output = complete(row, 'memory')
        deadline = re.search(r'max_we_inhibit_ns=([\d.]+)', output)
        if not deadline or float(deadline[1]) > 100:
            failures.append('Memory WE deadline')
        if 'active_write_cuts=12 stopped_clocks=2' not in output:
            failures.append('Memory cut completion')
    for row, wanted in zip(memory.get('negative', []), ['memory bank reset before physical WE inhibition', 'independent RAM pin address changed while WE low']):
        complete(row, 'memory negative', wanted)
    actual = read('actual-cpu-write-reset.json')
    if [r['policy'] for r in actual.get('runs', [])] != [0, 1]:
        failures.append('Actual CPU fault policies')
    for row in actual.get('runs', []):
        output = complete(row, 'actual CPU fault')
        if 'actual_cpu_write_cuts=2 restarted_scans=2' not in output or 'fixture_defaults=0' not in output:
            failures.append('Actual CPU restart coverage')
    for policy in [0, 1]:
        scan = read(f'scan-policy{policy}-timed/system-scan-timed.json')
        if scan:
            output = complete(scan, 'scan')
            if 'scan_frames=5 completed_column_reads=40' not in output or 'stopped_cpu_checks=1 reset_pending_checks=1' not in output:
                failures.append('Scan coverage')
            hashed(scan['compiled_bench'])
    for name, marker in [('verified-cpu-ideal.json', 'instruction_cases=6886 transactions=13406'),
                         ('verified-cpu-timed-quick.json', 'instruction_cases=1062 transactions=1821'),
                         ('verified-cpu-early-timed-quick.json', 'instruction_cases=1062 transactions=1821')]:
        vectors = read('vectors/' + name)
        if len(vectors.get('runs', [])) != 1:
            failures.append('Vector coverage ' + name)
        for row in vectors.get('runs', []):
            if marker not in complete(row, name):
                failures.append('Vector completion ' + name)
    program = read('program/system-program-ideal.json')
    if len(program.get('runs', [])) != 1:
        failures.append('Boot coverage')
    for row in program.get('runs', []):
        output = complete(row, 'boot/frame')
        if 'retirements=132197' not in output or 'fixture_defaults=0' not in output or not row.get('frame_matches_reference'):
            failures.append('Boot completion/unknown SRAM/frame')
    for name in ['adapter-origin.json', 'cpu-adapter-origin.json']:
        for item in read(name).get('files', []):
            hashed(item)
    environment = read('environment.json')
    if environment.get('source'):
        hashed(environment['source'])
    for item in environment.get('shared_rom_inputs', []):
        hashed(item)
        if not item['unchanged_from_baseline']:
            failures.append('ROM changed')
    if len(environment.get('versions', [])) != 5 or len(environment.get('shared_rom_inputs', [])) != 4:
        failures.append('Tool/ROM environment')
    for name in ['research/sources.json', 'research/phase-sources.json']:
        for item in read(name).get('files', []):
            if item.get('sha256'):
                hashed(item)
                hashed({'path': item['extraction'], 'sha256': item['extraction_sha256']})
    if failures:
        print(json.dumps({'failures': failures, 'production_released': False}))
        return 1
    if '--check' in sys.argv:
        manifest = json.loads(MANIFEST.read_text())
        for item in manifest['files']:
            hashed(item)
        print(json.dumps({'checked': len(manifest['files']), 'failures': failures}))
        return int(bool(failures))
    failures += audit_history()
    if failures:
        print(json.dumps({'failures': failures}))
        return 1
    (OUT / 'acceptance.json').write_text(json.dumps({'date': '2026-11-26',
        'native_video_ics': 36, 'video_ic_delta': 1, 'phase_delay_combinations': 384,
        'pulse_asymmetry_combinations': 256, 'frame_scenarios': 3, 'frames_per_scenario': 2,
        'reset_clock_cuts': 160, 'master_active_write_cuts': 48, 'actual_cpu_write_cuts': 4,
        'instruction_cases_ideal': 6886, 'instruction_cases_per_timed_scenario': 1062,
        'timed_controller_cq_scenarios': 2, 'timed_scan_policies': [0, 1],
        'ideal_boot_retirements': 132197, 'ideal_boot_transactions': 232576,
        'ideal_boot_frame_pixels': 76800, 'ideal_boot_sram_seeded': False,
        'full_timed_boot_executed': False, 'partial_erc_violations': 44,
        'physical_oscillators_qualified': False, 'all_clock_paths_qualified': False,
        'production_released': False}, indent=2) + '\n')
    names = ['.gitattributes', 'README.md', 'AGENTS.md', 'PROVENANCE.md', 'ROADMAP.md', 'DECISIONS.md', 'CHANGELOG.md',
             'docs/engineering/NET22.md', 'docs/engineering/VALIDATION_STATUS.md', 'docs/engineering/PRODUCTION_GATES.md']
    # Include every tool introduced in this revision, avoiding unrelated existing files.
    names += git('ls-files', '--others', '--exclude-standard', 'tools').decode().splitlines()
    names += [n for n in git('diff', '--name-only', BASE, '--', 'tools').decode().splitlines()]
    files = {ROOT / n for n in names}
    for folder in ['hardware/video_common_clock', 'sim/net22', 'verification/net22', 'references/net22']:
        files.update(p for p in (ROOT / folder).rglob('*') if p.is_file() and p != MANIFEST and p.suffix != '.kicad_prl' and '__pycache__' not in p.parts)
    data = {'iteration': 'NET-22', 'date': '2026-11-26', 'base_git_commit': BASE,
            'scope': 'Native common-clock video; selected digital timing/CPU/reset/boot proofs. Physical clocks, global PVT/MTBF/energy and fabrication unqualified.',
            'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({'recorded': len(files), 'prior_snapshots': 25, 'failures': failures, 'production_released': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
