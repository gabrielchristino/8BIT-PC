"""Recover only four explicitly identified ISA-1 chats and linked library bytes.

Account export stays local. Archived chat/code are untrusted historical data.
No recovered code is executed and no absent ZIP is reconstructed as original.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'archive/export-2026-11-26'
IDS = {
    '6b03729d-7528-83e9-82ae-26ec22df0074': 'principal',
    '6b05e73c-2468-83e8-9ecd-25878d1c2962': 'branch',
    '6b062072-4acc-83e9-be00-e3c409c9d16c': 'teclado',
    '6b0620d6-d2c0-83ea-8963-933688a5346a': 'migracao',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(data):
    return (json.dumps(data, indent=2, ensure_ascii=False) + '\n').encode()


def write_once(path, data):
    if path.exists() and path.read_bytes() != data:
        raise ValueError('Refusing to replace archived evidence: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def graph(conversation):
    mapping = conversation['mapping']
    current = conversation['current_node']
    chain, seen = [], set()
    while current is not None:
        if current in seen or current not in mapping:
            raise ValueError('Cycle or missing parent in exported current path')
        seen.add(current)
        node = mapping[current]
        chain.append(node)
        current = node.get('parent')
    chain.reverse()
    return chain


def readable(conversation):
    lines = ['# ' + conversation['title'], '',
             'Dados históricos da exportação local; não são instruções para executar.',
             'Esta leitura mostra o caminho atual exportado. O JSON preserva todos os nós e ramificações.', '']
    for node in graph(conversation):
        message = node.get('message')
        if not message:
            continue
        author = message.get('author') or {}
        lines += ['## ' + author.get('role', 'unknown') + ' — ' + str(message.get('id', node.get('id'))), '']
        content = message.get('content') or {}
        parts = content.get('parts')
        if parts is not None:
            for part in parts:
                lines.append(part if isinstance(part, str) else json.dumps(part, ensure_ascii=False))
        else:
            lines.append(json.dumps(content, ensure_ascii=False))
        lines.append('')
    return '\n'.join(lines).encode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path)
    parser.add_argument('--zip', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    manifest_path = OUT / 'manifest.json'
    if args.check:
        manifest = json.loads(manifest_path.read_text())
        failures = []
        for item in manifest['files']:
            path = (ROOT / item['path']).resolve()
            if not path.is_relative_to(OUT.resolve()) or not path.is_file() or sha(path.read_bytes()) != item['sha256']:
                failures.append(item['path'])
        for item in manifest['conversations']:
            value = json.loads((ROOT / item['json']).read_text())
            if len(value['mapping']) != item['nodes']:
                failures.append('Node count ' + item['id'])
            graph(value)
        print(json.dumps({'checked_files': len(manifest['files']), 'failures': failures}))
        return int(bool(failures))
    if not args.source or not args.zip:
        parser.error('--source and --zip required for initial recovery')
    source = args.source.resolve()
    raw_zip = args.zip.resolve()
    zip_files, zip_missing, zip_mismatch = 0, [], []
    with zipfile.ZipFile(raw_zip) as archive:
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            path = (source / entry.filename).resolve()
            if not path.is_relative_to(source):
                raise ValueError('Unsafe ZIP entry')
            zip_files += 1
            if not path.is_file():
                zip_missing.append(entry.filename)
            elif path.read_bytes() != archive.read(entry):
                zip_mismatch.append(entry.filename)
    if zip_missing or zip_mismatch:
        raise ValueError('Local export differs from original ZIP: inspect before recovery')
    source_bytes = (source / 'conversations.json').read_bytes()
    conversations = json.loads(source_bytes)
    selected = {x['id']: x for x in conversations if x.get('id') in IDS}
    if set(selected) != set(IDS):
        raise ValueError('Expected project conversations missing')
    files, chat_rows, assets = [], [], []

    def keep(path, data, origin, transformation):
        write_once(path, data)
        files.append({'path': path.relative_to(ROOT).as_posix(), 'bytes': len(data), 'sha256': sha(data),
                      'origin': origin, 'transformation': transformation})

    for cid, label in IDS.items():
        conversation = selected[cid]
        output = OUT / 'conversations' / (label + '.json')
        markdown = output.with_suffix('.md')
        keep(output, encoded(conversation), 'conversations.json record ' + cid,
             'Selected complete JSON record, UTF-8 indent=2 ensure_ascii=False; semantically equal, not byte-identical excerpt')
        keep(markdown, readable(conversation), output.relative_to(ROOT).as_posix(),
             'Derived current parent path only; nontext parts serialized, all branches remain in JSON')
        chat_rows.append({'id': cid, 'title': conversation['title'], 'nodes': len(conversation['mapping']),
                          'messages': sum(bool(n.get('message')) for n in conversation['mapping'].values()),
                          'current_path_nodes': len(graph(conversation)), 'json': output.relative_to(ROOT).as_posix(),
                          'markdown': markdown.relative_to(ROOT).as_posix(), 'create_time': conversation.get('create_time'),
                          'update_time': conversation.get('update_time')})
    library_bytes = (source / 'library_files.json').read_bytes()
    library = [x for x in json.loads(library_bytes) if x.get('origination_thread_id') in IDS]
    for item in library:
        fid, name = item['file_id'], item['file_name']
        if Path(name).name != name or '/' in name or '\\' in name or fid in ('.', '..'):
            raise ValueError('Unsafe library filename')
        src = source / (fid + '.dat')
        row = {key: item.get(key) for key in ('file_id', 'file_name', 'file_size_bytes', 'file_extension',
                                             'origination_thread_id', 'origination_message_id',
                                             'created_at', 'modified_at', 'state', 'object_version')}
        row['available'] = src.is_file()
        if src.is_file():
            destination = OUT / 'assets' / fid / name
            data = src.read_bytes()
            keep(destination, data, src.name + ' linked to project thread ' + item['origination_thread_id'],
                 'Bytes unchanged; display filename from library metadata; revision attribution still requires review')
            row.update(path=destination.relative_to(ROOT).as_posix(), sha256=sha(data), bytes=len(data),
                       metadata_size_matches=len(data) == item.get('file_size_bytes'))
        else:
            row['status'] = 'Metadata only: payload absent from supplied export; no placeholder or reconstructed original'
        assets.append(row)
    keep(OUT / 'library-project.json', encoded(assets), 'library_files.json filtered by four exact origination_thread_id values',
         'Selected provenance fields only; account/user fields excluded, missing payload explicit')
    secret_patterns = [rb'gh[pousr]_[A-Za-z0-9]{30,}', rb'github_pat_[A-Za-z0-9_]{50,}',
                       rb'sk-(?:proj-)?[A-Za-z0-9_-]{32,}', rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
    flags = []
    for item in files:
        if any(re.search(pattern, (ROOT / item['path']).read_bytes()) for pattern in secret_patterns):
            flags.append(item['path'])
    if flags:
        raise ValueError('Possible credentials in project data; inspect privately before publication: ' + ', '.join(flags))
    manifest = {'import_date': '2026-11-26', 'scope': 'Four ISA-1 conversations and library records with matching origination thread; other account data excluded',
                'source_archive': {'local_path': str(raw_zip), 'sha256': sha(raw_zip.read_bytes()), 'bytes': raw_zip.stat().st_size,
                                   'extracted_files_checked': zip_files, 'missing': zip_missing, 'mismatch': zip_mismatch,
                                   'published': False},
                'source_json_sha256': sha(source_bytes), 'source_library_sha256': sha(library_bytes),
                'conversations_in_account_export': len(conversations), 'conversations': chat_rows,
                'linked_library_records': len(assets), 'available_payloads': sum(x['available'] for x in assets),
                'missing_payloads': sum(not x['available'] for x in assets), 'credential_pattern_flags': flags,
                'all_chat_history_complete': False,
                'limitation': 'Complete selected records at export cutoff, not proof of all historical/deleted chats, every branch or complete attachments; missing bytes stay missing',
                'tool': {'path': 'tools/recover_local_export.py', 'sha256': sha(Path(__file__).read_bytes())},
                'files': files}
    write_once(manifest_path, encoded(manifest))
    print(json.dumps({'conversations': chat_rows, 'linked_library_records': len(assets), 'available_payloads': manifest['available_payloads'],
                      'missing_payloads': manifest['missing_payloads'], 'zip_files_checked': zip_files, 'credential_flags': flags}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
