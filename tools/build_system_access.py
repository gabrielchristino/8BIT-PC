"""Separate NET19 controller candidate: three physical HC174 -> AHC174.

Same logic, state/payload/ports and pin maps. Original NET15 is immutable.
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
from build_stack_bank import symbol
from build_cpu_global import KICAD
from build_memory_decode import sig
import build_keyboard_access as previous

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/system_access'
VERIFY=ROOT/'verification/net19a/native'
PHASES=previous.PHASES
ports=previous.ports


def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net19/access/'+s))


def definitions():
    defs=copy.deepcopy(previous.definitions())
    defs['SN74AHC174']=copy.deepcopy(defs['SN74HC174'])
    defs['SN74AHC174'].update(datasheet='https://www.ti.com/lit/ds/symlink/sn74ahc174.pdf',
                            source='SCLS425H table 4-1, 16-pin complete package; 5V +/-0.5V, -40..85C, CL<=50pF candidate')
    return defs


def design(defs):
    parts=copy.deepcopy(previous.design(defs))
    changed=[]
    for part in parts:
        if part['part']=='SN74HC174':
            assert defs['SN74HC174']['pins']==defs['SN74AHC174']['pins']
            part['part']='SN74AHC174';changed.append(part['reference'])
    assert changed==['U1','U2','U3']
    return parts


emitter=inspect.getsource(previous.previous.emit).replace('memory_access','system_access').replace('NET13A','NET19A').replace('NET-13A','NET-19A').replace('2026-11-25','2026-11-26')
exec(emitter,globals())
converter=previous._converter.replace('keyboard_access','system_access')
line='''if kind=='SN74HC174':lines.append(f"hc174_model #(.TIMED(TIMED)) {ref}({fs['CLK']},{fs['CLR_N']},{vec('D',6)},{vec('Q',6)});")'''
assert converter.count(line)==1
converter=converter.replace(line,'''if kind=='SN74AHC174':lines.append(f"net19_ahc174 #(.TIMED(TIMED),.EARLY(EARLY)) {ref}({fs['CLK']},{fs['CLR_N']},{vec('D',6)},{vec('Q',6)});")
        el'''+line)
converter=converter.replace('module system_access_netlist #(parameter TIMED=0)', 'module system_access_netlist #(parameter TIMED=0,EARLY=0)')
exec(converter,globals())


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=definitions();parts=design(defs);emit(defs,parts)
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n')
    (OUT/'design.json').write_text(json.dumps({'iteration':'NET-19A','parts':parts,'replaced':['U1','U2','U3'],'logic_change':False},indent=2)+'\n')
    cmd=[KICAD,'sch','export','netlist','--format','kicadxml','-o',str(VERIFY/'system_access.xml'),str(OUT/'system_access.kicad_sch')]
    subprocess.run(cmd,check=True,capture_output=True,timeout=120)
    report=convert();report.update(date='2026-11-26',command=cmd,kicad=subprocess.check_output([KICAD,'version'],text=True).strip(),
        transformation='Exactly three HC174 state packages replaced by pin-compatible AHC174, identical logic and passives; ancestor preserved',
        sources=[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in ['tools/build_system_access.py','tools/build_keyboard_access.py','hardware/keyboard_access/design.json','references/ti/sn74ahc174.pdf']])
    (VERIFY/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
    return int(bool(report['failures']))


if __name__=='__main__':raise SystemExit(main())
