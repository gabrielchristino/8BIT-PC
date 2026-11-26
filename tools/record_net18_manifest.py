"""Audit NET18 conditional evidence and twenty immutable Git snapshots."""
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
import record_net14a_manifest as original

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net18'
BASE = 'b439a3aa84505654ea064e0ccd6bc1e3636b4c0b'
MANIFEST = OUT / 'manifest.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


exec(inspect.getsource(original.audit_history).replace('verification/net13/', 'verification/net17/'), globals())


def main():
    failures = []

    def read(name):
        data = json.loads((OUT / name).read_text())
        if data.get('failures'):
            failures.append('Failed report ' + name)
        for source in data.get('sources', []):
            if digest(ROOT / source['path']) != source['sha256']:
                failures.append('Changed tested source ' + source['path'])
        return data

    hold = read('hold-up-results.json')
    if len(hold['runs']) != 64 or len(hold['negative']) != 3:
        failures.append('Hold-up coverage')
    for row in hold['runs'] + hold['negative']:
        if row['exit'] != 0 or not row['passed'] or not row['residual_passed'] or len(row['measures']) != 3:
            failures.append('Hold-up completion ' + str(row['index']))
        if row['negative'] and min(row['measures'].values()) >= 4.5:
            failures.append('Negative failed to violate rail floor')
    if hold['production_released'] or hold['analytic_bounds']['rail_at_bank_lower_v'] <= 4.5:
        failures.append('Hold-up scope')
    window = read('window-results.json')
    if not window['chosen']['passed'] or len(window['negative']) != 3 or any(r['passed'] for r in window['negative']):
        failures.append('DC window')
    inventory = read('load-inventory.json')
    if inventory['integrated_candidate_ic_count'] != 456 or inventory['global_board_integrated'] or len(inventory['power_budget']) != 29:
        failures.append('Inventory scope')
    if any(row['icc_guaranteed_max_a'] is not None for row in inventory['power_budget']):
        failures.append('Unreviewed consumption claim')
    graph = read('native/schematic-check.json')
    if (graph['components'], graph['ics'], graph['pins'], graph['no_connects']) != (18, 6, 100, 14) or graph['supervisor_analog_model_implemented']:
        failures.append('Pin graph / analog projection')
    for name, count, neg in [('native/results.json', 16, 2), ('native/apertures.json', 2, 1)]:
        report = read(name)
        if len(report['runs']) != count or len(report['negative']) != neg:
            failures.append('Digital coverage ' + name)
        for row in report['runs']:
            output = row.get('execution', {})
            if not row['passed'] or row['compile']['exit'] or output.get('exit') != 0 or 'RESULT ' not in output.get('stdout', '') or 'failures=0' not in output['stdout']:
                failures.append('Digital completion ' + name)
        if not all(row['passed'] and row['compile']['exit'] == 0 and row['execution']['exit'] != 0 for row in report['negative']):
            failures.append('Digital negatives ' + name)
    erc = read('native/erc-summary.json')
    if erc['exit'] != 5 or sum(erc['violation_counts'].values()) != 5 or erc['erc_passed'] or erc['board_release']:
        failures.append('Partial ERC falsely approved or changed')
    topology = read('native/topology-negative.json')
    if len(topology['negative']) != 2 or not all(row['passed'] for row in topology['negative']):
        failures.append('Topology negatives')
    read('native/preparation-check.json')
    for item in read('native/check-origin.json')['files']:
        if digest(ROOT / item['base']) != item['base_sha256'] or digest(ROOT / item['generated']) != item['generated_sha256']:
            failures.append('Fixture transformation ' + item['generated'])
    refs = read('references-check.json')
    if refs['downloads_checked'] != 9 or len(refs['zip_entries']) != 10 or not all(r['passed'] for r in refs['zip_entries']):
        failures.append('Vendor original integrity')
    vendor = read('vendor-trial/solver-trials.json')
    if len(vendor['runs']) != 3 or any(r['completed'] or r['final_v'] is not None for r in vendor['runs']):
        failures.append('Vendor trial scope changed: review rather than silently promote')
    if not vendor['library_unchanged']:
        failures.append('Vendor library changed')
    if '--check' in sys.argv:
        manifest = json.loads(MANIFEST.read_text())
        for item in manifest['files']:
            path = (ROOT / item['path']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or digest(path) != item['sha256']:
                failures.append(item['path'])
        print(json.dumps({'checked': len(manifest['files']), 'failures': failures, 'regulator_qualified': False, 'production_released': False}))
        return int(bool(failures))
    if not failures:
        failures += audit_history()
    if failures:
        print(json.dumps({'failures': failures}))
        return 1
    (OUT / 'acceptance.json').write_text(json.dumps({'date': '2026-11-26', 'scope': 'Conditional energy/DC and pin-derived reset forcepoint tests only',
        'hold_up_scenarios': 64, 'digital_reset_configurations': 16, 'partial_erc_violations': 5,
        'regulator_vendor_trials_completed': 0, 'global_current_budget_closed': False,
        'full_cpu_integration_executed': False, 'physical_por_reverse_fault_qualified': False,
        'regulator_qualified': False, 'production_released': False}, indent=2) + '\n')
    names = ['.gitattributes', 'README.md', 'AGENTS.md', 'PROVENANCE.md', 'ROADMAP.md', 'DECISIONS.md', 'CHANGELOG.md',
             'docs/engineering/NET18.md', 'docs/engineering/VALIDATION_STATUS.md', 'docs/engineering/PRODUCTION_GATES.md']
    names += ['tools/' + name + '.py' for name in ('inventory_power_loads', 'run_power_hold_up', 'run_power_window',
              'run_power_vendor', 'build_power_reset', 'prepare_power_reset_checks', 'run_power_reset',
              'run_power_apertures', 'check_power_topology', 'check_power_reset_erc', 'check_power_references', 'record_net18_manifest')]
    names += ['references/power-candidates/' + name + '.pdf' for name in
              ('ref31', 'tlv3501', 'tps25947', 'tps3703', 'tps3808', 'tps63020', 'tps63070', 'tusb320lai')]
    files = {ROOT / n for n in names}
    for folder in ('hardware/power_reset', 'sim/net18', 'verification/net18', 'references/vendor/tps63070'):
        files.update(p for p in (ROOT / folder).rglob('*') if p.is_file() and p != MANIFEST and p.suffix != '.kicad_prl' and '__pycache__' not in p.parts)
    manifest = {'iteration': 'NET-18', 'date': '2026-11-26', 'base_git_commit': BASE,
                'scope': 'Conditional DC/hold-up, supervisor topology and digital reset projection. Incomplete vendor regulator trials explicitly unapproved; no global/physical production signoff',
                'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p),
                           'origin': 'New NET18 work, identified intermediate or attributed original vendor source; not recovered historical project revision'} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'recorded': len(files), 'historical_snapshots': 20, 'bytes': sum(p.stat().st_size for p in files), 'failures': failures, 'production_released': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
