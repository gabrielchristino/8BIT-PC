"""Preserve original primary clock datasheets; failures are not substitutions."""
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net22/research'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    refs = ROOT / 'references/net22'
    refs.mkdir(parents=True, exist_ok=True)
    sources = [
        ('abracon-ach', 'https://abracon.com/Oscillators/ACH.pdf'),
        ('ecs-2100x', 'https://ecsxtal.com/store/pdf/ecs-2100x.pdf'),
        ('ltc6900', 'https://www.analog.com/media/en/technical-documentation/data-sheets/6900fa.pdf'),
        ('ltc6906', 'https://www.analog.com/media/en/technical-documentation/data-sheets/6906fc.pdf'),
        ('sn74ac125', 'https://www.ti.com/lit/ds/symlink/sn74ac125.pdf'),
        ('sn74act125', 'https://www.ti.com/lit/ds/symlink/sn74act125.pdf'),
        ('sn74lvc125a', 'https://www.ti.com/lit/ds/symlink/sn74lvc125a.pdf'),
        ('sn74lv1t125', 'https://www.ti.com/lit/ds/symlink/sn74lv1t125.pdf'),
        ('mc74ac125', 'https://www.onsemi.com/pdf/datasheet/mc74ac125-d.pdf'),
    ]
    records = []
    for name, url in sources:
        path = refs / (name + '.pdf')
        record = {'url': url, 'path': path.relative_to(ROOT).as_posix(), 'selected_for_bom': False}
        try:
            if not path.exists():
                with urlopen(Request(url, headers={'User-Agent': 'ISA1-engineering-source-audit'}), timeout=45) as response:
                    payload = response.read()
                if not payload.startswith(b'%PDF-'):
                    raise ValueError('Response is not PDF')
                path.write_bytes(payload)
            extraction = OUT / (name + '.txt')
            command = ['pdftotext', '-layout', str(path), str(extraction)]
            subprocess.run(command, check=True, capture_output=True, timeout=30)
            record.update(downloaded=True, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                          extraction=extraction.relative_to(ROOT).as_posix(), extraction_sha256=hashlib.sha256(extraction.read_bytes()).hexdigest(),
                          transformation='Original PDF bytes unchanged; separate pdftotext -layout', command=command)
        except Exception as exc:
            record.update(downloaded=False, error=type(exc).__name__ + ': ' + str(exc))
        records.append(record)
        print(json.dumps({'name': name, 'downloaded': record['downloaded'], 'error': record.get('error')}), flush=True)
    (OUT / 'sources.json').write_text(json.dumps({'date': '2026-11-26', 'files': records,
        'collector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'Primary research; candidate is not selected/qualified BOM. Failed retrievals remain explicit.',
        'production_released': False}, indent=2) + '\n')


if __name__ == '__main__':
    main()
