"""Read-only audit of frozen NET27/NET30 attempts; never starts a simulator.

Writes only the explicitly selected audit output, outside the attempts.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
import time


EXPECTED = dict(retirements=132197, transactions=232576,
                vram_transactions=32771, frame_pixels=76800)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text())


def final_checks(report, state, stdout, stderr, frame, reference):
    """Independent completion criteria, also exercised by falsification cases."""
    errors = []
    def require(condition, label):
        if not condition:
            errors.append(label)
    require(state.get('status') == 'complete' and state.get('simulation_passed') is True, 'completion-state')
    require(state.get('exit') == 0 and state.get('wall_timeout') is False, 'process-exit')
    require(not stderr, 'stderr-not-empty')
    require(not report.get('failures', ['missing']), 'report-failures')
    require(report.get('full_timed_program') is True and report.get('timed') is True
            and report.get('quick') is False, 'full-timed-scope')
    require(report.get('exact_counts_verified') is True and report.get('unseeded_no_aborts_verified') is True,
            'runner-acceptance-flags')
    runs = report.get('runs', [])
    require(len(runs) == 1, 'one-run')
    if len(runs) == 1:
        run = runs[0]
        require(run.get('passed') is True and run.get('frame_matches_reference') is True, 'runner-frame-comparison')
        for phase in ['compile', 'execution']:
            result = run.get(phase, {})
            require(result.get('exit') == 0 and result.get('wall_timeout') is False
                    and not result.get('stderr'), phase + '-result')
        require(run.get('execution', {}).get('stdout') == stdout, 'report-stdout')
    result_lines = re.findall(r'^RESULT (.*)$', stdout, re.M)
    fields = dict(re.findall(r'(\w+)=(\d+)', result_lines[0])) if len(result_lines) == 1 else {}
    require(all(fields.get(k) == str(v) for k, v in EXPECTED.items()) and fields.get('failures') == '0', 'exact-counts')
    require(int(fields.get('wait_checks', '0')) > 0 and int(fields.get('pause_checks', '0')) > 0, 'wait-pause-monitors')
    memory = re.findall(r'^MEMORY_MODEL (.*)$', stdout, re.M)
    mf = dict(re.findall(r'(\w+)=(\d+)', memory[0])) if len(memory) == 1 else {}
    require(mf == dict(ram_valid_writes='337', vram_valid_writes='32770', ram_aborts='0',
                       vram_aborts='0', fixture_defaults='0'), 'memory-no-aborts-unseeded')
    require('analog_metastability_approved=0' in stdout and stdout.count('$finish called') == 1,
            'finish-and-reset-scope')
    require(not re.search(r'FATAL|ERROR|WARNING', stdout, re.I), 'diagnostic-output')
    require(state.get('stdout_sha256') == digest(stdout.encode()) and state.get('stderr_sha256') == digest(stderr.encode()), 'log-hashes')
    require(frame == reference and frame.startswith(b'P6\n160 480\n255\n')
            and len(frame) == len(b'P6\n160 480\n255\n') + 76800 * 3, 'exact-frame-bytes')
    require(report.get('observed_frame_sha256') == digest(frame), 'frame-hash')
    limits = state.get('limits', {})
    require(limits == dict(memory_mb=1024, cpu_seconds=72000, wall_seconds=86400, output_mb_per_file=8), 'declared-limits')
    require(0 < state.get('seconds', 0) <= limits.get('wall_seconds', 0), 'wall-limit')
    return errors


def process_identity(state):
    boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    proc = Path('/proc') / str(state['pid'])
    observed = {'boot_id': boot, 'pid': state['pid'], 'present': proc.exists()}
    try:
        observed.update(command=[x.decode() for x in (proc/'cmdline').read_bytes().split(b'\0') if x],
                        cwd=os.readlink(proc/'cwd'), limits=(proc/'limits').read_text(),
                        stat=(proc/'stat').read_text(), status=(proc/'status').read_text())
    except FileNotFoundError:
        pass
    observed['matches_recorded_identity'] = (boot == state['boot_id']
        and observed.get('command') == state['command'] and observed.get('cwd') == state['cwd'])
    return observed


def audit(root, attempt, reference):
    state = load(attempt/'run-state.json')
    origin = load(attempt/'run-origin.json')
    checks, errors = [], []
    def check(path, sha, role):
        path = Path(path)
        ok = path.is_file() and digest(path.read_bytes()) == sha
        checks.append(dict(path=path.relative_to(root).as_posix(), role=role, matches=ok, sha256=sha))
        if not ok:
            errors.append(role + ':' + str(path.relative_to(root)))
    for source in origin['sources']:
        check(root/source['path'], source['sha256'], 'frozen-runner')
    snapshots = load(attempt/'compiler-inputs.json')
    for source in snapshots:
        check(root/source['snapshot'], source['sha256'], 'compiled-snapshot')
        original = Path(source['original'])
        if original.is_relative_to(root):
            check(original, source['sha256'], 'frozen-model')
    identity = process_identity(state)
    stdout = (attempt/'simulation.stdout.log').read_text()
    stderr = (attempt/'simulation.stderr.log').read_text()
    progress = re.findall(r'^PROGRESS (.*)$', stdout, re.M)
    result = dict(attempt=attempt.relative_to(root).as_posix(), state=state,
                  identity=identity, source_checks=checks, errors=errors,
                  last_progress=progress[-1] if progress else None, simulation_accepted=False,
                  expected=EXPECTED, production_released=False)
    report_path = attempt/'system-program-timed.json'
    if state['status'] != 'complete':
        result['classification'] = 'running' if identity['matches_recorded_identity'] else 'interrupted-or-unresolved'
        if state['status'] == 'running' and not identity['matches_recorded_identity']:
            errors.append('recorded-running-process-not-found')
        return result
    if not report_path.exists():
        errors.append('missing-final-report')
        result['classification'] = 'rejected'
        return result
    report = load(report_path)
    frame = (attempt/'observed-frame.ppm').read_bytes()
    errors += final_checks(report, state, stdout, stderr, frame, reference)
    source_records = []
    for source in report['sources']:
        path = root/source['path']
        resolution = 'current' if path.is_file() and digest(path.read_bytes()) == source['sha256'] else None
        if resolution is None:
            for commit in [origin['run_source_commit'], origin['circuit_base_commit']]:
                blob = subprocess.run(['git', 'show', commit+':'+source['path']], cwd=root, capture_output=True)
                if blob.returncode == 0 and digest(blob.stdout) == source['sha256']:
                    resolution = 'git:' + commit
                    break
        source_records.append(dict(**source, resolution=resolution))
        if resolution is None:
            errors.append('unresolved-report-source:'+source['path'])
    result.update(classification='accepted' if not errors else 'rejected', simulation_accepted=not errors,
                  final_report_sha256=digest(report_path.read_bytes()), report_sources=source_records,
                  observed_frame_sha256=digest(frame), exact_frame_bytes=len(frame),
                  note='All 32768 VRAM bytes checked in HDL; RAM sentinel and every architectural retirement/bus transaction checked. No exhaustive final RAM dump is claimed.')
    # Deliberate corruption of the acceptance evidence must never pass.
    cases = []
    for label in ['count', 'frame', 'abort', 'missing-finish', 'missing-state', 'timeout']:
        bad_report, bad_state, bad_stdout, bad_frame = copy.deepcopy(report), copy.deepcopy(state), stdout, frame
        if label == 'count': bad_stdout = stdout.replace('retirements=132197', 'retirements=132196')
        if label == 'frame': bad_frame = frame[:-1] + bytes([frame[-1] ^ 1])
        if label == 'abort': bad_stdout = stdout.replace('ram_aborts=0', 'ram_aborts=1', 1)
        if label == 'missing-finish': bad_stdout = stdout.replace('$finish called', 'removed finish')
        if label == 'missing-state': bad_state['simulation_passed'] = False
        if label == 'timeout': bad_state['wall_timeout'] = True
        rejected = final_checks(bad_report, bad_state, bad_stdout, stderr, bad_frame, reference)
        cases.append(dict(case=label, rejected=bool(rejected), reasons=rejected))
    result['acceptance_negatives'] = cases
    if not all(c['rejected'] for c in cases):
        errors.append('acceptance-monitor-negative-escaped')
        result.update(simulation_accepted=False, classification='rejected')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    attempts = [root/f'verification/net{n}/full-timed/attempt-001' for n in [27, 30]]
    assert not any(output.is_relative_to(p) for p in attempts), 'Never write into attempts'
    sys.path.insert(0, str(root/'tools'))
    from run_rtl import program_fixture
    with tempfile.TemporaryDirectory(prefix='isa1-full-audit-') as work:
        program, reference, _ = program_fixture(Path(work))
        assert all(program[k] == EXPECTED[k] for k in ['retirements', 'transactions'])
        rows = [audit(root, p, reference) for p in attempts]
        regenerated = []
        for attempt in attempts:
            for name in ['program_state.hex', 'program_bus.hex', 'rom_image.hex']:
                regenerated.append(dict(attempt=attempt.relative_to(root).as_posix(), file=name,
                    identical=(attempt/'input-images'/name).read_bytes() == (Path(work)/name).read_bytes()))
        assert all(r['identical'] for r in regenerated)
    data = dict(observed_unix=time.time(), python=platform.python_version(), platform=platform.platform(),
                command=sys.argv, reference=program, reference_frame_sha256=digest(reference),
                regenerated_input_comparisons=regenerated, attempts=rows,
                auditor_sha256=digest(Path(__file__).read_bytes()), production_released=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps([dict(attempt=r['attempt'], classification=r['classification'], errors=r['errors'],
                           last_progress=r['last_progress']) for r in rows]))
    return int(any(r['errors'] for r in rows))


if __name__ == '__main__':
    raise SystemExit(main())
