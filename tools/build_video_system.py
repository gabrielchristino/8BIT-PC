"""NET-14C separate native variant: backend clock has no asynchronous clear.

Registered backend transitions occur only on master edges, so CPU reset cannot
truncate its pulse. Preserve the NET-14B design and record the changed pin.
"""
import copy
import csv
import inspect
import json
from pathlib import Path
import subprocess
import uuid
import xml.etree.ElementTree as ET
from build_cpu_global import KICAD
from build_memory_decode import sig
from build_stack_bank import symbol as old_symbol
import build_video_raster as previous

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/video_system';VERIFY=ROOT/'verification/net14c/native'
definitions=previous.definitions
ports=previous.ports


def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net14c/system/'+s))


def design(defs):
    parts=copy.deepcopy(previous.design(defs));changed=[]
    for p in parts:
        if p['part']!='SN74AHC74':continue
        for ch in range(2):
            qpin=next(pin for pin,x in defs[p['part']]['pins'].items() if x['name']==f'Q{ch}')
            if p['nets'][qpin]!='BACKEND':continue
            pin=next(pin for pin,x in defs[p['part']]['pins'].items() if x['name']==f'CLR{ch}_N')
            changed.append({'reference':p['reference'],'pin':pin,'from':p['nets'][pin],'to':'+5V','reason':'Never asynchronously truncate backend clock; cleared phases are sampled on subsequent master edges'})
            p['nets'][pin]='+5V'
    assert len(changed)==1
    (VERIFY/'changed-pin.json').write_text(json.dumps(changed,indent=2)+'\n')
    return parts


def package_symbol(kind,spec):
    return tuple(x.replace('NET02:','NET14C:') if isinstance(x,str) else x for x in old_symbol(kind,spec))


exec(previous._emitter.replace('video_raster','video_system').replace('NET14B','NET14C').replace('NET-14B','NET-14C'),globals())
exec(inspect.getsource(previous.convert).replace('video_raster','video_system'),globals())


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=definitions();parts=design(defs);emit(defs,parts)
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n')
    (OUT/'design.json').write_text(json.dumps({'iteration':'NET-14C','parts':parts},indent=2)+'\n')
    cmd=[KICAD,'sch','export','netlist','--format','kicadxml','-o',str(VERIFY/'video_system.xml'),str(OUT/'video_system.kicad_sch')]
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    report=convert();report.update(command=cmd,kicad=subprocess.check_output([KICAD,'version'],text=True).strip())
    (VERIFY/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return int(bool(report['failures']))


if __name__=='__main__':raise SystemExit(main())
