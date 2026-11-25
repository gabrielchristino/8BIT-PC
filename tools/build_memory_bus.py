"""NET-13 native memory chips, separate I/O buses, receivers and read muxes."""
import copy
import csv
import json
from pathlib import Path
import re
import subprocess
import uuid
import xml.etree.ElementTree as ET
from build_cpu_global import KICAD
from build_memory_decode import sig
from build_stack_bank import symbol as old_symbol
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/memory_bus';VERIFY=ROOT/'verification/net13'


def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net13/bus/'+s))


def definitions():
    from build_memory_access import definitions as ad
    from build_stack_bank import definitions as sd
    defs={k:copy.deepcopy(v) for k,v in ad().items() if k in ('SN74AHC08','SN74AHC32','SN74AHC04','SN74AHC125','C')}
    defs['SN74AHCT157']=copy.deepcopy(sd()['SN74HC157']);defs['SN74AHCT157']['datasheet']='https://www.ti.com/lit/ds/symlink/sn74ahct157.pdf'
    def add(kind,ins,outs,bidir,vcc,gnd,url):
        pins={str(p):{'name':n,'type':'input'} for p,n in ins.items()}
        pins.update({str(p):{'name':n,'type':'output'} for p,n in outs.items()});pins.update({str(p):{'name':n,'type':'bidirectional'} for p,n in bidir.items()})
        pins[str(vcc)]={'name':'VCC','type':'power_in'};pins[str(gnd)]={'name':'GND','type':'power_in'}
        defs[kind]={'datasheet':url,'pins':pins,'source':'Explicit manufacturer package pin functions; package variant is part of symbol name'}
    addr={1:'A14',2:'A12',3:'A7',4:'A6',5:'A5',6:'A4',7:'A3',8:'A2',9:'A1',10:'A0',21:'A10',23:'A11',24:'A9',25:'A8',26:'A13'}
    io={p:f'IO{i}' for i,p in enumerate([11,12,13,15,16,17,18,19])}
    for kind,url in [('AS7C256A_28SOJ','https://www.alliancememory.com/wp-content/uploads/as7c256av.1.2.pdf'),('AT28C256_28PDIP','https://ww1.microchip.com/downloads/en/DeviceDoc/Industrial-Grade-256-Kbit-%2832%2C768-x-8%29-Paged-Parallel-EEPROM.pdf')]:
        add(kind,{**addr,20:'CE_N',22:'OE_N',27:'WE_N'},{},io,28,14,url)
    add('SN74HCT244',{1:'OE0_N',19:'OE1_N',**{p:f'A{i}' for i,p in enumerate([2,4,6,8,11,13,15,17])}},
        {p:f'Y{i}' for i,p in enumerate([18,16,14,12,9,7,5,3])},{},20,10,'https://www.ti.com/lit/ds/symlink/sn74hct244.pdf')
    defs['R']={'datasheet':'','pins':{'1':{'name':'1','type':'passive'},'2':{'name':'2','type':'passive'}},'source':'Proposed 3.3k pull-up, tolerance budget +/-5%; not a capacitor/rise-time proof'}
    return defs


def ports():
    ins={'RESET_N':'reset_n','POWER_GOOD':'power_good','OWNER':'vram_owner','DRIVE':'data_drive','CPU_OE_N':'oe_n','CPU_WE_N':'we_n'}
    for n,v,w in [('RAM_A','ram_address',15),('VRAM_A','vram_address',15),('ROM_A','rom_address',15),('VIDEO_A','video_address',15),('WDATA','write_data',8),('IO_DATA','io_data',8),('CS_N','cs_n',4),('SELECT','select',4)]:ins.update({f'{n}_{i}':f'{v}[{i}]' for i in range(w)})
    outs={f'READ_DATA_{i}':f'read_data[{i}]' for i in range(8)};outs.update({f'VRAM_BUFFER_{i}':f'video_data[{i}]' for i in range(8)})
    return ins,outs


