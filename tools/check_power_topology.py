"""Fault injections must fail native XML validation, not merely HDL tests."""
import hashlib
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
from build_power_reset import ROOT, VERIFY, convert


def main():
    source = VERIFY / 'power_reset.xml'
    rows = []
    mutations = [('divider', 'R2', 'value', '940 ohm 0.1% effective'),
                 ('reset_load', 'U4', 'pin', None)]
    with tempfile.TemporaryDirectory(prefix='isa1-power-negative-') as tmp:
        for name, ref, field, value in mutations:
            tree = ET.parse(source)
            if field == 'value':
                tree.find(f'./components/comp[@ref="{ref}"]/value').text = value
            else:
                # Move just the fast inhibit input from buffered to raw output.
                pins = json.loads((ROOT / 'hardware/power_reset/package-functions.json').read_text())['SN74AHC08']['pins']
                pin = next(p for p, s in pins.items() if s['name'] == 'A1')
                nets = tree.findall('./nets/net')
                old = next(n for n in nets if n.get('name').removeprefix('/') == 'RAW_BUFFERED')
                raw = next(n for n in nets if n.get('name').removeprefix('/') == 'RAW_SAFE_N')
                node = next(n for n in old.findall('node') if n.get('ref') == ref and n.get('pin') == pin)
                old.remove(node)
                raw.append(node)
            changed = Path(tmp) / (name + '.xml')
            tree.write(changed)
            try:
                convert(changed, Path(tmp) / (name + '.sv'))
                error = ''
            except ValueError as exc:
                error = str(exc)
            rows.append({'mutation': name, 'expected_rejection': True, 'error': error,
                         'passed': error.startswith('Changed value R2') if name == 'divider' else error.startswith('Pin mismatch U4/')})
    report = {'sources': [{'path': n, 'sha256': hashlib.sha256((ROOT / n).read_bytes()).hexdigest()} for n in
                         ('tools/build_power_reset.py', 'tools/check_power_topology.py', 'verification/net18/native/power_reset.xml')],
              'negative': rows, 'failures': [r['mutation'] for r in rows if not r['passed']]}
    (VERIFY / 'topology-negative.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return int(bool(report['failures']))


if __name__ == '__main__':
    raise SystemExit(main())
