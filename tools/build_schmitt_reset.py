"""NET21 candidate: supervisor CL50pF and spare Schmitt receiver pair.

Preserves NET20; digital projection still uses a qualified external RAW signal.
"""
import copy
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import uuid
import xml.etree.ElementTree as ET
from build_cpu_global import KICAD
from build_memory_decode import sig
import build_system_reset as previous

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/schmitt_reset'
VERIFY = ROOT / 'verification/net21/native'


def uid(text):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'isa1/net21/' + text))


def definitions():
    defs = copy.deepcopy(previous.definitions())
    defs.pop('TPS3703F6050DSER')
    defs['TPS3808G01DBVR'] = {'datasheet': 'https://www.ti.com/lit/ds/symlink/tps3808.pdf',
        'source': 'SBVS050N Figure5-1/table5-1 DBV six pins, not DRV thermal-pad package; footprint not qualified.',
        'pins': {pin: {'name': name, 'type': kind} for pin, name, kind in [
            ('1', 'RESET_N', 'open_collector'), ('2', 'GND', 'power_in'), ('3', 'MR_N', 'input'),
            ('4', 'CT', 'input'), ('5', 'SENSE', 'input'), ('6', 'VCC', 'power_in')]}}
    return defs


def design(defs):
    parts = copy.deepcopy(previous.design(previous.definitions()))
    u6 = next(p for p in parts if p['reference'] == 'U6')
    u6.update(part='TPS3808G01DBVR', nets={'1': 'RAW_SAFE_N', '2': 'GND', '3': '+5V',
                                            '4': None, '5': 'SUPERVISOR_SENSE', '6': '+5V'})

    def connect(ref, function, net):
        part = next(p for p in parts if p['reference'] == ref)
        pin = next(pin for pin, s in defs[part['part']]['pins'].items() if s['name'] == function)
        part['nets'][pin] = net

    # Same number of packages. Two previously idle Schmitt inverters form a
    # non-inverting receiver; the previous standard CMOS input is tied off.
    for function, net in [('A0', 'GND'), ('OE0_N', '+5V'), ('Y0', None)]:
        connect('U1', function, net)
    for function, net in [('A2', 'RAW_SAFE_N'), ('Y2', 'RAW_INVERTED'), ('A3', 'RAW_INVERTED'), ('Y3', 'RAW_BUFFERED')]:
        connect('U2', function, net)
    for part in parts:
        if part['reference'] == 'R2':
            part['value'] = '1120 ohm 0.1% effective'
        elif part['reference'] == 'R4':
            part['value'] = '100k 1%'
    return parts


def package_symbol(kind, spec):
    drawn = copy.deepcopy(spec)
    if kind == 'TPS3808G01DBVR':
        drawn['pins']['1']['type'] = 'output'
    result = tuple(x.replace('NET20:', 'NET21:') if isinstance(x, str) else x for x in previous.package_symbol(kind, drawn))
    if kind == 'TPS3808G01DBVR':
        result = (result[0].replace('(pin output line', '(pin open_collector line'), result[1])
    return result


emitter = previous.emitter.replace('system_reset', 'schmitt_reset').replace('NET20', 'NET21').replace('NET-20', 'NET-21')
exec(emitter, globals())
converter = previous.converter.replace('system_reset', 'schmitt_reset').replace('TPS3703F6050DSER', 'TPS3808G01DBVR')
exec(converter, globals())
digital_convert = convert


def convert(path=None, destination=None):
    path = path or VERIFY / 'schmitt_reset.xml'
    report = digital_convert(path, destination)
    root = ET.parse(path).getroot()
    raw = next(n for n in root.findall('./nets/net') if n.get('name').removeprefix('/') == 'RAW_SAFE_N')
    expected = {('U6', '1'), ('R4', '2'), ('U2', '5')}
    if {(n.get('ref'), n.get('pin')) for n in raw.findall('node')} != expected:
        raise ValueError('Supervisor must drive exactly one Schmitt input')
    report.update(scope='Exact pin graph with TPS3808 supervisor and Schmitt pair; qualified external RAW forcepoint, not analog supervisor/POR or fabrication/PVT/MTBF proof.',
                  supervisor_cmos_inputs=1, receiver='two SN74AHC14 inverters',
                  supervisor_test_cl_pf=50, input_ci_max_at_5v_pf=10, routing_budget_pf=10,
                  raw_load_budget_pf=20, raw_load_budget_within_test_cl=True,
                  analog_supervisor_implemented=False, production_released=False)
    return report


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    VERIFY.mkdir(parents=True, exist_ok=True)
    defs = definitions()
    parts = design(defs)
    emit(defs, parts)
    (OUT / 'package-functions.json').write_text(json.dumps(defs, indent=2) + '\n')
    (OUT / 'design.json').write_text(json.dumps({'iteration': 'NET-21A', 'parts': parts}, indent=2) + '\n')
    command = [KICAD, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(VERIFY / 'schmitt_reset.xml'), str(OUT / 'schmitt_reset.kicad_sch')]
    subprocess.run(command, check=True, capture_output=True, timeout=120)
    report = convert()
    names = ['tools/build_schmitt_reset.py', 'tools/build_system_reset.py', 'references/net20/tps3808.pdf', 'references/ti/sn74ahc14.pdf']
    report.update(date='2026-11-26', command=command, kicad=subprocess.check_output([KICAD, 'version'], text=True).strip(),
                  sources=[{'path': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest()} for p in names])
    (VERIFY / 'schematic-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
