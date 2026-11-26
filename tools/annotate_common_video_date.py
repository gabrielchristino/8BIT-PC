"""Correct copied date metadata without changing executed inputs or results."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / 'verification/net22/native/results.json'
    payload = path.read_bytes()
    data = json.loads(payload)
    if data.get('metadata_correction'):
        raise ValueError('Already annotated')
    saved = ROOT / 'verification/net22/development/frame-metadata-date/results-original.json'
    saved.parent.mkdir(parents=True, exist_ok=True)
    saved.write_bytes(payload)
    data['metadata_correction'] = {'date': '2026-11-26', 'original_date_field': data['date'],
        'reason': 'Runner inherited the fixed2026-11-25 date from NET14C. Actual current execution was26/11/2026; this is a metadata correction after execution, not a repeated run or changed numeric result.',
        'original_report': saved.relative_to(ROOT).as_posix(), 'original_report_sha256': hashlib.sha256(payload).hexdigest()}
    data['date'] = '2026-11-26'
    data['scope'] = 'NET22 native shared-clock shift phases and registered line carry, with NET13 memory/controller, VRAM seeded for full-frame comparison. Stopped-master reset release in this bench; no complete PVT/analog/CPU-power signoff.'
    data['sources'].append({'path': 'tools/annotate_common_video_date.py', 'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    path.write_text(json.dumps(data, indent=2) + '\n')
    print('Recorded explicit correction of inherited date metadata; original report preserved')


if __name__ == '__main__':
    main()
