"""NET18 supervisor + buffered reset variant; vendor analog behavior external.

The digital forcepoint RAW_SAFE_N represents a qualified supervisor output,
not a substitute simulation of the TPS3703 internals. Ancestor is immutable.
"""
import copy
import csv
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import uuid
import xml.etree.ElementTree as ET
from build_memory_decode import sig
from build_cpu_global import KICAD
import build_reset_domains as base

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/power_reset'
VERIFY = ROOT / 'verification/net18/native'


def uid(s):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'isa1/net18/' + s))


def definitions():
    defs = copy.deepcopy(base.definitions())
    defs['TPS3703F6050DSER'] = {
        'datasheet': 'https://www.ti.com/lit/ds/symlink/tps3703.pdf',
        'source': 'SBVS249B figure 6-1 / Pin Functions, DSE six pins; CT open, UV-only F6050 candidate, no footprint qualified',
        'pins': {p: {'name': n, 'type': t} for p, n, t in [
            ('1', 'SENSE', 'input'), ('2', 'VCC', 'power_in'),
            ('3', 'CT', 'input'), ('4', 'RESET_N', 'output'),
            ('5', 'GND', 'power_in'), ('6', 'MR_N', 'input')]}}
    return defs


def design(defs):
    parts = copy.deepcopy(base.design(defs))
    # The supervisor drives ONE CMOS input. The fast qualifier uses its buffer.
    u4 = next(p for p in parts if p['reference'] == 'U4')
    for pin, spec in defs[u4['part']]['pins'].items():
        if spec['name'] == 'A1':
            assert u4['nets'][pin] == 'RAW_SAFE_N'
            u4['nets'][pin] = 'RAW_BUFFERED'
    parts += [
        {'reference': 'U6', 'part': 'TPS3703F6050DSER', 'x': 70, 'y': 240,
         'nets': {'1': 'SUPERVISOR_SENSE', '2': '+5V', '3': None,
                  '4': 'RAW_SAFE_N', '5': 'GND', '6': '+5V'}},
        {'reference': 'R2', 'part': 'R', 'value': '950 ohm 0.1% effective', 'x': 180, 'y': 210,
         'nets': {'1': '+5V', '2': 'SUPERVISOR_SENSE'}},
        {'reference': 'R3', 'part': 'R', 'value': '100 ohm 0.1% effective', 'x': 180, 'y': 260,
         'nets': {'1': 'SUPERVISOR_SENSE', '2': 'GND'}},
        {'reference': 'R4', 'part': 'R', 'value': '10k 1%', 'x': 290, 'y': 240,
         'nets': {'1': '+5V', '2': 'RAW_SAFE_N'}},
        {'reference': 'C7', 'part': 'C', 'value': '100nF', 'x': 400, 'y': 210,
         'nets': {'1': '+5V', '2': 'GND'}},
        {'reference': 'C8', 'part': 'C', 'value': '1n C0G sense candidate', 'x': 400, 'y': 260,
         'nets': {'1': 'SUPERVISOR_SENSE', '2': 'GND'}},
    ]
    for p in parts:
        p['x'] = round(p['x'] / 1.27) * 1.27
        p['y'] = round(p['y'] / 1.27) * 1.27
    return parts


def package_symbol(kind, spec):
    return tuple(x.replace('NET16B:', 'NET18:') if isinstance(x, str) else x
                 for x in base.package_symbol(kind, spec))


emitter = inspect.getsource(base.emit).replace('reset_domains', 'power_reset').replace('NET16B', 'NET18').replace('NET-16B', 'NET-18').replace('2026-11-25', '2026-11-26')
exec(emitter, globals())

# Exact XML checks remain inherited. Omit ONLY the analog supervisor from the
# digital projection; all its pins/values are still compared with the design.
converter = inspect.getsource(base.convert).replace('reset_domains', 'power_reset')
converter = converter.replace("kind=p['part'];ref=p['reference'];fs={}", "kind=p['part'];ref=p['reference'];fs={}\n        if kind=='TPS3703F6050DSER':continue")
converter = converter.replace("if kind in ('C','R'):continue", "if kind in ('C','R'):continue")
converter = converter.replace("'ics':5", "'ics':6")
exec(converter, globals())
digital_convert = convert


def convert(path=None, destination=None):
    path = path or VERIFY / 'power_reset.xml'
    report = digital_convert(path, destination)
    root = ET.parse(path).getroot()
    raw = next(n for n in root.findall('./nets/net') if n.get('name').removeprefix('/') == 'RAW_SAFE_N')
    endpoints = {(n.get('ref'), n.get('pin')) for n in raw.findall('node')}
    if endpoints != {('U6', '4'), ('R4', '2'), ('U1', '2')}:
        raise ValueError('Supervisor RESET must drive only U1 input plus pullup')
    report.update(scope='Exact supervisor/passive/logic pin graph. Digital projection forces RAW_SAFE_N; supervisor internals, finite RESET rise, below-valid-VDD and MTBF are NOT simulated',
                  supervisor_reset_cmos_inputs=1, supervisor_reset_load_budget_pf=10,
                  supervisor_analog_model_implemented=False, production_released=False)
    return report


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    VERIFY.mkdir(parents=True, exist_ok=True)
    defs = definitions()
    parts = design(defs)
    emit(defs, parts)
    (OUT / 'package-functions.json').write_text(json.dumps(defs, indent=2) + '\n')
    (OUT / 'design.json').write_text(json.dumps({'iteration': 'NET-18', 'parts': parts}, indent=2) + '\n')
    cmd = [KICAD, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(VERIFY / 'power_reset.xml'), str(OUT / 'power_reset.kicad_sch')]
    subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    report = convert()
    report.update(command=cmd, kicad=subprocess.check_output([KICAD, 'version'], text=True).strip(),
                  sources=[{'path': n, 'sha256': hashlib.sha256((ROOT / n).read_bytes()).hexdigest()}
                           for n in ('tools/build_reset_domains.py', 'tools/build_power_reset.py', 'references/power-candidates/tps3703.pdf')])
    (VERIFY / 'schematic-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
