"""NET20 candidate: fast CPU reset, delayed memory banks, buffered clocks.

The CPU no longer directly drives SRAM address/data: held HC377 payload allows
fast CPU reset while all memory-affecting banks remain behind the RC delay.
Supervisor analog behavior is still a qualified external digital forcepoint.
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
import build_power_reset as previous

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/system_reset'
VERIFY=ROOT/'verification/net20/native'


def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net20/reset/'+s))


def definitions():return copy.deepcopy(previous.definitions())


def design(defs):
    parts=copy.deepcopy(previous.design(defs))
    def connect(ref,function,net):
        part=next(p for p in parts if p['reference']==ref)
        pin=next(pin for pin,s in defs[part['part']]['pins'].items() if s['name']==function)
        part['nets'][pin]=net
    for channel,name,source in [(1,'SAFE_MEMORY','ACCESS_SAFE'),(2,'SAFE_KEYBOARD','ACCESS_SAFE'),(3,'BANK_DECODE_N','BANK_MEMORY_N')]:
        connect('U1',f'A{channel}',source);connect('U1',f'OE{channel}_N','GND');connect('U1',f'Y{channel}',name)
    # Asynchronous CPU assertion is independent of RC. CPU release waits for
    # memory banks, then two CPU-clock edges; no asynchronous RUN gating.
    connect('U4','A2','RAW_BUFFERED');connect('U4','B2','BANK_RESET_N');connect('U4','Y2','CPU_CLEAR_FAST_N')
    for channel in range(2):
        connect('U3',f'CLK{channel}','BANK_RESET_CLK')
        connect('U5',f'CLK{channel}','CPU_RESET_CLK')
        connect('U5',f'CLR{channel}_N','CPU_CLEAR_FAST_N')
    def add_buffer(ref,x,y,channels):
        fs={}
        for i,(source,target) in enumerate(channels):fs.update({f'A{i}':source,f'Y{i}':target,f'OE{i}_N':'GND'})
        pins={p:fs.get(s['name']) for p,s in defs['SN74AHC125']['pins'].items()}
        for p,s in defs['SN74AHC125']['pins'].items():
            if s['name'] in ('VCC','GND'):pins[p]='+5V' if s['name']=='VCC' else 'GND'
        parts.append({'reference':ref,'part':'SN74AHC125','x':round(x/1.27)*1.27,'y':round(y/1.27)*1.27,'nets':pins})
    add_buffer('U7',290,330,[('BANK_RESET_N','BANK_MEMORY_N'),('BANK_RESET_N','BANK_KEYBOARD_N'),('CPU_CLK','CPU_CORE_CLK'),('CPU_CLK','CPU_RESET_CLK')])
    add_buffer('U8',510,330,[('BACKEND','BACKEND_ROOT'),('BACKEND_ROOT','ACCESS_CLK'),('BACKEND_ROOT','KEYBOARD_CLK'),('BACKEND_ROOT','BANK_RESET_CLK')])
    for i,x in [(11,320),(12,540)]:
        parts.append({'reference':f'C{i}','part':'C','value':'100nF','x':round(x/1.27)*1.27,'y':round(300/1.27)*1.27,'nets':{'1':'+5V','2':'GND'}})
    return parts


def package_symbol(kind,spec):
    return tuple(x.replace('NET18:','NET20:') if isinstance(x,str) else x for x in previous.package_symbol(kind,spec))


emitter=previous.emitter.replace('power_reset','system_reset').replace('NET18','NET20').replace('NET-18','NET-20')
exec(emitter,globals())
converter=previous.converter.replace('power_reset','system_reset')
converter=converter.replace("'BACKEND':'backend_clk','CPU_CLK':'cpu_clk'","'BACKEND':'backend_source','CPU_CLK':'cpu_source'")
old="outputs={'BANK_RESET_N':'bank_reset_n','CPU_RESET_N':'cpu_reset_n','ACCESS_SAFE':'access_safe'}"
new="outputs={'BANK_RESET_N':'bank_reset_n','CPU_RESET_N':'cpu_reset_n','ACCESS_SAFE':'access_safe','BANK_MEMORY_N':'bank_memory_n','BANK_KEYBOARD_N':'bank_keyboard_n','BANK_DECODE_N':'bank_decode_n','SAFE_MEMORY':'safe_memory','SAFE_KEYBOARD':'safe_keyboard','CPU_CORE_CLK':'cpu_core_clk','ACCESS_CLK':'access_clk','KEYBOARD_CLK':'keyboard_clk'}"
assert converter.count(old)==1;converter=converter.replace(old,new)
old='''if kind=='SN74AHC125':lines.append(f"assign #(TIMED?10:0) {fs['Y0']}={fs['OE0_N']} ? 1'bz : {fs['A0']};")'''
new='''if kind=='SN74AHC125':
            for i in range(4):
                if f'Y{i}' in fs:lines.append(f"assign #(TIMED?10:0) {fs[f'Y{i}']}={fs[f'OE{i}_N']} ? 1'bz : {fs[f'A{i}']};")'''
assert converter.count(old)==1;converter=converter.replace(old,new)
old='input wire raw_safe_n,backend_clk,cpu_clk,output wire bank_reset_n,cpu_reset_n,access_safe'
new='input wire raw_safe_n,backend_source,cpu_source,output wire bank_reset_n,cpu_reset_n,access_safe,bank_memory_n,bank_keyboard_n,bank_decode_n,safe_memory,safe_keyboard,cpu_core_clk,access_clk,keyboard_clk'
assert converter.count(old)==1;converter=converter.replace(old,new).replace("'ics':6","'ics':8")
exec(converter,globals())
digital_convert=convert


def convert(path=None,destination=None):
    path=path or VERIFY/'system_reset.xml';report=digital_convert(path,destination)
    root=ET.parse(path).getroot();raw=next(n for n in root.findall('./nets/net') if n.get('name').removeprefix('/')=='RAW_SAFE_N')
    if {(n.get('ref'),n.get('pin')) for n in raw.findall('node')}!={('U6','4'),('R4','2'),('U1','2')}:
        raise ValueError('Supervisor RESET exceeds one CMOS load')
    report.update(scope='Exact pin graph with fast CPU assertion and delayed memory banks, qualified RAW supervisor forcepoint, bounded RC and binary release. Not analog supervisor, global PVT/skew/MTBF or fabrication approval',
                  supervisor_cmos_loads=1,clock_distribution_added=True,cpu_run_gated=False,
                  clock_skew_independent_corners_qualified=False,production_released=False)
    return report


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=definitions();parts=design(defs);emit(defs,parts)
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n')
    (OUT/'design.json').write_text(json.dumps({'iteration':'NET-20A','parts':parts},indent=2)+'\n')
    cmd=[KICAD,'sch','export','netlist','--format','kicadxml','-o',str(VERIFY/'system_reset.xml'),str(OUT/'system_reset.kicad_sch')]
    subprocess.run(cmd,check=True,capture_output=True,timeout=120)
    report=convert();report.update(date='2026-11-26',command=cmd,kicad=subprocess.check_output([KICAD,'version'],text=True).strip(),
      sources=[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in ['tools/build_system_reset.py','tools/build_power_reset.py','hardware/power_reset/design.json']])
    (VERIFY/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return 0


if __name__=='__main__':raise SystemExit(main())
