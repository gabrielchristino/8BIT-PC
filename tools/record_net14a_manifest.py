"""Audit the phase contract and historical snapshots without rewriting evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net14a'
BASE = '9fae1298a3cd74844d294464bfdd0541241815af'
MANIFEST = OUT / 'manifest.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def audit_history():
    prior = json.loads(git('show', BASE + ':verification/net13/baseline-integrity.json'))
    snapshots = [(x['git_commit'], x['manifest']) for x in prior] + [(BASE, 'verification/net13/manifest.json')]
    audits, entries = [], []
    for commit, name in snapshots:
        m = json.loads(git('show', commit + ':' + name))
        audit = {'git_commit': commit, 'manifest': name, 'checked': len(m['files']), 'failures': []}
        audits.append(audit)
        entries.extend((commit + ':' + x['path'], x['sha256'], audit) for x in m['files'])
    # Resolve all commit:path expressions, then hash each unique Git blob once.
    # This preserves snapshot scope and avoids repeatedly reading identical PDFs.
    refs = '\n'.join(x[0] for x in entries) + '\n'
    proc = subprocess.run(['git', 'cat-file', '--batch-check=%(objectname) %(objecttype)'],
                          input=refs.encode(), capture_output=True, cwd=ROOT, check=True)
    objects = proc.stdout.decode().splitlines()
    assert len(objects) == len(entries) and all(x.endswith(' blob') for x in objects)
    ids = [x.split()[0] for x in objects]
    unique = list(dict.fromkeys(ids))
    proc = subprocess.run(['git', 'cat-file', '--batch'], input=('\n'.join(unique) + '\n').encode(),
                          capture_output=True, cwd=ROOT, check=True)
    data = proc.stdout
    hashes, offset = {}, 0
    for oid in unique:
        end = data.index(b'\n', offset)
        header = data[offset:end].decode().split()
        assert header[0] == oid and header[1] == 'blob'
        size = int(header[2]); start = end + 1
        hashes[oid] = hashlib.sha256(data[start:start + size]).hexdigest()
        assert data[start + size:start + size + 1] == b'\n'
        offset = start + size + 1
    assert offset == len(data)
    for (reference, expected, audit), oid in zip(entries, ids):
        if hashes[oid] != expected:
            audit['failures'].append(reference)
    (OUT / 'baseline-integrity.json').write_text(json.dumps(audits, indent=2) + '\n')
    return [f for a in audits for f in a['failures']]


def main():
    report = json.loads((OUT / 'results.json').read_text())
    failures = list(report['failures'])
    for item in report['sources']:
        if digest(ROOT / item['path']) != item['sha256']:
            failures.append('Changed tested source ' + item['path'])
    if len(report['runs']) != 1 or not all(x['passed'] for x in report['runs']):
        failures.append('Positive scenario missing')
    if len(report['negative']) != 3 or not all(x['passed'] for x in report['negative']):
        failures.append('Negative calibration missing')
    expected = 'frames=2 samples=210000 visible=153600 hsync=25200 vsync=800 writes=2012 grant_starts=32 failures=0'
    if expected not in report['runs'][0]['execution']['stdout']:
        failures.append('Coverage changed; review acceptance criteria')
    for item in json.loads((ROOT / 'references/video-contract-2026-11-25.json').read_text())['files']:
        if digest(ROOT / item['path']) != item['sha256']:
            failures.append('Changed reference ' + item['path'])
    if '--check' in sys.argv:
        manifest = json.loads(MANIFEST.read_text())
        for item in manifest['files']:
            p = (ROOT / item['path']).resolve()
            if not p.is_relative_to(ROOT) or not p.is_file() or digest(p) != item['sha256']:
                failures.append(item['path'])
        print(json.dumps({'checked': len(manifest['files']), 'failures': failures, 'production_released': False}))
        return int(bool(failures))
    if failures:
        print(json.dumps({'failures': failures})); return 1
    failures += audit_history()
    if failures:
        print(json.dumps({'failures': failures})); return 1
    names = ['README.md', 'ROADMAP.md', 'DECISIONS.md', 'PROVENANCE.md', 'CHANGELOG.md', 'AGENTS.md',
             'docs/engineering/PRODUCTION_GATES.md', 'docs/engineering/VALIDATION_STATUS.md',
             'docs/engineering/NET14A.md', 'tools/run_video_contract.py', 'tools/record_net14a_manifest.py',
             'references/video-contract-2026-11-25.json']
    files = {ROOT / n for n in names}
    for folder in ('sim/net14a', 'verification/net14a'):
        files.update(p for p in (ROOT / folder).rglob('*') if p.is_file() and p != MANIFEST)
    manifest = {'iteration': 'NET-14A', 'date': '2026-11-25', 'base_git_commit': BASE,
                'scope': 'Executable pre-design contract and consolidated review checklist, not physical raster or fabrication approval',
                'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                           'sha256': digest(p), 'origin': 'New NET-14A work; development subdirectory preserves explicitly identified failed fixture evidence'}
                          for p in sorted(files)]}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'recorded': len(files), 'historical_snapshots': 14, 'failures': failures,
                      'production_released': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
