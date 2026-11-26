"""Hash original downloads, verify exact vendor ZIP extraction and tool versions."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net18'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    metadata = json.loads((OUT / 'research/sources.json').read_text())
    failures, rows = [], []
    for item in metadata['files']:
        if digest(ROOT / item['path']) != item['sha256']:
            failures.append(item['path'])
        if item.get('extraction_sha256') and digest(ROOT / item['extraction']) != item['extraction_sha256']:
            failures.append(item['extraction'])
    folder = ROOT / 'references/vendor/tps63070'
    with zipfile.ZipFile(folder / 'slvmbp8a.zip') as archive:
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            path = (folder / 'original' / entry.filename).resolve()
            if not path.is_relative_to((folder / 'original').resolve()):
                raise ValueError('Unsafe archive path')
            original = archive.read(entry)
            okay = path.is_file() and path.read_bytes() == original
            rows.append({'entry': entry.filename, 'path': path.relative_to(ROOT).as_posix(),
                         'bytes': len(original), 'sha256': hashlib.sha256(original).hexdigest(), 'passed': okay})
            if not okay:
                failures.append(entry.filename)
    versions = {}
    for name, cmd in [('python', ['python3', '--version']), ('ngspice', ['ngspice', '--version']),
                      ('iverilog', ['iverilog', '-V']), ('pdftotext', ['pdftotext', '-v'])]:
        run = subprocess.run(cmd, capture_output=True, text=True)
        versions[name] = {'command': cmd, 'exit': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr}
    report = {'date': '2026-11-26', 'downloads_checked': len(metadata['files']), 'zip_entries': rows,
              'versions': versions, 'failures': failures,
              'copyright': 'TI original notices retained, no new license applied or general redistribution permission inferred',
              'sources': [{'path': n, 'sha256': digest(ROOT / n)} for n in ('tools/check_power_references.py', 'verification/net18/research/sources.json')]}
    (OUT / 'references-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'downloads_checked': len(metadata['files']), 'zip_entries': len(rows), 'failures': failures}))
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