def design(defs):
    parts=[];gates=[];cache={};buffers=[]
    def part(kind,fs):
        ref=f'U{sum(p["part"] not in ("C","R") for p in parts)+1}'
        pins={p:fs.get(s['name']) for p,s in defs[kind]['pins'].items()}
        for p,s in defs[kind]['pins'].items():
            if s['name'] in ('VCC','GND'):pins[p]='+5V' if s['name']=='VCC' else 'GND'
        p={'reference':ref,'part':kind,'nets':pins};parts.append(p);return p
    def gate(kind,*args,name=None):
        if kind!='SN74AHC04':args=tuple(sorted(args))
        key=kind,args
        if key in cache and name is None:return cache[key]
        n=name or f'G_{len(gates)}';gates.append((kind,args,n));cache[key]=n;return n
    def AND(a,b,name=None):return gate('SN74AHC08',a,b,name=name)
    def OR(a,b,name=None):return gate('SN74AHC32',a,b,name=name)
    def NOT(a,name=None):return gate('SN74AHC04',a,name=name)
    safe=AND('RESET_N','POWER_GOOD','SAFE');unsafe=NOT(safe)
    ram_oe=OR('CPU_OE_N',OR('CS_N_0',unsafe),'RAM_OE_N')
    ram_we=OR('CPU_WE_N',OR('CS_N_0',unsafe),'RAM_WE_N')
    vram_we=OR('CPU_WE_N',OR(NOT('OWNER'),OR('CS_N_1',unsafe)),'VRAM_WE_N')
    vram_oe=OR(unsafe,AND('OWNER','CPU_OE_N'),'VRAM_OE_N')
    rom_oe=OR('CPU_OE_N',OR('CS_N_2',unsafe),'ROM_OE_N')
    # Explicit JEDEC SOJ/PDIP maps, not the incompatible TSOP numbering.
    for kind,prefix,ce,oe,we in [('AS7C256A_28SOJ','RAM','CS_N_0',ram_oe,ram_we),('AS7C256A_28SOJ','VRAM','GND',vram_oe,vram_we),('AT28C256_28PDIP','ROM','CS_N_2',rom_oe,'+5V')]:
        part(kind,{'CE_N':ce,'OE_N':oe,'WE_N':we,**{f'A{i}':f'{prefix}_CHIP_A_{i}' if prefix=='VRAM' else f'{prefix}_A_{i}' for i in range(15)},**{f'IO{i}':f'{prefix}_IO_{i}' for i in range(8)}})
    for nib in range(4):
        first=nib*4;part('SN74AHCT157',{'G_N':'GND','SELECT':'OWNER',**{f'A{i}':f'VIDEO_A_{first+i}' if first+i<15 else 'GND' for i in range(4)},**{f'B{i}':f'VRAM_A_{first+i}' if first+i<15 else 'GND' for i in range(4)},**{f'Y{i}':f'VRAM_CHIP_A_{first+i}' if first+i<15 else None for i in range(4)}})
    for prefix,index in [('RAM',0),('VRAM',1)]:
        en=NOT(AND(AND(safe,'DRIVE'),NOT(f'CS_N_{index}')))
        for nib in range(2):
            part('SN74AHC125',{**{f'A{i}':f'WDATA_{nib*4+i}' for i in range(4)},**{f'OE{i}_N':en for i in range(4)},**{f'Y{i}':f'{prefix}_IO_{nib*4+i}' for i in range(4)}})
    for prefix in ('RAM','VRAM','ROM'):
        part('SN74HCT244',{'OE0_N':'GND','OE1_N':'GND',**{f'A{i}':f'{prefix}_IO_{i}' for i in range(8)},**{f'Y{i}':f'{prefix}_BUFFER_{i}' for i in range(8)}})
    sel0=OR('SELECT_1','SELECT_3','READ_SEL_0');sel1=OR('SELECT_2','SELECT_3','READ_SEL_1')
    for a,b,sel,out in [('RAM_BUFFER','VRAM_BUFFER',sel0,'LOW_PAIR'),('ROM_BUFFER','IO_DATA',sel0,'HIGH_PAIR'),('LOW_PAIR','HIGH_PAIR',sel1,'READ_DATA')]:
        for nib in range(2):
            part('SN74AHCT157',{'G_N':'GND','SELECT':sel,**{f'A{i}':f'{a}_{nib*4+i}' for i in range(4)},**{f'B{i}':f'{b}_{nib*4+i}' for i in range(4)},**{f'Y{i}':f'{out}_{nib*4+i}' for i in range(4)}})
    for kind in ('SN74AHC08','SN74AHC32','SN74AHC04'):
        selected=[g for g in gates if g[0]==kind];cap=6 if kind=='SN74AHC04' else 4
        for first in range(0,len(selected),cap):
            fs={}
            for i in range(cap):
                g=selected[first+i] if first+i<len(selected) else None;fs[f'A{i}']=g[1][0] if g else 'GND'
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
        for first in range(0,len(targets),4):
            if not buffers or buffers[-1][1]==4:buffers.append([part('SN74AHC125',{**{f'A{i}':'GND' for i in range(4)},**{f'OE{i}_N':'GND' for i in range(4)}}),0])
            p,i=buffers[-1];buffers[-1][1]+=1;out=f'BUF_{len(buffers)}_{i}'
            for pin,s in defs['SN74AHC125']['pins'].items():
                if s['name']==f'A{i}':p['nets'][pin]=n
                if s['name']==f'Y{i}':p['nets'][pin]=out
            for target,pin in targets[first:first+4]:target['nets'][pin]=out
    chips=list(parts)
    for i,p in enumerate(chips):
        p.update(x=round((60+98*(i%8))/1.27)*1.27,y=round((70+85*(i//8))/1.27)*1.27)
        parts.append({'reference':f'C{i+1}','part':'C','nets':{'1':'+5V','2':'GND'},'x':p['x']+31.75,'y':p['y']-27.94})
    for prefix in ('RAM','VRAM','ROM'):
        for i in range(8):
            k=len([p for p in parts if p['part']=='R']);parts.append({'reference':f'R{k+1}','part':'R','nets':{'1':'+5V','2':f'{prefix}_IO_{i}'},'x':round((45+30*k)/1.27)*1.27,'y':450.85})
    if len(chips)>40:raise ValueError('Sheet capacity')
    return parts


def package_symbol(kind,spec):
    if kind not in ('AS7C256A_28SOJ','AT28C256_28PDIP','R'):return tuple(v.replace('NET02:','NET13:') if isinstance(v,str) else v for v in old_symbol(kind,spec))
    loc={}
    if kind=='R':
        loc={'1':(0,3.81,270),'2':(0,-3.81,90)};body='(rectangle (start -1.27 2.54) (end 1.27 -2.54) (stroke (width 0.254) (type default)) (fill (type none)))';ref='R'
    else:
        for typ,x,angle in [('input',-17.78,0),('bidirectional',17.78,180)]:
            rows=[(p,s) for p,s in spec['pins'].items() if s['type']==typ]
            for i,(p,s) in enumerate(rows):loc[p]=(x,(len(rows)-1)*1.27-i*2.54,angle)
        loc['28']=(0,27.94,270);loc['14']=(0,-27.94,90);ref='U';body='(rectangle (start -12.7 25.4) (end 12.7 -25.4) (stroke (width 0.254) (type default)) (fill (type background)))'
    text=f'(symbol "NET13:{kind}" (pin_names (offset 0.508)) (in_bom yes) (on_board yes) (property "Reference" "{ref}" (at 0 34 0) (effects (font (size 1 1)))) (property "Value" "{kind}" (at 0 32 0) (effects (font (size 1 1)))) (property "Datasheet" {json.dumps(spec["datasheet"])} (at 0 0 0) (effects (font (size 1 1)) hide)) (symbol "{kind}_0_1" {body}) (symbol "{kind}_1_1" '
    for p,s in spec['pins'].items():
        x,y,angle=loc[p];text+=f'(pin {s["type"]} line (at {x} {y} {angle}) (length {2.54 if kind=="R" else 5.08}) (name "{s["name"]}" (effects (font (size 1 1)))) (number "{p}" (effects (font (size 1 1)))))'
    return text+'))',loc


def emit(defs,parts):
    prepared={k:package_symbol(k,v) for k,v in defs.items()};sheet=uid('sheet')
    (OUT/'bus_packages.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor) '+' '.join(v[0].replace('(symbol "NET13:','(symbol "') for v in prepared.values())+')\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "NET13") (type "KiCad") (uri "${KIPRJMOD}/bus_packages.kicad_sym") (options "") (descr "ISA-1 memory package pins")))\n')
    project=OUT/'memory_bus.kicad_pro'
    if not project.exists():project.write_text(json.dumps({'meta':{'filename':project.name,'version':1}},indent=2)+'\n')
    lines=[f'(kicad_sch (version 20230121) (generator eeschema) (uuid {sheet}) (paper "A1")','(title_block (title "ISA-1 SRAM / EEPROM data front-end") (date "2026-11-25") (rev "NET-13") (comment 1 "CANDIDATE - LOAD / PCB / ANALOG VALIDATION PENDING - NOT FOR PRODUCTION"))','(lib_symbols '+' '.join(v[0] for v in prepared.values())+')'];rows=[]
    for p in parts:
        ref,kind,x,y=p['reference'],p['part'],p['x'],p['y'];value='100nF' if kind=='C' else '3.3k' if kind=='R' else kind
        ax,ay=(x+5,y-2) if kind in ('C','R') else (x,y-(34.29 if '28' in kind else 25.4))
        props=f'(property "Reference" "{ref}" (at {ax} {ay} 0) (effects (font (size 1 1)))) (property "Value" "{value}" (at {ax} {ay+2.54} 0) (effects (font (size 1 1))))'
        pins=' '.join(f'(pin "{pin}" (uuid {uid(ref+"/"+pin)}))' for pin in p['nets'])
        lines.append(f'(symbol (lib_id "NET13:{kind}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (uuid {uid(ref)}) {props} {pins} (instances (project "memory_bus" (path "/{sheet}" (reference "{ref}") (unit 1)))))')
        for pin,n in p['nets'].items():
            px,py,angle=prepared[kind][1][pin];px+=x;py=y-py;rows.append({'reference':ref,'part':kind,'pin':pin,'function':defs[kind]['pins'][pin]['name'],'net':n or 'NC'})
            if n is None:lines.append(f'(no_connect (at {px} {py}) (uuid {uid(ref+"/nc/"+pin)}))')
            else:lines.append(f'(label "{n}" (at {px} {py} 0) (effects (font (size 0.65 0.65)) (justify {"right bottom" if angle==0 else "left bottom"})) (uuid {uid(ref+"/label/"+pin)}))')
    lines+=['(sheet_instances (path "/" (page "1")))',')'];(OUT/'memory_bus.kicad_sch').write_text('\n'.join(lines)+'\n')
    with (OUT/'pinmap.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    return rows


def convert(source=None,destination=None):
    source=source or VERIFY/'memory_bus.xml';destination=destination or OUT/'memory_bus_netlist.sv'
    defs=json.loads((OUT/'package-functions.json').read_text());expected={p['reference']:p for p in json.loads((OUT/'design.json').read_text())['parts']};root=ET.parse(source).getroot();nets=set();actual={}
    for net in root.findall('./nets/net'):
        n=net.get('name').removeprefix('/');nets.add(n)
        for p in net.findall('node'):
            key=p.get('ref'),p.get('pin')
            if key in actual:raise ValueError('Multiple nets '+str(key))
            actual[key]=n
    ins,outs=ports();drivers={n:[('external','strong')] for n in [*ins,'+5V','GND']};inputs=[];loads={};lines=[];seen=set();ram_writers=[];vram_writers=[]
    for c in root.findall('./components/comp'):
        ref=c.get('ref');kind=expected[ref]['part'];seen.add(ref);fs={}
        value='100nF' if kind=='C' else '3.3k' if kind=='R' else kind
        if c.findtext('value')!=value:raise ValueError('Value changed '+ref)
        for pin,s in defs[kind]['pins'].items():
            n=actual.get((ref,pin));typ=s['type'];name=s['name']
            if typ in ('input','power_in','bidirectional') and (not n or n.startswith('unconnected-')):raise ValueError('Floating input '+ref+'/'+pin)
            if name in ('VCC','GND') and n!={'VCC':'+5V','GND':'GND'}[name]:raise ValueError('Wrong power '+ref)
            if n:fs[name]=sig(n)
            if typ=='input':inputs.append((ref,pin,n));loads.setdefault(n,[]).append(ref+'/'+pin)
            if typ in ('output','bidirectional') and n:drivers.setdefault(n,[]).append((ref+'/'+pin,'tri' if typ=='bidirectional' or kind=='SN74AHC125' else 'strong'))
        def vec(prefix,w):return '{'+','.join(fs[f'{prefix}{i}'] for i in reversed(range(w)))+'}'
        if kind=='C':continue
        if kind=='R':
            if fs['1']!="1'b1" or not re.fullmatch(r'n_(RAM|VRAM|ROM)_IO_[0-7]',fs['2']):raise ValueError('Pull-up wiring '+ref)
            lines.append(f"pullup({fs['2']});");continue
        if kind in ('AS7C256A_28SOJ','AT28C256_28PDIP'):
            ro=kind.startswith('AT');seed=167 if ro else 49 if ref=='U1' else 93
            if ro and fs['WE_N']!="1'b1":raise ValueError('EEPROM WE is not permanently protected HIGH')
            lines.append(f"wire {ref}_drive; parallel_memory_32k #(.TIMED(TIMED),.READ_ONLY({int(ro)}),.SEED({seed}),.EARLY_ON(EARLY_ON)) {ref}({vec('A',15)},{fs['CE_N']},{fs['OE_N']},{fs['WE_N']},{vec('IO',8)},checks_valid,{ref}_drive);")
        elif kind=='SN74AHCT157':lines.append(f"assign #MUX_T {vec('Y',4)}={fs['G_N']} ? 4'b0 : {fs['SELECT']} ? {vec('B',4)} : {vec('A',4)};")
        elif kind=='SN74HCT244':
            for i in range(8):lines.append(f"assign #RECEIVER_T {fs[f'Y{i}']}={fs[f'OE{i//4}_N']} ? 1'bz : {fs[f'A{i}']};")
        elif kind in ('SN74AHC08','SN74AHC32'):
            op='&' if kind=='SN74AHC08' else '|'
            for i in range(4):
                if f'Y{i}' in fs:lines.append(f"assign #GATE_T {fs[f'Y{i}']}={fs[f'A{i}']} {op} {fs[f'B{i}']};")
        elif kind=='SN74AHC04':
            for i in range(6):
                if f'Y{i}' in fs:lines.append(f"assign #GATE_T {fs[f'Y{i}']}=~{fs[f'A{i}']};")
        elif kind=='SN74AHC125':
            for i in range(4):
                if f'Y{i}' not in fs:continue
                state=f'{ref}_drive{i}';lines.append(f"wire {state};assign #(BUF_ON,BUF_OFF) {state}=~{fs[f'OE{i}_N']};")
                lines.append(f"assign #(GATE_T,GATE_T,BUF_OFF) {fs[f'Y{i}']}={fs[f'OE{i}_N']} ? 1'bz : {fs[f'A{i}']};")
                n=fs[f'Y{i}']
                if n.startswith('n_RAM_IO_'):ram_writers.append(state)
                if n.startswith('n_VRAM_IO_'):vram_writers.append(state)
        else:raise ValueError('No model '+kind)
    if seen!=set(expected):raise ValueError('Inventory mismatch')
    for ref,pin,n in inputs:
        ds=drivers.get(n,[])
        if not ds:raise ValueError('Undriven '+ref+'/'+pin)
        if len(ds)>1 and not re.fullmatch(r'(RAM|VRAM|ROM)_IO_[0-7]',n):raise ValueError('Multiple drivers '+n)
    for n,ds in drivers.items():
        if len(ds)>1 and not re.fullmatch(r'(RAM|VRAM)_IO_[0-7]',n):raise ValueError('Multiple drivers '+n)
        if re.fullmatch(r'(RAM|VRAM)_IO_[0-7]',n) and (len(ds)!=2 or any(t!='tri' for _,t in ds)):raise ValueError('Invalid memory bus driver set '+n)
    for n in outs:
        if len(drivers.get(n,[]))!=1:raise ValueError('Undriven output '+n)
    if len(ram_writers)!=8 or len(vram_writers)!=8:raise ValueError('Missing write drivers')
    lines.append('wire ram_write_driving=|{'+','.join(ram_writers)+'};wire vram_write_driving=|{'+','.join(vram_writers)+'};')
    lines.append('always @(U1_drive or ram_write_driving)if(U1_drive===1 && ram_write_driving===1)$fatal(1,"SRAM output and write buffer overlap RAM");')
    lines.append('always @(U2_drive or vram_write_driving)if(U2_drive===1 && vram_write_driving===1)$fatal(1,"SRAM output and write buffer overlap VRAM");')
    names=[sig(n) for n in (nets|set(ins)) if n not in ('+5V','GND')]
    if len(names)!=len(set(names)):raise ValueError('Name collision')
    header=['`timescale 1ns/1ps','// GENERATED from actual KiCad XML. Models/fixtures are not physical validation.',
      'module memory_bus_netlist #(parameter TIMED=0,EARLY_ON=0)(input wire reset_n,power_good,vram_owner,data_drive,oe_n,we_n,input wire [14:0] ram_address,vram_address,rom_address,video_address,input wire [7:0] write_data,io_data,input wire [3:0] cs_n,select,output wire [7:0] read_data,video_data);',
      'localparam GATE_T=TIMED?10:0,MUX_T=TIMED?12:0,RECEIVER_T=TIMED?42:0,BUF_ON=TIMED?(EARLY_ON?0:10):0,BUF_OFF=TIMED?10:0;',
      'wire checks_valid=reset_n && power_good;']
    header+=['wire '+n+';' for n in sorted(names)];header+=[f'assign {sig(n)}={v};' for n,v in ins.items()]
    lines+=[f'assign {v}={sig(n)};' for n,v in outs.items()];lines+=['endmodule'];destination.write_text('\n'.join(header+lines)+'\n')
    return {'date':'2026-11-25','components':len(seen),'ics':sum(p['part'] not in ('C','R') for p in expected.values()),'pins':sum(len(p['nets']) for p in expected.values()),'no_connects':sum(n is None for p in expected.values() for n in p['nets'].values()),'max_signal_input_loads':max(len(v) for n,v in loads.items() if n not in ('+5V','GND')),'failures':[],'scope':'Pin graph and digital fanout; electrical load/PCB/analog/PVT closure pending'}


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True);defs=definitions();parts=design(defs);rows=emit(defs,parts)
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n');(OUT/'design.json').write_text(json.dumps({'iteration':'NET-13','parts':parts},indent=2)+'\n')
    cmd=[KICAD,'sch','export','netlist','--format','kicadxml','-o',str(VERIFY/'memory_bus.xml'),str(OUT/'memory_bus.kicad_sch')];r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    report=convert();report.update(command=cmd,kicad=subprocess.check_output([KICAD,'version'],text=True).strip())
    actual={}
    for n in ET.parse(VERIFY/'memory_bus.xml').getroot().findall('./nets/net'):
        for p in n.findall('node'):actual[p.get('ref'),p.get('pin')]=n.get('name').removeprefix('/')
    for row in rows:
        found=actual.get((row['reference'],row['pin']))
        if row['net']!='NC' and found!=row['net']:report['failures'].append(row)
        if row['net']=='NC' and found and not found.startswith('unconnected-'):report['failures'].append(row)
    (VERIFY/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return int(bool(report['failures']) or report['max_signal_input_loads']>4)


if __name__=='__main__':raise SystemExit(main())
