"""NET-11 memory region/address decoder, separate from physical access strobes."""
import csv
import hashlib
import json
import re
import subprocess
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from build_x_register_bank import definitions
from build_stack_bank import symbol
from build_cpu_global import KICAD
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/memory_decode'
VERIFY=ROOT/'verification/net11'


def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net11/'+s))
def sig(n):return "1'b1" if n=='+5V' else "1'b0" if n=='GND' else 'n_'+re.sub('[^a-zA-Z0-9_]','_',n)


def ports():
    ins={'BOOT':'boot','EB':'eb','VB_0':'vb[0]','VB_1':'vb[1]','ACCESS':'access','SAFE':'safe'}
    ins.update({f'ADDRESS_{i}':f'address[{i}]' for i in range(16)})
    outs={f'SELECT_{n}':f'select[{i}]' for i,n in enumerate(('RAM','VRAM','ROM','IO'))}
    outs.update({f'IO_{n}':f'io_select[{i}]' for i,n in enumerate(('VB','EB','BOOT','ROW','COL_LO','COL_HI'))})
    for name in ('RAM','VRAM','ROM'):outs.update({f'{name}_ADDRESS_{i}':name.lower()+f'_address[{i}]' for i in range(15)})
    return ins,outs


def design(defs):
    parts=[];gates=[];cache={};channels=[]
    def part(kind,fs):
        nets={pin:fs.get(spec['name']) for pin,spec in defs[kind]['pins'].items()}
        for pin,spec in defs[kind]['pins'].items():
            if spec['name'] in ('VCC','GND'):nets[pin]='+5V' if spec['name']=='VCC' else 'GND'
        p={'reference':f'U{len(parts)+1}','part':kind,'nets':nets};parts.append(p);return p
    def gate(kind,*args,name=None):
        if kind!='SN74HC04':args=tuple(sorted(args))
        key=(kind,args)
        if key in cache and name is None:return cache[key]
        n=name or f'G_{len(gates)}';gates.append((kind,args,n));cache[key]=n;return n
    def NOT(a):return gate('SN74HC04',a)
    def AND(a,b,name=None):return gate('SN74HC08',a,b,name=name)
    def OR(a,b):return gate('SN74HC32',a,b)
    def tree(op,items):
        items=list(items)
        while len(items)>1:items=[op(*items[i:i+2]) if len(items[i:i+2])==2 else items[i] for i in range(0,len(items),2)]
        return items[0]
    def buf(n,out):
        if not channels or channels[-1][1]==4:channels.append([part('SN74HC125',{**{f'A{i}':'GND' for i in range(4)},**{f'OE{i}_N':'GND' for i in range(4)}}),0])
        p,i=channels[-1];channels[-1][1]+=1
        for pin,spec in defs['SN74HC125']['pins'].items():
            if spec['name']==f'A{i}':p['nets'][pin]=n
            if spec['name']==f'Y{i}':p['nets'][pin]=out
    a=[f'ADDRESS_{i}' for i in range(16)]
    overlay=AND('BOOT',NOT(OR(a[15],a[14])))
    rawram=AND(NOT(a[15]),NOT(overlay))
    rawvram=AND(a[15],NOT(OR(a[14],a[13])))
    rawio=AND(AND(a[15],NOT(a[14])),a[13])
    rawrom=OR(AND(a[15],a[14]),overlay)
    active=AND('SAFE','ACCESS')
    for name,n in zip(('RAM','VRAM','ROM','IO'),(rawram,rawvram,rawrom,rawio)):AND(active,n,'SELECT_'+name)
    # MMIO register selects are exact, qualified address matches. They are not
    # write pulses and must feed a single-commit backend in the next stage.
    for name,value in [('VB',0xa000),('EB',0xa001),('BOOT',0xa002),('ROW',0xa010),('COL_LO',0xa011),('COL_HI',0xa012)]:
        match=tree(AND,[a[i] if value>>i&1 else NOT(a[i]) for i in range(16)])
        AND(active,match,'IO_'+name)
    for i in range(15):
        buf(a[i],f'RAM_ADDRESS_{i}')
        buf(a[i] if i<13 else f'VB_{i-13}',f'VRAM_ADDRESS_{i}')
        buf(a[i] if i<14 else AND(a[15],'EB'),f'ROM_ADDRESS_{i}')
    for kind in ('SN74HC08','SN74HC32','SN74HC04'):
        selected=[g for g in gates if g[0]==kind];cap=6 if kind=='SN74HC04' else 4
        for start in range(0,len(selected),cap):
            fs={}
            for i in range(cap):
                g=selected[start+i] if start+i<len(selected) else None
                fs[f'A{i}']=g[1][0] if g else 'GND'
                if cap==4:fs[f'B{i}']=g[1][1] if g else 'GND'
                fs[f'Y{i}']=g[2] if g else None
            part(kind,fs)
    while True:
        loads={}
        for p in parts:
            for pin,n in p['nets'].items():
                if defs[p['part']]['pins'][pin]['type']=='input' and n not in ('+5V','GND'):loads.setdefault(n,[]).append((p,pin))
        over=next(((n,v) for n,v in loads.items() if len(v)>4),None)
        if over is None:break
        n,targets=over
        for start in range(0,len(targets),4):
            out='FANOUT_'+str(len(channels))+'_'+str(channels[-1][1] if channels else 0)
            buf(n,out)
            for p,pin in targets[start:start+4]:p['nets'][pin]=out
    if len(parts)>56:raise ValueError('Sheet capacity')
    for i,p in enumerate(list(parts)):
        p.update(x=round((60+98*(i%8))/1.27)*1.27,y=round((65+75*(i//8))/1.27)*1.27)
        parts.append({'reference':f'C{i+1}','part':'C','nets':{'1':'+5V','2':'GND'},'x':p['x']+31.75,'y':p['y']-25.4})
    return parts


def emit(defs,parts):
    prepared={k:(symbol(k,v)[0].replace('NET02:','NET11:'),symbol(k,v)[1]) for k,v in defs.items()}
    (OUT/'memory_packages.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor) '+' '.join(v[0].replace('(symbol "NET11:', '(symbol "') for v in prepared.values())+')\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "NET11") (type "KiCad") (uri "${KIPRJMOD}/memory_packages.kicad_sym") (options "") (descr "ISA-1 memory decode package pins")))\n')
    project=OUT/'memory_decode.kicad_pro'
    if not project.exists():project.write_text(json.dumps({'meta':{'filename':project.name,'version':1}},indent=2)+'\n')
    sheet=uid('sheet');lines=[f'(kicad_sch (version 20230121) (generator eeschema) (uuid {sheet}) (paper "A1")',
        '(title_block (title "ISA-1 memory address decoder") (date "2026-11-25") (rev "NET-11") (comment 1 "ADDRESS DECODE ONLY - NO MEMORY STROBES - NOT FOR PRODUCTION"))',
        '(lib_symbols '+' '.join(v[0] for v in prepared.values())+')'];rows=[]
    for p in parts:
        ref,kind,x,y=p['reference'],p['part'],p['x'],p['y'];value='100nF' if kind=='C' else kind
        ax,ay=(x+5,y-2) if kind=='C' else (x,y-25.4)
        props=f'(property "Reference" "{ref}" (at {ax} {ay} 0) (effects (font (size 1 1)))) (property "Value" "{value}" (at {ax} {ay+2.54} 0) (effects (font (size 1 1))))'
        pins=' '.join(f'(pin "{pin}" (uuid {uid(ref+"/"+pin)}))' for pin in p['nets'])
        lines.append(f'(symbol (lib_id "NET11:{kind}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (uuid {uid(ref)}) {props} {pins} (instances (project "memory_decode" (path "/{sheet}" (reference "{ref}") (unit 1)))))')
        for pin,n in p['nets'].items():
            px,py,angle=prepared[kind][1][pin];px+=x;py=y-py
            rows.append({'reference':ref,'part':kind,'pin':pin,'function':defs[kind]['pins'][pin]['name'],'net':n or 'NC'})
            if n is None:lines.append(f'(no_connect (at {px} {py}) (uuid {uid(ref+"/nc/"+pin)}))')
            else:lines.append(f'(label "{n}" (at {px} {py} 0) (effects (font (size 0.7 0.7)) (justify {"right bottom" if angle==0 else "left bottom"})) (uuid {uid(ref+"/label/"+pin)}))')
    lines+=['(sheet_instances (path "/" (page "1")))',')'];(OUT/'memory_decode.kicad_sch').write_text('\n'.join(lines)+'\n')
    with (OUT/'pinmap.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    return rows


def convert(source=None,destination=None):
    source=source or VERIFY/'memory_decode.xml';destination=destination or OUT/'memory_decode_netlist.sv'
    defs=json.loads((OUT/'package-functions.json').read_text());parts=json.loads((OUT/'design.json').read_text())['parts'];expected={p['reference']:p for p in parts}
    root=ET.parse(source).getroot();actual={};nets=set();ins,outs=ports();drivers={n:['external'] for n in [*ins,'+5V','GND']};inputs=[];loads={};seen=set()
    for net in root.findall('./nets/net'):
        n=net.get('name').removeprefix('/');nets.add(n)
        for node in net.findall('node'):
            key=node.get('ref'),node.get('pin')
            if key in actual:raise ValueError('Multiple nets '+str(key))
            actual[key]=n
    lines=[]
    for comp in root.findall('./components/comp'):
        ref=comp.get('ref');p=expected[ref];kind=p['part'];fs={};seen.add(ref)
        if comp.findtext('value')!=('100nF' if kind=='C' else kind):raise ValueError('Value changed '+ref)
        for pin,spec in defs[kind]['pins'].items():
            n=actual.get((ref,pin));name,typ=spec['name'],spec['type']
            if typ in ('input','power_in') and (not n or n.startswith('unconnected-')):raise ValueError('Floating input '+ref+'/'+pin)
            if name in ('VCC','GND') and n!={'VCC':'+5V','GND':'GND'}[name]:raise ValueError('Wrong power '+ref)
            if n:fs[name]=sig(n)
            if typ=='input':inputs.append((ref,pin,n));loads.setdefault(n,[]).append(ref+'/'+pin)
            if typ=='output' and n:drivers.setdefault(n,[]).append(ref+'/'+pin)
        if kind=='C':continue
        if kind in ('SN74HC08','SN74HC32'):
            op='&' if kind=='SN74HC08' else '|'
            for i in range(4):
                if f'Y{i}' in fs:lines.append(f"assign #GATE_T {fs[f'Y{i}']}={fs[f'A{i}']} {op} {fs[f'B{i}']};")
        elif kind=='SN74HC04':
            for i in range(6):
                if f'Y{i}' in fs:lines.append(f"assign #INV_T {fs[f'Y{i}']}=~{fs[f'A{i}']};")
        elif kind=='SN74HC125':
            for i in range(4):
                if f'Y{i}' in fs:lines.append(f"assign #BUF_T {fs[f'Y{i}']}={fs[f'OE{i}_N']} ? 1'bz : {fs[f'A{i}']};")
        else:raise ValueError('No model '+kind)
    if seen!=set(expected):raise ValueError('Inventory mismatch')
    for ref,pin,n in inputs:
        if len(drivers.get(n,[]))!=1:raise ValueError('Driver count '+ref+'/'+pin+' '+str(n))
    if any(len(d)!=1 for d in drivers.values()):raise ValueError('Multiple drivers')
    for n in outs:
        if len(drivers.get(n,[]))!=1:raise ValueError('Undriven output '+n)
    names=[sig(n) for n in nets if n not in ('+5V','GND')]
    if len(names)!=len(set(names)):raise ValueError('Name collision')
    header=['`timescale 1ns/1ps','// GENERATED from KiCad XML. Address decode only, not memory write/read sequencing.',
      'module memory_decode_netlist #(parameter TIMED=0)(input wire [15:0] address,input wire boot,eb,input wire [1:0] vb,input wire access,safe,output wire [3:0] select,output wire [5:0] io_select,output wire [14:0] ram_address,vram_address,rom_address);',
      'localparam GATE_T=TIMED?31:0,INV_T=TIMED?24:0,BUF_T=TIMED?36:0;']
    header+=['wire '+n+';' for n in sorted(names)]
    header+=[f'assign {sig(n)}={v};' for n,v in ins.items()]
    lines+=[f'assign {v}={sig(n)};' for n,v in outs.items()];lines+=['endmodule'];destination.write_text('\n'.join(header+lines)+'\n')
    report={'date':'2026-11-25','components':len(seen),'pins':sum(len(p['nets']) for p in parts),'no_connects':sum(n is None for p in parts for n in p['nets'].values()),'max_signal_input_loads':max(len(v) for n,v in loads.items() if n not in ('+5V','GND')),'failures':[]}
    return report


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=definitions();defs={k:v for k,v in defs.items() if k in ('SN74HC08','SN74HC32','SN74HC04','SN74HC125','C')};parts=design(defs)
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n');(OUT/'design.json').write_text(json.dumps({'iteration':'NET-11','parts':parts},indent=2)+'\n');rows=emit(defs,parts)
    command=[KICAD,'sch','export','netlist','--format','kicadxml','-o',str(VERIFY/'memory_decode.xml'),str(OUT/'memory_decode.kicad_sch')]
    r=subprocess.run(command,capture_output=True,text=True,timeout=120)
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    report=convert();report.update(kicad=subprocess.check_output([KICAD,'version'],text=True).strip(),command=command)
    actual={}
    for n in ET.parse(VERIFY/'memory_decode.xml').getroot().findall('./nets/net'):
        for p in n.findall('node'):actual[p.get('ref'),p.get('pin')]=n.get('name').removeprefix('/')
    for row in rows:
        found=actual.get((row['reference'],row['pin']))
        if row['net']!='NC' and found!=row['net']:report['failures'].append(row)
        if row['net']=='NC' and found and not found.startswith('unconnected-'):report['failures'].append(row)
    (VERIFY/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return int(bool(report['failures']) or report['max_signal_input_loads']>4)


if __name__=='__main__':raise SystemExit(main())
