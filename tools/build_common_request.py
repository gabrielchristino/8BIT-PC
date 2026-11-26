"""NET24: move both request synchronizer clocks onto the MDR clock branch."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import uuid
import xml.etree.ElementTree as ET
from build_stack_bank import symbol
from build_cpu_global import KICAD
from build_memory_decode import sig
import build_system_access as previous

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/common_request'
VERIFY=ROOT/'verification/net24/native'
PHASES=previous.PHASES
ports=previous.ports


def uid(text):return str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net24/request/'+text))


def definitions():
    return copy.deepcopy(json.loads((ROOT/'hardware/system_access/package-functions.json').read_text()))


def design(defs):
    parts=copy.deepcopy(json.loads((ROOT/'hardware/system_access/design.json').read_text())['parts'])
    sync=next(p for p in parts if p['reference']=='U4')
    assert sync['part']=='SN74HC74'
    assert sync['nets']['3']=='BUF_3_3' and sync['nets']['11']=='BUF_3_4'
    sync['nets']['3']=sync['nets']['11']='BUF_4_1'
    return parts


emitter=previous.emitter.replace('system_access','common_request').replace('NET19A','NET24').replace('NET-19A','NET-24')
exec(emitter,globals())
converter=previous.converter.replace('system_access','common_request')
exec(converter,globals())


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=definitions();parts=design(defs);emit(defs,parts)
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n')
    (OUT/'design.json').write_text(json.dumps({'iteration':'NET24 candidate','parts':parts,
        'transformation':'U4 CLK0/CLK1 both move to BUF_4_1; all data/reset/gates/parts and other clocks unchanged'},indent=2)+'\n')
    command=[KICAD,'sch','export','netlist','--format','kicadxml','-o',str(VERIFY/'common_request.xml'),str(OUT/'common_request.kicad_sch')]
    result=subprocess.run(command,capture_output=True,text=True,timeout=120)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    report=convert()
    report.update(date='2026-11-26',command=command,kicad=subprocess.check_output([KICAD,'version'],text=True).strip(),
        transformation='Exactly two clock pin connections U4.3/U4.11 regroup request FFs with MDR on BUF_4_1. Old state/payload branches now three CLK inputs each; new common request/MDR branch three. No part or logic removal.',
        sources=[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in
                 ['tools/build_common_request.py','tools/build_system_access.py','hardware/system_access/design.json',
                  'hardware/system_access/package-functions.json','references/ti/sn74hc74.pdf','references/ti/sn74ahc125.pdf']],
        scope='Native request clock regrouping candidate. Original HC74 second-stage monitor preserved, first-stage analog metastability still unmodeled; no global PVT/skew/MTBF or fabrication qualification.',production_released=False)
    (VERIFY/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
    return int(bool(report['failures']) or report['max_signal_input_loads']>4)


if __name__=='__main__':raise SystemExit(main())
