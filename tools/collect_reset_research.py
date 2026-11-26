"""Preserve primary datasheets consulted for the open supervisor interface."""
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net20/research'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    refs = ROOT / 'references/net20'
    refs.mkdir(parents=True, exist_ok=True)
    names = ['sn74ahc1g125', 'sn74lvc1g125', 'tps3808', 'tps3700', 'tps3890', 'tps3840']
    records = []
    for name in names + ['sn74ahc125', 'tps3703']:
        url = 'https://www.ti.com/lit/ds/symlink/' + name + '.pdf'
        target = refs / (name + '.pdf')
        if name == 'sn74ahc125':
            target = ROOT / 'references/ti/sn74ahc125.pdf'
        elif name == 'tps3703':
            target = ROOT / 'references/power-candidates/tps3703.pdf'
        fetched = target.is_file()
        if not fetched:
            with urlopen(Request(url, headers={'User-Agent': 'ISA1-engineering-source-audit'}), timeout=60) as response:
                payload = response.read()
            if not payload.startswith(b'%PDF-'):
                raise ValueError('Not PDF ' + name)
            target.write_bytes(payload)
        extraction = OUT / (name + '.txt')
        subprocess.run(['pdftotext', '-layout', str(target), str(extraction)], check=True)
        records.append({'path': target.relative_to(ROOT).as_posix(), 'url': url,
                        'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                        'reused_existing_original': fetched, 'extraction': extraction.relative_to(ROOT).as_posix(),
                        'extraction_sha256': hashlib.sha256(extraction.read_bytes()).hexdigest(),
                        'transformation': 'Original PDF bytes retained, separate pdftotext -layout. Research only; alternative is not a selected BOM part.'})
        print(name, flush=True)
    (OUT / 'sources.json').write_text(json.dumps({'date': '2026-11-26', 'files': records,
        'sources': [{'path': 'tools/collect_reset_research.py', 'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}],
        'pdftotext': subprocess.run(['pdftotext', '-v'], capture_output=True, text=True).stderr,
        'production_released': False}, indent=2) + '\n')


if __name__ == '__main__':
    main()
