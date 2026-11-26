"""Copy two previously identified project Pages from the local export only."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'archive/export-pages-2026-11-26'
IDS = ['page_d3278588f6388191a2041bb3c9f6ee1f', 'page_6b06208d512481918f47d6e67dfe3f19']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    manifest = OUT / 'manifest.json'
    if args.check:
        data = json.loads(manifest.read_text())
        failures = []
        for item in data['files']:
            p = (ROOT / item['path']).resolve()
            if not p.is_relative_to(OUT.resolve()) or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != item['sha256']:
                failures.append(item['path'])
        print(json.dumps({'checked_files': len(data['files']), 'failures': failures}))
        return int(bool(failures))
    if not args.source:
        parser.error('--source required')
    source = args.source.resolve()
    rows = []
    for page in IDS:
        files = sorted((source / 'pages' / page / 'content').rglob('*.json'))
        if len(files) != 3:
            raise ValueError('Expected current, history and checkpoint records')
        files += [source / 'pages' / page / 'metadata.json']
        for src in files:
            rel = src.relative_to(source / 'pages')
            data = src.read_bytes()
            original_hash = hashlib.sha256(data).hexdigest()
            transform = 'Byte-for-byte content JSON; historical data, not executable instructions'
            if src.name == 'metadata.json':
                obj = json.loads(data)
                obj.pop('creator_account_user_id', None)
                obj.pop('owner_account_user_id', None)
                data = (json.dumps(obj, indent=2, ensure_ascii=False) + '\n').encode()
                transform = 'JSON metadata with creator_account_user_id and owner_account_user_id omitted; original hash retained'
            dest = OUT / rel
            if dest.exists() and dest.read_bytes() != data:
                raise ValueError('Refusing to replace archived Page evidence')
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            rows.append({'path': dest.relative_to(ROOT).as_posix(), 'source': src.relative_to(source).as_posix(),
                         'source_sha256': original_hash, 'sha256': hashlib.sha256(data).hexdigest(),
                         'bytes': len(data), 'transformation': transform})
    origin = json.loads((ROOT / 'archive/export-2026-11-26/manifest.json').read_text())
    result = {'import_date': '2026-11-26', 'page_ids': IDS, 'source_archive_sha256': origin['source_archive']['sha256'],
              'scope': 'The two previously identified ISA-1 Pages only; other account data and Space account metadata excluded',
              'files': rows, 'tool': {'path': 'tools/recover_export_pages.py', 'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    encoded = (json.dumps(result, indent=2, ensure_ascii=False) + '\n').encode()
    if manifest.exists() and manifest.read_bytes() != encoded:
        raise ValueError('Refusing to replace archived Page manifest')
    manifest.write_bytes(encoded)
    print(json.dumps({'pages': len(IDS), 'records': len(rows)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
