"""Generate separate NET21 adapters and checks, preserving NET20 evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net21'


def main():
    transforms = [
        ('sim/net20/isa1_memory_reset.sv', 'sim/net21/isa1_memory_schmitt.sv', [('system_reset_netlist', 'schmitt_reset_netlist')]),
        ('sim/net20/tb_reset_memory.sv', 'sim/net21/tb_reset_memory.sv', []),
        ('tools/run_reset_memory.py', 'tools/run_schmitt_memory.py', []),
        ('tools/run_reset_scan.py', 'tools/run_schmitt_scan.py', []),
        ('tools/run_system_hold_up.py', 'tools/run_schmitt_hold_up.py', [
            ('# TPS3703F6050: nominal 0.5V, UV -6%, accuracy +/-1% below 800mV.', '# TPS3808G01: nominal .405V, accuracy +/-2%.'),
            ('# External divider 950/100 ohm. +/-10uA is an explicit sense-current', '# External divider1120/100 ohm; +/-25nA is specified at SENSE=VIT.'),
            ('# qualification budget, not a guaranteed datasheet value at every voltage.', '# That input-current condition is not extended to arbitrary input voltages.'),
            ('trip=.5*.94*.99*(1+950*.999/(100*1.001))-10e-6*950*1.001',
             'trip=.405*.98*(1+1120*.999/(100*1.001))-25e-9*1120*1.001'),
            ("'TPS3703F6050DSER'", "'TPS3808G01DBVR'"),
            ("'divider_top_ohm':950", "'divider_top_ohm':1120"),
            ("'sense_abs_current_budget_a':10e-6", "'sense_abs_current_budget_a':25e-9"),
            ("'detect_delay_budget_s':30e-6", "'detect_delay_budget_s':20e-6"),
            ('we=31.1e-6', 'we=21.1e-6'),
            ('Supervisor 30us applies', 'Supervisor 20us applies'),
            ("sources=['tools/run_system_hold_up.py'", "sources=['tools/prepare_schmitt_checks.py','tools/run_system_hold_up.py'"),
            ('references/power-candidates/tps3703.pdf', 'references/net20/tps3808.pdf'),
            ('AHC125 input max10pF leaves no trace allowance in supervisor CL10pF test condition. That interface is NOT qualified.',
             'Schmitt input max10pF at5V plus trace budget10pF fits CL50pF test load. Board cap/POR/transients still require qualification.'),
        ]),
        ('tools/check_system_reset_erc.py', 'tools/check_schmitt_reset_erc.py', []),
    ]
    records = []
    for source, target, changes in transforms:
        text = (ROOT / source).read_text()
        for old, new in changes:
            if old not in text:
                raise ValueError('Missing predecessor fragment ' + old)
            text = text.replace(old, new)
        for old, new in [
            ('verification/net20', 'verification/net21'), ('sim/net20/', 'sim/net21/'),
            ('sim/net21/isa1_memory_reset.sv', 'sim/net21/isa1_memory_schmitt.sv'),
            ('system_reset', 'schmitt_reset'), ('NET20', 'NET21'), ('NET-20', 'NET-21'),
            ('tools/run_reset_memory.py', 'tools/run_schmitt_memory.py'),
            ('tools/run_reset_scan.py', 'tools/run_schmitt_scan.py'),
            ('tools/run_system_hold_up.py', 'tools/run_schmitt_hold_up.py'),
            ('tools/make_reset_system.py', 'tools/prepare_schmitt_checks.py'),
        ]:
            text = text.replace(old, new)
        path = ROOT / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        records.append({'source': source, 'source_sha256': hashlib.sha256((ROOT / source).read_bytes()).hexdigest(),
                        'target': target, 'target_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'check-origin.json').write_text(json.dumps({'date': '2026-11-26', 'transformations': records,
        'scope': 'NET21 Schmitt/supervisor variant: same native CPU/MMIO/raster/payload graph; new reset package. Conditional hold-up changes detection to20us, divider1120/100 and threshold.405V +/-2%. No analog supervisor model or board approval.'}, indent=2) + '\n')
    print('Generated separate NET21 adapters and checks')


if __name__ == '__main__':
    main()
