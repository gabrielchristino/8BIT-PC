"""Verify the reviewed project subset and immutable prior engineering snapshots."""
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
import record_net14a_manifest as original

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/export-2026-11-26'
BASE = '332fd31b743d6a61e5f8d691364454f47ce6ab52'
MANIFEST = OUT / 'manifest.json'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


exec(inspect.getsource(original.audit_history).replace('verification/net13/', 'verification/net18/'), globals())


def main():
    failures = []
    for folder in ('archive/export-2026-11-26', 'archive/export-pages-2026-11-26'):
        data = json.loads((ROOT / folder / 'manifest.json').read_text())
        if digest(ROOT / data['tool']['path']) != data['tool']['sha256']:
            failures.append('Recovery tool changed ' + data['tool']['path'])
        for item in data['files']:
            p = (ROOT / item['path']).resolve()
            if not p.is_relative_to((ROOT / folder).resolve()) or not p.is_file() or digest(p) != item['sha256']:
                failures.append(item['path'])
    archive = json.loads((ROOT / 'archive/export-2026-11-26/manifest.json').read_text())
    if (archive['available_payloads'], archive['missing_payloads'], len(archive['conversations'])) != (240, 33, 4) or archive['source_archive']['published'] or archive['all_chat_history_complete']:
        failures.append('Recovery scope')
    reports = {}
    for name in ('historical-audits.json', 'source-coverage.json'):
        data = json.loads((OUT / name).read_text())
        reports[name] = data
        if data['failures']:
            failures.append('Failed report ' + name)
        for item in data['sources']:
            if digest(ROOT / item['path']) != item['sha256']:
                failures.append('Changed tested source ' + item['path'])
    audits = reports['historical-audits.json']
    if len(audits['runs']) != 2 or not all(r['passed'] and r['bytes_identical'] and r['exit'] == 0 for r in audits['runs']) or not audits['historical_rev983_diagnostic_asm_still_missing']:
        failures.append('Historical reproduction/scope')
    coverage = reports['source-coverage.json']
    if coverage['unique_payload_hashes'] != 228 or coverage['message_records_including_branch_overlap'] != 1304 or coverage['distinct_missing_originating_message_ids'] != 72:
        failures.append('Coverage changed')
    if '--check' in sys.argv:
        manifest = json.loads(MANIFEST.read_text())
        for item in manifest['files']:
            path = (ROOT / item['path']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or digest(path) != item['sha256']:
                failures.append(item['path'])
        print(json.dumps({'checked_files': len(manifest['files']), 'failures': failures, 'all_history_recovered': False, 'production_released': False}))
        return int(bool(failures))
    if not failures:
        failures += audit_history()
    if failures:
        print(json.dumps({'failures': failures}))
        return 1
    (OUT / 'acceptance.json').write_text(json.dumps({'date': '2026-11-26', 'available_payloads': 240, 'unique_payload_hashes': 228,
        'missing_payloads': 33, 'missing_message_origin_ids': 72, 'historical_generators_reproduced_byte_identical': 2,
        'all_history_recovered': False, 'account_export_published': False, 'production_released': False}, indent=2) + '\n')
    names = ['.gitattributes', 'README.md', 'AGENTS.md', 'PROVENANCE.md', 'ROADMAP.md', 'DECISIONS.md', 'CHANGELOG.md',
             'docs/LACUNAS.md', 'docs/INVENTORY.md', 'docs/EXPORT_RECOVERY_2026-11-26.md', 'docs/engineering/VALIDATION_STATUS.md']
    names += ['tools/' + name + '.py' for name in ('recover_local_export', 'recover_export_pages', 'verify_export_audits', 'inventory_export_coverage', 'record_export_manifest')]
    files = {ROOT / name for name in names}
    for folder in ('archive/export-2026-11-26', 'archive/export-pages-2026-11-26', 'verification/export-2026-11-26'):
        files.update(p for p in (ROOT / folder).rglob('*') if p.is_file() and p != MANIFEST and '__pycache__' not in p.parts)
    data = {'date': '2026-11-26', 'base_git_commit': BASE, 'scope': 'Reviewed ISA-1 subset of local account export and reproduced historical symbolic generators; explicit coverage gaps',
            'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)} for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({'recorded': len(files), 'bytes': sum(p.stat().st_size for p in files), 'prior_snapshots': 21, 'failures': failures}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
