"""Expose export graph/library gaps and exact duplicates without guessing versions."""
import collections
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/export-2026-11-26'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    archive = ROOT / 'archive/export-2026-11-26'
    manifest = json.loads((archive / 'manifest.json').read_text())
    assets = json.loads((archive / 'library-project.json').read_text())
    messages = {}
    for row in manifest['conversations']:
        conversation = json.loads((ROOT / row['json']).read_text())
        messages[row['id']] = {node['message']['id'] for node in conversation['mapping'].values() if node.get('message')}
    available = [x for x in assets if x['available']]
    sizes = {x['bytes'] for x in available}
    baseline = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    hashes = collections.defaultdict(list)
    for name in baseline:
        if name.startswith(('archive/export-2026-11-26/', 'archive/export-pages-2026-11-26/')):
            continue
        if not name or not (name.startswith(('archive/', 'revisions/')) or name.startswith(('isa1_rev', 'ISA-1_REV'))):
            continue
        path = ROOT / name
        if path.is_file() and path.stat().st_size in sizes:
            hashes[digest(path)].append(name)
    missing_origins = [{k: x.get(k) for k in ('file_id', 'file_name', 'origination_thread_id', 'origination_message_id', 'available')}
                       for x in assets if x.get('origination_message_id') not in messages[x['origination_thread_id']]]
    matches = [{'file_id': x['file_id'], 'path': x['path'], 'sha256': x['sha256'],
                'existing_exact_byte_matches': hashes.get(x['sha256'], [])} for x in available]
    report = {'date': '2026-11-26', 'scope': 'Metadata/graph/hash coverage only, no assembly of mixed revisions or qualification of archived code',
              'conversations': len(manifest['conversations']),
              'message_records_including_branch_overlap': sum(x['messages'] for x in manifest['conversations']),
              'available_payloads': len(available), 'unique_payload_hashes': len({x['sha256'] for x in available}),
              'missing_payloads': len(assets) - len(available),
              'available_extensions': dict(collections.Counter(x['file_extension'] for x in available)),
              'metadata_size_mismatches': [x['file_id'] for x in available if not x['metadata_size_matches']],
              'originating_message_ids_not_in_exported_graph': missing_origins,
              'distinct_missing_originating_message_ids': len({x['origination_message_id'] for x in missing_origins}),
              'warning': 'Library metadata links 171 records to originating message IDs absent from the selected conversation graphs. Do not claim all chat/history recovered or infer a missing message from an asset.',
              'existing_byte_matches': matches,
              'sources': [{'path': n, 'sha256': digest(ROOT / n)} for n in ('tools/inventory_export_coverage.py', 'archive/export-2026-11-26/manifest.json', 'archive/export-2026-11-26/library-project.json')],
              'failures': [] if len(missing_origins) == 171 and len(available) == 240 and len({x['sha256'] for x in available}) == 228 else ['Unexpected coverage; review source snapshot']}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'source-coverage.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'messages_with_overlap': report['message_records_including_branch_overlap'], 'available_payloads': len(available),
                      'unique_payload_hashes': report['unique_payload_hashes'], 'missing_payloads': report['missing_payloads'],
                      'records_with_missing_originating_message_ids': len(missing_origins),
                      'distinct_missing_originating_message_ids': report['distinct_missing_originating_message_ids'],
                      'files_matching_older_archive_bytes': sum(bool(x['existing_exact_byte_matches']) for x in matches), 'failures': report['failures']}))
    return int(bool(report['failures']))


if __name__ == '__main__':
    raise SystemExit(main())
