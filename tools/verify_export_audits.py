"""Reproduce inspected historical symbolic generators only in temporary copies."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/export-2026-11-26'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    library = json.loads((ROOT / 'archive/export-2026-11-26/library-project.json').read_text())

    def unique(name):
        hits = [ROOT / x['path'] for x in library if x['file_name'] == name and x['available']]
        if len(hits) != 1:
            raise ValueError('Ambiguous historical file ' + name)
        return hits[0]

    names = ['isa1_rev33_microcode.py', 'isa1_rev33_microcode.json', 'isa1_rev76.py', 'isa1_rev76_microcode.json']
    originals = {n: unique(n) for n in names}
    sources = [{'path': p.relative_to(ROOT).as_posix(), 'sha256': digest(p)} for p in originals.values()]
    sources.append({'path': 'tools/verify_export_audits.py', 'sha256': digest(Path(__file__))})
    rows = []
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='isa1-recovered-history-') as tmp:
        work = Path(tmp)
        for name, path in originals.items():
            shutil.copyfile(path, work / name)
        for script, generated in [('isa1_rev33_microcode.py', 'isa1_rev33_microcode.json'),
                                  ('isa1_rev76.py', 'isa1_rev76_microcode.json')]:
            cmd = ['python3', str(work / script)]
            proc = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=60)
            path = work / generated
            data = json.loads(path.read_text()) if path.exists() else None
            expected = json.loads(originals[generated].read_text())
            row = {'script': script, 'command': cmd, 'exit': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr,
                   'generated_sha256': digest(path) if path.exists() else None,
                   'original_sha256': digest(originals[generated]),
                   'json_semantically_equal': data == expected,
                   'bytes_identical': path.is_file() and path.read_bytes() == originals[generated].read_bytes(),
                   'audit': data.get('audit') if data else None,
                   'passed': proc.returncode == 0 and data == expected}
            rows.append(row)
    for item in sources:
        if digest(ROOT / item['path']) != item['sha256']:
            raise ValueError('Original/source changed')
    expected_counts = rows[0]['audit']['opcode_count'] == 19 and rows[1]['audit']['stack_roundtrips'] == 196608 and rows[1]['audit']['expanded_instructions'] == 15
    report = {'date': '2026-11-26', 'python': subprocess.check_output(['python3', '--version'], text=True).strip(),
              'scope': 'Recovered REV33/REV76 symbolic structural generators. No gate, microcode execution, electrical or current ISA26 signoff',
              'sources': sources, 'runs': rows, 'expected_counts': expected_counts,
              'historical_rev983_diagnostic_asm_still_missing': True,
              'failures': [r['script'] for r in rows if not r['passed']] + ([] if expected_counts else ['Unexpected audit counts']),
              'production_released': False}
    (OUT / 'historical-audits.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'runs': [{'script': r['script'], 'exit': r['exit'], 'semantic_equal': r['json_semantically_equal'], 'bytes_identical': r['bytes_identical']} for r in rows],
                      'expected_counts': expected_counts, 'failures': report['failures']}))
    return int(bool(report['failures']))


if __name__ == '__main__':
    raise SystemExit(main())
