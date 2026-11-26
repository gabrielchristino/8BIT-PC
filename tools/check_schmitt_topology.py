"""Reject package pin reversal and predecessor pullup in temporary XML copies."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
import build_schmitt_reset as native

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net21/native'


def main():
    xml = OUT / 'schmitt_reset.xml'
    tree = ET.parse(xml)
    names = ['tools/check_schmitt_topology.py', 'tools/build_schmitt_reset.py',
             'hardware/schmitt_reset/design.json', 'hardware/schmitt_reset/package-functions.json',
             'verification/net21/native/schmitt_reset.xml', 'hardware/schmitt_reset/schmitt_reset_netlist.sv']
    report = {'date': '2026-11-26', 'sources': [{'path': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest()} for p in names],
              'negative': [], 'failures': [], 'production_released': False}
    with tempfile.TemporaryDirectory(prefix='isa1-schmitt-pins-') as tmp:
        target = Path(tmp)
        native.convert(xml, target / 'positive.sv')
        report['positive_projection_matches'] = (target / 'positive.sv').read_bytes() == (ROOT / 'hardware/schmitt_reset/schmitt_reset_netlist.sv').read_bytes()
        if not report['positive_projection_matches']:
            report['failures'].append('Positive graph projection differs')
        for case in ('supervisor_power_reset_pin_reversal', 'predecessor_pullup'):
            changed = copy.deepcopy(tree)
            if case == 'supervisor_power_reset_pin_reversal':
                nodes = [n for n in changed.findall('./nets/net/node') if n.get('ref') == 'U6' and n.get('pin') in ('1', '6')]
                assert len(nodes) == 2
                for node in nodes:
                    node.set('pin', '6' if node.get('pin') == '1' else '1')
                expected = 'Pin mismatch U6/'
            else:
                changed.find('./components/comp[@ref="R4"]/value').text = '10k 1%'
                expected = 'Changed value R4'
            path = target / (case + '.xml')
            changed.write(path, encoding='utf-8', xml_declaration=True)
            error = None
            try:
                native.convert(path, target / (case + '.sv'))
            except ValueError as exc:
                error = str(exc)
            passed = error is not None and error.startswith(expected)
            report['negative'].append({'case': case, 'expected': expected, 'error': error, 'passed': passed,
                                       'mutated_xml_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
            if not passed:
                report['failures'].append(case)
    (OUT / 'topology-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'positive_projection_matches': report['positive_projection_matches'], 'negative_cases': len(report['negative']), 'failures': report['failures']}))
    return int(bool(report['failures']))


if __name__ == '__main__':
    raise SystemExit(main())
