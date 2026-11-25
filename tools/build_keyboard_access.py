"""NET-15 separate memory controller waits for settled column reads.

Preserve NET-13 access controller, phase/ownership/dead-driver contracts.
"""
import copy
import csv
import inspect
import json
from pathlib import Path
import subprocess
import uuid
import xml.etree.ElementTree as ET
from build_stack_bank import symbol
from build_cpu_global import KICAD
from build_memory_decode import sig
import build_memory_bus_access as previous

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/keyboard_access';VERIFY=ROOT/'verification/net15/access'
PHASES=previous.PHASES;definitions=previous.definitions


def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net15/access/'+s))


def ports():
    ins,outs=previous.ports()
    ins.update({'KEY_READY':'key_ready','IO_COL_LO':'io_col_lo','IO_COL_HI':'io_col_hi'})
    return ins,outs


_design=inspect.getsource(previous.design)
old="    can_start=OR(NOT('SELECT_1'),'VRAM_SLOT')"
new="""    column_read=A('READ_FLAG','SELECT_3',OR('IO_COL_LO','IO_COL_HI'))
    key_ok=OR(NOT(column_read),'KEY_READY')
    can_start=AND(OR(NOT('SELECT_1'),'VRAM_SLOT'),key_ok)"""
assert _design.count(old)==1
exec(_design.replace(old,new),globals())
exec(inspect.getsource(previous.emit).replace('memory_access','keyboard_access').replace('NET13A','NET15A').replace('NET-13A','NET-15A'),globals())
_converter=inspect.getsource(previous.convert).replace('memory_access','keyboard_access')
_converter=_converter.replace('request,write_request,vram_slot,input wire','request,write_request,vram_slot,key_ready,io_col_lo,io_col_hi,input wire')
exec(_converter,globals())


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=definitions();parts=design(defs);rows=emit(defs,parts)
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n')
    (OUT/'design.json').write_text(json.dumps({'iteration':'NET-15A','parts':parts},indent=2)+'\n')
    cmd=[KICAD,'sch','export','netlist','--format','kicadxml','-o',str(VERIFY/'keyboard_access.xml'),str(OUT/'keyboard_access.kicad_sch')]
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    report=convert();report.update(command=cmd,kicad=subprocess.check_output([KICAD,'version'],text=True).strip())
    actual={}
    for n in ET.parse(VERIFY/'keyboard_access.xml').getroot().findall('./nets/net'):
        for p in n.findall('node'):actual[p.get('ref'),p.get('pin')]=n.get('name').removeprefix('/')
    for row in rows:
        found=actual.get((row['reference'],row['pin']))
        if row['net']!='NC' and found!=row['net']:report['failures'].append(row)
        if row['net']=='NC' and found and not found.startswith('unconnected-'):report['failures'].append(row)
    (VERIFY/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return int(bool(report['failures']) or report['max_signal_input_loads']>4)


if __name__=='__main__':raise SystemExit(main())
