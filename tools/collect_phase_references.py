"""Preserve primary references for a proposed common-clock phase generator."""
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    records = []
    refs = ROOT / 'references/net22'
    out = ROOT / 'verification/net22/research'
    refs.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    for name in ['sn74ahc164', 'sn74lvc1g27']:
        url = 'https://www.ti.com/lit/ds/symlink/' + name + '.pdf'
        path = refs / (name + '.pdf')
        if not path.exists():
            with urlopen(Request(url, headers={'User-Agent': 'ISA1-engineering-source-audit'}), timeout=45) as response:
                payload = response.read()
            if not payload.startswith(b'%PDF-'):
                raise ValueError('Not PDF ' + name)
            path.write_bytes(payload)
        extraction = out / (name + '.txt')
        subprocess.run(['pdftotext', '-layout', str(path), str(extraction)], check=True)
        records.append({'path': path.relative_to(ROOT).as_posix(), 'url': url, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'extraction': extraction.relative_to(ROOT).as_posix(), 'extraction_sha256': hashlib.sha256(extraction.read_bytes()).hexdigest(),
                        'transformation': 'Original PDF unchanged; separate pdftotext -layout; candidate not qualified BOM'})
    (out / 'phase-sources.json').write_text(json.dumps({'date': '2026-11-26', 'files': records,
        'sources': [{'path': 'tools/collect_phase_references.py', 'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}]}, indent=2) + '\n')
    print('Preserved AHC164 and LVC1G27 primary references')


if __name__ == '__main__':
    main()
