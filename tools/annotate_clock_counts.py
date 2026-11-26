"""Correct package classification metadata without changing tested circuit bytes."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    path=ROOT/'verification/net23/native/schematic-check.json'
    original=path.read_bytes()
    data=json.loads(original)
    if data.get('package_count_correction'):raise ValueError('Already annotated')
    design_path=ROOT/'hardware/clocked_reset/design.json'
    parts=json.loads(design_path.read_text())['parts']
    digital=sum(p['part'].startswith('SN74') for p in parts)
    supervisors=sum(p['part'].startswith('TPS3808') for p in parts)
    oscillators=sum(p['part'].startswith('ACH_') for p in parts)
    assert (digital,supervisors,oscillators)==(7,1,2)
    saved=ROOT/'verification/net23/development/package-count-metadata/schematic-check-original.json'
    saved.parent.mkdir(parents=True,exist_ok=True)
    saved.write_bytes(original)
    data['logic_ics']=digital
    data['supervisor_ics']=supervisors
    data['package_count_correction']={'date':'2026-11-26','original_logic_ics':8,
        'reason':'Eight original IC packages comprise seven SN74 logic ICs plus one TPS3808 supervisor; two oscillator modules are separate. Classification-only correction, no rebuild or repeated simulation.',
        'original_report':saved.relative_to(ROOT).as_posix(),'original_sha256':hashlib.sha256(original).hexdigest()}
    data['sources'] += [{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in
                       ['tools/annotate_clock_counts.py','hardware/clocked_reset/design.json']]
    path.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'ics':8,'logic_ics':digital,'supervisor_ics':supervisors,'oscillator_modules':oscillators,'circuit_bytes_changed':False}))


if __name__=='__main__':main()
