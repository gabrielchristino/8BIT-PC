"""Audit accepted NET20 reports and all 23 predecessor snapshots in Git."""
import hashlib
import inspect
import json
from pathlib import Path
import re
import subprocess
import sys
import record_net14a_manifest as original

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net20'
BASE = '8af86e361e6eb510ff32c5f4c45cabc7ae633c85'
MANIFEST = OUT / 'manifest.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


exec(inspect.getsource(original.audit_history).replace('verification/net13/', 'verification/net19a/'), globals())


def main():
    failures = []

    def read(name):
        data = json.loads((OUT / name).read_text())
        if data.get('failures'):
            failures.append('Failed report ' + name)
        for item in data.get('sources', []):
            if digest(ROOT / item['path']) != item['sha256']:
                failures.append('Changed tested source ' + item['path'])
        return data

    def complete(row, label, negative=None):
        result = row.get('execution', {})
        output = result.get('stdout', '')
        if row['compile']['exit'] or row['compile']['stderr'] or not row.get('passed', True):
            failures.append('Compile/acceptance ' + label)
        if negative:
            if result.get('exit') in (None, 0) or negative not in output:
                failures.append('Missing negative rejection ' + label)
        elif result.get('exit') != 0 or 'RESULT ' not in output or 'failures=0' not in output:
            failures.append('Incomplete execution ' + label)
        return output

    memory = read('reset-memory-results.json')
    expected = [(p, a) for p in (0, 1) for a in (1000, 19000)]
    if [(r['policy'], r['assertion_ns']) for r in memory['runs']] != expected or len(memory['negative']) != 2:
        failures.append('Memory reset matrix')
    for row in memory['runs']:
        output = complete(row, 'memory')
        match = re.search(r'max_we_inhibit_ns=([\d.]+)', output)
        if 'active_write_cuts=12 stopped_clocks=2' not in output or not match or float(match[1]) > 100:
            failures.append('Memory pin deadline/coverage')
    for row, message in zip(memory['negative'], ['memory bank reset before physical WE inhibition', 'independent RAM pin address changed while WE low']):
        complete(row, 'memory fault', message)
    for mode, policy in [('ideal', 1), ('timed', 0), ('timed', 1)]:
        name = f'scan-policy{policy}-{mode}/system-scan-{mode}.json'
        scan = read(name)
        output = complete(scan, name)
        if scan['binary_reset_policy'] != policy or 'scan_frames=5 completed_column_reads=40' not in output or 'stopped_cpu_checks=1 reset_pending_checks=1' not in output:
            failures.append('Scan coverage ' + name)
        compiled = scan['compiled_bench']
        if digest(ROOT / compiled['path']) != compiled['sha256']:
            failures.append('Compiled scan snapshot ' + name)
        text = (ROOT / compiled['path']).read_text()
        if 'dut(memory.cpu_core_clk,memory.cpu_reset_n' not in text or f'.RESET_POLICY({policy})' not in text:
            failures.append('Scan uses wrong reset/clock ' + name)
    for mode, quick, count in [('ideal', False, 6886), ('timed', True, 1062)]:
        name = 'vectors/verified-cpu-' + mode + ('-quick' if quick else '') + '.json'
        report = read(name)
        output = complete(report['runs'][0], name)
        if f'instruction_cases={count}' not in output:
            failures.append('Instruction coverage ' + name)
        bench = OUT / f'vectors/verified-tb_rtl_cpu-{mode}.sv'
        if digest(bench) != report['adapted_bench_sha256'] or 'dut(memory.cpu_core_clk,memory.cpu_reset_n' not in bench.read_text():
            failures.append('Instruction reset/bench ' + name)
    program = read('program/system-program-ideal.json')
    output = complete(program['runs'][0], 'program')
    if not program['runs'][0].get('frame_matches_reference') or 'retirements=132197 transactions=232576' not in output or 'frame_pixels=76800' not in output or 'fixture_defaults=0' not in output:
        failures.append('Program unknown SRAM/frame')
    if digest(OUT / 'program/system-tb_rtl_program-ideal.sv') != program['adapted_bench_sha256']:
        failures.append('Program compiled snapshot')
    hold = read('hold-up-results.json')
    if len(hold['runs']) != 64 or len(hold['negative']) != 3 or hold['assumptions']['supervisor_output_load_qualified'] or hold['assumptions']['max_bank_assert_after_raw_s'] != 20e-6:
        failures.append('Conditional hold-up scope')
    if not all(row['passed'] and row['residual_passed'] and row['exit'] == 0 for row in hold['runs'] + hold['negative']):
        failures.append('Hold-up completion')
    graph = read('native/schematic-check.json')
    if (graph['components'], graph['ics'], graph['pins'], graph['no_connects']) != (22, 8, 132, 10):
        failures.append('Native inventory')
    erc = read('native/erc-summary.json')
    if erc['exit'] != 5 or erc['erc_passed'] or sum(erc['violation_counts'].values()) != 12:
        failures.append('ERC falsely approved/changed')
    loads = read('load-check.json')
    if len(loads['nets']) != 14 or max(row['input_count'] for row in loads['nets']) != 4 or loads['supervisor_interface']['guaranteed_test_load_budget_closed']:
        failures.append('Load scope')
    for item in read('research/sources.json')['files']:
        if digest(ROOT / item['path']) != item['sha256'] or digest(ROOT / item['extraction']) != item['extraction_sha256']:
            failures.append('Research source ' + item['path'])
    for item in read('adapter-origin.json')['files']:
        if digest(ROOT / item['path']) != item['sha256']:
            failures.append('Adapter provenance ' + item['path'])
    for item in read('check-origin.json')['transformations']:
        if digest(ROOT / item['source']) != item['source_sha256'] or digest(ROOT / item['target']) != item['target_sha256']:
            failures.append('Checker provenance ' + item['target'])
    environment = read('environment.json')
    if len(environment['versions']) != 5 or len(environment['shared_rom_inputs']) != 4:
        failures.append('Environment missing')
    for item in environment['shared_rom_inputs']:
        if digest(ROOT / item['path']) != item['sha256'] or not item['unchanged_from_baseline']:
            failures.append('Firmware changed ' + item['path'])
    if '--check' in sys.argv:
        manifest = json.loads(MANIFEST.read_text())
        for item in manifest['files']:
            path = (ROOT / item['path']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or digest(path) != item['sha256']:
                failures.append(item['path'])
        print(json.dumps({'checked': len(manifest['files']), 'failures': failures, 'production_released': False}))
        return int(bool(failures))
    if not failures:
        failures += audit_history()
    if failures:
        print(json.dumps({'failures': failures}))
        return 1
    (OUT / 'acceptance.json').write_text(json.dumps({'date': '2026-11-26', 'active_write_cuts': 48,
        'max_selected_we_inhibit_ns': 80, 'conditional_hold_up_cases': 64, 'hold_up_negatives': 3,
        'ideal_instruction_cases': 6886, 'selected_timed_instruction_cases': 1062,
        'ideal_boot_retirements': 132197, 'frame_pixels': 76800, 'scan_policies_timed': [0, 1],
        'supervisor_output_load_qualified': False, 'partial_erc_violations': 12,
        'full_program_timed_executed': False, 'production_released': False}, indent=2) + '\n')
    names = ['.gitattributes', 'README.md', 'AGENTS.md', 'PROVENANCE.md', 'ROADMAP.md', 'DECISIONS.md', 'CHANGELOG.md',
             'docs/engineering/NET20.md', 'docs/engineering/VALIDATION_STATUS.md', 'docs/engineering/PRODUCTION_GATES.md']
    names += ['tools/' + name + '.py' for name in ['build_system_reset', 'make_reset_system', 'run_reset_scan',
        'run_reset_memory', 'run_reset_vectors', 'run_reset_program', 'prepare_reset_checks', 'run_system_hold_up',
        'check_system_reset_erc', 'check_reset_loads', 'collect_reset_research', 'record_reset_environment',
        'update_net20_continuity', 'record_net20_manifest']]
    files = {ROOT / name for name in names}
    for folder in ['hardware/system_reset', 'sim/net20', 'references/net20', 'verification/net20']:
        files.update(p for p in (ROOT / folder).rglob('*') if p.is_file() and p != MANIFEST and p.suffix != '.kicad_prl' and '__pycache__' not in p.parts)
    manifest = {'iteration': 'NET-20A', 'date': '2026-11-26', 'base_git_commit': BASE,
                'scope': 'Native reset distribution integrated digitally, explicit supervisor CL gap and conditional hold-up; no fabrication or analog/PVT/MTBF signoff.',
                'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'recorded': len(files), 'prior_snapshots': 23, 'failures': failures, 'production_released': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
