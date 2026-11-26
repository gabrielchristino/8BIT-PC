"""Audit NET21 selected evidence and 24 immutable predecessor snapshots."""
import hashlib
import inspect
import json
from pathlib import Path
import re
import subprocess
import sys
import record_net14a_manifest as original

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net21'
BASE = '5c8eba51346be08b5f2ed53da111aef970f71133'
MANIFEST = OUT / 'manifest.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


exec(inspect.getsource(original.audit_history).replace('verification/net13/', 'verification/net20/'), globals())


def main():
    failures = []

    def read(name):
        data = json.loads((OUT / name).read_text())
        if data.get('failures'):
            failures.append('Failed accepted report ' + name)
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
                failures.append('Negative completion ' + label)
        elif result.get('exit') != 0 or 'RESULT ' not in output or 'failures=0' not in output:
            failures.append('Incomplete execution ' + label)
        return output

    memory = read('reset-memory-results.json')
    if [(r['policy'], r['assertion_ns']) for r in memory['runs']] != [(p, a) for p in (0, 1) for a in (1000, 19000)] or len(memory['negative']) != 2:
        failures.append('Memory cut matrix')
    for row in memory['runs']:
        output = complete(row, 'memory')
        match = re.search(r'max_we_inhibit_ns=([\d.]+)', output)
        if 'active_write_cuts=12 stopped_clocks=2' not in output or not match or float(match[1]) > 100:
            failures.append('Memory deadline/coverage')
    for row, message in zip(memory['negative'], ['memory bank reset before physical WE inhibition', 'independent RAM pin address changed while WE low']):
        complete(row, 'memory negative', message)
    actual = read('actual-cpu-write-reset.json')
    if [r['policy'] for r in actual['runs']] != [0, 1]:
        failures.append('Actual CPU policies')
    for row in actual['runs']:
        output = complete(row, 'actual CPU write')
        if 'actual_cpu_write_cuts=2 restarted_scans=2' not in output or 'fixture_defaults=0' not in output:
            failures.append('Actual CPU write coverage')
        match = re.search(r'max_we_inhibit_ns=([\d.]+)', output)
        if not match or float(match[1]) > 100:
            failures.append('Actual CPU WE deadline')
    for policy in (0, 1):
        name = f'scan-policy{policy}-timed/system-scan-timed.json'
        scan = read(name)
        output = complete(scan, name)
        if scan['binary_reset_policy'] != policy or 'scan_frames=5 completed_column_reads=40' not in output or 'stopped_cpu_checks=1 reset_pending_checks=1' not in output:
            failures.append('Scan coverage ' + name)
        bench = scan['compiled_bench']
        if digest(ROOT / bench['path']) != bench['sha256'] or 'dut(memory.cpu_core_clk,memory.cpu_reset_n' not in (ROOT / bench['path']).read_text():
            failures.append('Scan actual reset/compiled bench')
    window = read('research-window.json')
    if not window['chosen']['passed'] or len(window['negative']) != 4 or any(row['passed'] for row in window['negative']) or window['chosen']['nominal_rail_v'] != 5.392:
        failures.append('Window coverage/rail')
    hold = read('hold-up-results.json')
    if len(hold['runs']) != 64 or len(hold['negative']) != 3 or not all(row['passed'] and row['residual_passed'] and row['exit'] == 0 for row in hold['runs'] + hold['negative']):
        failures.append('Hold-up completion')
    if hold['assumptions']['detect_delay_budget_s'] != 20e-6 or hold['assumptions']['supervisor_output_load_qualified'] or hold['analytic_bounds']['rail_at_bank_lower_v'] <= 4.5:
        failures.append('Hold-up qualification scope')
    line = read('reset-line-results.json')
    if len(line['runs']) != 24 or len(line['negative']) != 1 or not all(row['passed'] and row['exit'] == 0 for row in line['runs'] + line['negative']):
        failures.append('Line RC completion')
    if line['summary']['minimum_high_v'] <= 3.85 or line['summary']['maximum_low_v'] >= 1.35:
        failures.append('Line levels')
    graph = read('native/schematic-check.json')
    if (graph['components'], graph['ics'], graph['pins'], graph['no_connects']) != (22, 8, 132, 9) or not graph['raw_load_budget_within_test_cl'] or graph['analog_supervisor_implemented']:
        failures.append('Graph/supervisor scope')
    erc = read('native/erc-summary.json')
    if erc['exit'] != 5 or erc['erc_passed'] or sum(erc['violation_counts'].values()) != 12:
        failures.append('Partial ERC falsely approved/changed')
    topology = read('native/topology-check.json')
    if not topology['positive_projection_matches'] or len(topology['negative']) != 2 or not all(row['passed'] for row in topology['negative']):
        failures.append('Topology calibration')
    loads = read('load-check.json')
    if len(loads['nets']) != 16 or max(row['input_count'] for row in loads['nets']) != 4 or not loads['supervisor_interface']['budget_within_test_load'] or loads['supervisor_interface']['guaranteed_test_load_budget_closed']:
        failures.append('Load budget vs physical scope')
    inventory = read('load-inventory.json')
    if inventory['candidate_union_ic_count'] != 458 or len(inventory['power_budget']) != 30 or inventory['global_board_integrated'] or any(row['board_icc_upper_bound_a'] is not None for row in inventory['power_budget']):
        failures.append('Inventory/current scope')
    for item in read('check-origin.json')['transformations']:
        if digest(ROOT / item['source']) != item['source_sha256'] or digest(ROOT / item['target']) != item['target_sha256']:
            failures.append('Transformation changed ' + item['target'])
    environment = read('environment.json')
    if len(environment['versions']) != 5 or len(environment['shared_rom_inputs']) != 4:
        failures.append('Environment')
    for item in environment['shared_rom_inputs']:
        if digest(ROOT / item['path']) != item['sha256'] or not item['unchanged_from_baseline']:
            failures.append('ROM ' + item['path'])
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
    (OUT / 'acceptance.json').write_text(json.dumps({'date': '2026-11-26', 'master_active_write_cuts': 48,
        'selected_max_we_inhibit_ns': 94, 'actual_cpu_write_cuts': 4, 'actual_cpu_restarted_scans': 4,
        'scan_timed_policies': [0, 1], 'hold_up_cases': 64, 'hold_up_negatives': 3, 'line_rc_cases': 24,
        'line_rc_negatives': 1, 'window_negatives': 4, 'topology_negatives': 2,
        'raw_cap_budget_pf': 20, 'supervisor_test_cl_pf': 50, 'raw_cap_budget_within_test_condition': True,
        'analog_supervisor_qualified': False, 'nominal_rail_proposal_v': 5.392, 'partial_erc_violations': 12,
        'full_program_or_instruction_vectors_rerun_for_net21': False, 'production_released': False}, indent=2) + '\n')
    names = ['.gitattributes', 'README.md', 'AGENTS.md', 'PROVENANCE.md', 'ROADMAP.md', 'DECISIONS.md', 'CHANGELOG.md',
             'docs/engineering/NET21.md', 'docs/engineering/VALIDATION_STATUS.md', 'docs/engineering/PRODUCTION_GATES.md',
             'references/net20/tps3808.pdf', 'references/ti/sn74ahc14.pdf',
             'references/power-candidates/tps63070.pdf', 'references/power-candidates/tps25947.pdf']
    names += ['tools/' + name + '.py' for name in ['build_schmitt_reset', 'prepare_schmitt_checks', 'run_schmitt_memory',
        'run_schmitt_scan', 'run_schmitt_cpu_fault', 'run_schmitt_hold_up', 'run_schmitt_power_window',
        'check_schmitt_interface', 'check_schmitt_loads', 'check_schmitt_topology', 'inventory_schmitt_system',
        'check_schmitt_reset_erc', 'record_schmitt_environment', 'update_net21_continuity', 'record_net21_manifest']]
    files = {ROOT / name for name in names}
    for folder in ['hardware/schmitt_reset', 'sim/net21', 'verification/net21']:
        files.update(p for p in (ROOT / folder).rglob('*') if p.is_file() and p != MANIFEST and p.suffix != '.kicad_prl' and '__pycache__' not in p.parts)
    manifest = {'iteration': 'NET-21A', 'date': '2026-11-26', 'base_git_commit': BASE,
                'scope': 'Schmitt/supervisor load budget and selected digital/RC/DC/hold-up tests. Conditional power/current/POR, no regulator or fabrication/PVT/MTBF approval.',
                'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'recorded': len(files), 'prior_snapshots': 24, 'failures': failures, 'production_released': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
