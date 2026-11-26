"""NET22 native candidate: shared shift-register phases and registered line carry.

Starts from committed native video_system JSON, never executes its stateful builder.
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
from build_cpu_global import KICAD
from build_memory_decode import sig
from build_stack_bank import symbol as old_symbol
import build_video_raster as original

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/video_common_clock'
VERIFY = ROOT / 'verification/net22/native'


def uid(text):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'isa1/net22/video/' + text))


def definitions():
    defs = copy.deepcopy(original.definitions())
    defs['SN74AHC164'] = {'datasheet': 'https://www.ti.com/lit/ds/symlink/sn74ahc164.pdf',
        'source': 'TI SCAS970, February2024, PW14 candidate; exact pin functions, no footprint approval',
        'pins': {pin: {'name': name, 'type': kind} for pin, name, kind in [
            ('1', 'A', 'input'), ('2', 'B', 'input'), ('3', 'Q0', 'output'), ('4', 'Q1', 'output'),
            ('5', 'Q2', 'output'), ('6', 'Q3', 'output'), ('7', 'GND', 'power_in'), ('8', 'CLK', 'input'),
            ('9', 'CLR_N', 'input'), ('10', 'Q4', 'output'), ('11', 'Q5', 'output'), ('12', 'Q6', 'output'),
            ('13', 'Q7', 'output'), ('14', 'VCC', 'power_in')]}}
    defs['SN74LVC1G27'] = {'datasheet': 'https://www.ti.com/lit/ds/symlink/sn74lvc1g27.pdf',
        'source': 'TI SCES488F, November2026, DBV6 candidate; not an assumed AHC27',
        'pins': {pin: {'name': name, 'type': kind} for pin, name, kind in [
            ('1', 'A', 'input'), ('2', 'GND', 'power_in'), ('3', 'B', 'input'), ('4', 'Y', 'output'),
            ('5', 'VCC', 'power_in'), ('6', 'C', 'input')]}}
    return defs


def ports():
    ins, outs = original.ports()
    outs.pop('P3')
    outs['CAPTURE_CLOCK'] = 'capture_clk'
    return ins, outs


def design(defs):
    parts = copy.deepcopy(json.loads((ROOT / 'hardware/video_system/design.json').read_text())['parts'])

    def part(ref):
        return next(p for p in parts if p['reference'] == ref)

    def pin(ref, function):
        return next(pin for pin, value in defs[part(ref)['part']]['pins'].items() if value['name'] == function)

    def get(ref, function):
        return part(ref)['nets'][pin(ref, function)]

    def setnet(ref, function, net):
        part(ref)['nets'][pin(ref, function)] = net

    def replace(ref, kind, functions):
        p = part(ref)
        nets = {pin: functions.get(s['name']) for pin, s in defs[kind]['pins'].items()}
        for number, spec in defs[kind]['pins'].items():
            if spec['name'] in ('VCC', 'GND'):
                nets[number] = '+5V' if spec['name'] == 'VCC' else 'GND'
        p.update(part=kind, nets=nets)

    # Both terminal comparisons in the ancestor are balanced, not serial.
    # Preserve their gates; register positive H_END/V_END on phase3.
    hload, vload, ven = get('U1', 'LOAD_N'), get('U3', 'LOAD_N'), get('U3', 'ENP')
    inv = {}
    for p in parts:
        if p['part'] == 'SN74AHC04':
            for i in range(6):
                a = next(k for k, s in defs[p['part']]['pins'].items() if s['name'] == f'A{i}')
                y = next(k for k, s in defs[p['part']]['pins'].items() if s['name'] == f'Y{i}')
                if p['nets'][y] is not None:
                    inv[p['nets'][y]] = p['nets'][a]
    hterminal, vterminal = inv[hload], inv[vload]
    # The former RUN & H_END gate becomes a min-delay RUN buffer. Its old
    # vertical consumers now use H_END_REG directly, avoiding cascaded enable
    # propagation from phase3 through three RCO stages.
    found = []
    for p in parts:
        if p['part'] != 'SN74AHC08':
            continue
        for i in range(4):
            f = {s['name']: number for number, s in defs[p['part']]['pins'].items()}
            if p['nets'][f[f'Y{i}']] == ven:
                assert {p['nets'][f[f'A{i}']], p['nets'][f[f'B{i}']]} == {'RUN', hterminal}
                p['nets'][f[f'A{i}']] = 'RUN'
                p['nets'][f[f'B{i}']] = '+5V'
                found.append(p['reference'])
    assert len(found) == 1
    replace('U9', 'SN74AHC164', {'A': 'PHASE_SERIAL', 'B': '+5V', 'CLK': 'BUF_2_2', 'CLR_N': 'BUF_1_1',
                                **{f'Q{i}': f'P{i}' for i in range(4)}})
    replace('U10', 'SN74LVC1G27', {'A': 'P0', 'B': 'P1', 'C': 'P2', 'Y': 'PHASE_SERIAL'})
    setnet('U11', 'CLK0', 'BUF_2_2')
    for ref in ['U1', 'U2']:
        setnet(ref, 'ENP', ven)
    for ref in ['U3', 'U4', 'U5']:
        setnet(ref, 'CLK', 'BUF_2_1')
        setnet(ref, 'ENP', 'H_END_REG')
        setnet(ref, 'LOAD_N', 'V_LOAD_REGISTERED_N')
    setnet('U11', 'CLK1', 'BUF_2_0')  # RUN shares H counter clock.
    setnet('U12', 'CLK1', 'BUF_2_0')  # SLOT samples old H on the same branch.
    for ref in ['U6', 'U7']:
        setnet(ref, 'CLK', 'CAPTURE_CLOCK')
    setnet('U12', 'CLK0', 'CAPTURE_CLOCK')
    setnet('U34', 'A3', 'P3')
    setnet('U34', 'Y3', 'CAPTURE_CLOCK')
    # One clock-buffer output now drives RESET sync pair + shift CLK + backend
    # CLK (four input pins); H branch four, V branch three, capture branch three.
    blank = {'reference': 'U36', 'part': 'SN74AHC74', 'x': 59.69, 'y': 495.3, 'nets': {}}
    parts.append(blank)
    replace('U36', 'SN74AHC74', {
        'CLK0': 'P3', 'CLR0_N': 'BUF_1_1', 'PRE0_N': '+5V', 'D0': hterminal, 'Q0': 'H_END_REG',
        'CLK1': 'P3', 'CLR1_N': 'BUF_1_1', 'PRE1_N': '+5V', 'D1': vterminal, 'QB1': 'V_LOAD_REGISTERED_N'})
    parts.append({'reference': 'C36', 'part': 'C', 'x': 80.01, 'y': 464.82, 'nets': {'1': '+5V', '2': 'GND'}})
    return parts


def package_symbol(kind, spec):
    return tuple(x.replace('NET02:', 'NET22V:') if isinstance(x, str) else x for x in old_symbol(kind, spec))


exec(original._emitter.replace('video_raster', 'video_common_clock').replace('NET14B', 'NET22V').replace('NET-14B', 'NET-22V'), globals())
converter = inspect.getsource(original.convert).replace('video_raster', 'video_common_clock')
old = "        if kind=='SN74LV161A':"
new = '''        if kind=='SN74AHC164':
            lines.append(f"net22_ahc164 #(.TIMED(TIMED),.EARLY_CAPTURE(EARLY_CAPTURE)) {ref}({fs['CLK']},{fs['CLR_N']},{fs['A']},{fs['B']},{vec('Q',8)},checks);")
        elif kind=='SN74LVC1G27':
            lines.append(f"assign #(TIMED?3.6:0) {fs['Y']}=~({fs['A']} | {fs['B']} | {fs['C']});")
        elif kind=='SN74LV161A':'''
assert converter.count(old) == 1
converter = converter.replace(old, new)
exec(converter, globals())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    VERIFY.mkdir(parents=True, exist_ok=True)
    defs = definitions()
    parts = design(defs)
    emit(defs, parts)
    (OUT / 'package-functions.json').write_text(json.dumps(defs, indent=2) + '\n')
    (OUT / 'design.json').write_text(json.dumps({'iteration': 'NET-22V candidate', 'parts': parts}, indent=2) + '\n')
    command = [KICAD, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(VERIFY / 'video_common_clock.xml'), str(OUT / 'video_common_clock.kicad_sch')]
    subprocess.run(command, check=True, capture_output=True, timeout=120)
    report = convert()
    report.update(date='2026-11-26', command=command, kicad=subprocess.check_output([KICAD, 'version'], text=True).strip(),
                  sources=[{'path': name, 'sha256': hashlib.sha256((ROOT / name).read_bytes()).hexdigest()} for name in
                           ['tools/build_video_common_clock.py', 'hardware/video_system/design.json', 'tools/build_video_raster.py', 'references/net22/sn74ahc164.pdf', 'references/net22/sn74lvc1g27.pdf']],
                  scope='Native candidate graph with common-clock serial phases and phase3 registered line carry. Not yet full regression, analog/global PVT or production approval.', production_released=False)
    (VERIFY / 'schematic-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return int(bool(report['failures']) or report['max_signal_input_loads'] > 4)


if __name__ == '__main__':
    raise SystemExit(main())
