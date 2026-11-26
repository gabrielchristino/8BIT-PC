"""NET23 candidate: two ACH configurations and reuse one idle CPU buffer."""
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
import build_schmitt_reset as previous

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/clocked_reset'
VERIFY = ROOT / 'verification/net23/native'


def uid(text):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'isa1/net23/' + text))


def definitions():
    defs = copy.deepcopy(json.loads((ROOT / 'hardware/schmitt_reset/package-functions.json').read_text()))
    for kind in ['ACH_CPU_CONFIG', 'ACH_MASTER_CONFIG']:
        defs[kind] = {'datasheet': 'https://abracon.com/Oscillators/ACH.pdf',
            'source': 'ACH2016 pin table; configured L/C/T/A, standard15pF; full procurement PN NOT homologated',
            'pins': {pin: {'name': name, 'type': typ} for pin, name, typ in [
                ('1', 'ENABLE', 'input'), ('4', 'GND', 'power_in'), ('5', 'OUT', 'output'), ('8', 'VCC', 'power_in')]}}
    return defs


def design(defs):
    parts = copy.deepcopy(json.loads((ROOT / 'hardware/schmitt_reset/design.json').read_text())['parts'])
    u1 = next(p for p in parts if p['reference'] == 'U1')
    assert (u1['nets']['2'], u1['nets']['1'], u1['nets']['3']) == ('GND', '+5V', None)
    u1['nets'].update({'2': 'CPU_OSC', '1': 'GND', '3': 'CPU_CLK'})
    for p in parts:
        if p['reference'] == 'U7':
            assert p['nets']['9'] == 'CPU_CLK' and p['nets']['12'] == 'CPU_CLK'
    for ref, kind, output, x, frequency in [('X1', 'ACH_CPU_CONFIG', 'CPU_OSC', 69.85, '0.100'),
                                          ('X2', 'ACH_MASTER_CONFIG', 'MASTER', 220.98, '25.175')]:
        parts.append({'reference': ref, 'part': kind, 'value': f'ACH config {frequency}MHz L C T A standard15pF; PN open',
                      'x': x, 'y': 450.85, 'nets': {'1': '+5V', '4': 'GND', '5': output, '8': '+5V'}})
    for ref, x in [('C13', 110.49), ('C14', 261.62)]:
        parts.append({'reference': ref, 'part': 'C', 'value': '100nF candidate', 'x': x, 'y': 420.37,
                      'nets': {'1': '+5V', '2': 'GND'}})
    return parts


def package_symbol(kind, spec):
    return tuple(x.replace('NET21:', 'NET23:') if isinstance(x, str) else x
                 for x in previous.package_symbol(kind, spec))


emitter = previous.emitter.replace('schmitt_reset', 'clocked_reset').replace('NET21', 'NET23').replace('NET-21', 'NET-23')
emitter = emitter.replace('ISA-1 delayed bank reset / fast inhibit candidate', 'ISA-1 clock sources and reset candidate')
assert emitter.count(" else kind") == 2
emitter = emitter.replace(" else kind", " else p.get('value',kind)")
exec(emitter, globals())
converter = previous.converter.replace('schmitt_reset', 'clocked_reset')


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


converter = once(converter, "'BACKEND':'backend_source','CPU_CLK':'cpu_source'", "'BACKEND':'backend_source'")
converter = once(converter, "'KEYBOARD_CLK':'keyboard_clk'}", "'KEYBOARD_CLK':'keyboard_clk','CPU_OSC':'cpu_source','MASTER':'master_source'}")
converter = once(converter, "if kind in ('C','R'):continue", """if kind in ('C','R'):continue
        if kind in ('ACH_CPU_CONFIG','ACH_MASTER_CONFIG'):
            prefix='CPU' if kind=='ACH_CPU_CONFIG' else 'MASTER'
            lines.append(f"net23_ach #(.PERIOD_NS({prefix}_PERIOD_NS),.DUTY({prefix}_DUTY),.STARTUP_NS({prefix}_STARTUP_NS)) {ref}(osc_power_valid,{fs['ENABLE']},{fs['OUT']});")
            continue""")
converter = once(converter, 'ASSERT_DELAY=1000,RELEASE_DELAY=42000)',
    'ASSERT_DELAY=1000,RELEASE_DELAY=42000,CPU_PERIOD_NS=10000,MASTER_PERIOD_NS=39.721946,CPU_DUTY=0.5,MASTER_DUTY=0.5,CPU_STARTUP_NS=10000000,MASTER_STARTUP_NS=10000000)')
converter = once(converter, 'input wire raw_safe_n,backend_source,cpu_source,output wire',
    'input wire raw_safe_n,backend_source,osc_power_valid,output wire')
converter = once(converter, 'cpu_core_clk,access_clk,keyboard_clk);',
    'cpu_core_clk,access_clk,keyboard_clk,cpu_source,master_source);')
exec(converter, globals())
digital_convert = convert


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    VERIFY.mkdir(parents=True, exist_ok=True)
    defs, parts = definitions(), None
    parts = design(defs)
    emit(defs, parts)
    (OUT / 'package-functions.json').write_text(json.dumps(defs, indent=2) + '\n')
    (OUT / 'design.json').write_text(json.dumps({'iteration': 'NET23 candidate', 'parts': parts}, indent=2) + '\n')
    command = [KICAD, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(VERIFY / 'clocked_reset.xml'), str(OUT / 'clocked_reset.kicad_sch')]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    report = digital_convert()
    report.update(date='2026-11-26', logic_ics=8, oscillator_modules=2, active_packages=10,
                  command=command, kicad=subprocess.check_output([KICAD, 'version'], text=True).strip(),
                  sources=[{'path': n, 'sha256': hashlib.sha256((ROOT / n).read_bytes()).hexdigest()} for n in
                           ['tools/build_clocked_reset.py', 'hardware/schmitt_reset/design.json', 'hardware/schmitt_reset/package-functions.json',
                            'tools/build_schmitt_reset.py', 'references/net22/abracon-ach.pdf']],
                  scope='Exact native configured oscillator/reset pin graph. Qualified VDD plus behavioral oscillator projection; supervisor/RC remain abstractions. Full PN, PCB capacitance, jitter/POR/global PVT/MTBF and fabrication unqualified.',
                  production_released=False)
    # Inherited count is logic ICs; expose oscillator packages separately.
    assert report['ics'] == 8
    (VERIFY / 'schematic-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return int(bool(report['failures']) or report['max_signal_input_loads'] > 4)


if __name__ == '__main__':
    raise SystemExit(main())
