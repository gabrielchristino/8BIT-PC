"""NET-15 candidate MMIO registers and intact four-membrane scan interface.

Native package pins -> KiCad XML -> functional/delay graph. Electrical keypad
parameters, firmware settling/debounce and input metastability remain gates.
"""
import copy
import csv
import inspect
import json
from pathlib import Path
import re
import subprocess
import uuid
import xml.etree.ElementTree as ET
from build_cpu_global import KICAD
from build_memory_decode import sig
from build_stack_bank import symbol as old_symbol
import build_memory_bus as emitter_source
import build_video_raster as video_source

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/mmio_keyboard';VERIFY=ROOT/'verification/net15'


def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net15/'+s))


def definitions():
    from build_memory_access import definitions as access_defs
    from build_microcode_bank import definitions as micro_defs
    defs={k:copy.deepcopy(v) for k,v in emitter_source.definitions().items() if k in ('SN74AHC08','SN74AHC32','SN74AHC04','SN74AHC125','SN74AHCT157','C','R')}
    defs['SN74HC174']=copy.deepcopy(access_defs()['SN74HC174'])
    defs['SN74HC139']=copy.deepcopy(micro_defs()['SN74HC139'])
    defs['SN74AHC574']=copy.deepcopy(video_source.definitions()['SN74AHC574'])
    defs['SN74LV161A']=copy.deepcopy(video_source.definitions()['SN74LV161A'])
    defs['SN74AHC14']=copy.deepcopy(defs['SN74AHC04']);defs['SN74AHC14']['datasheet']='https://www.ti.com/lit/ds/symlink/sn74ahc14.pdf'
    defs['R']['source']='Proposed weak pull-ups, columns 150k and rows 100k, +/-5%; row drivers inactive Hi-Z. Conditional contact/leakage/capacitance qualification only.'
    defs['J8']={'datasheet':'','pins':{str(i+1):{'name':f'PIN{i+1}','type':'passive'} for i in range(8)},'source':'User reference: pins 1..4 rows L1..L4, 5..8 local columns C1..C4, connector front view in KEYPAD_CONNECTOR; not measured'}
    return defs


def ports():
    ins={'CLK':'clk','BANK_RESET_N':'bank_reset_n','ACCESS_SAFE':'access_safe','IO_COMMIT':'io_commit'}
    ins.update({f'IO_SEL_{i}':f'io_select[{i}]' for i in range(6)})
    ins.update({f'WDATA_{i}':f'write_data[{i}]' for i in range(8)})
    outs={'BOOT':'boot','EB':'eb','VB_0':'vb[0]','VB_1':'vb[1]','ROW_0':'row[0]','ROW_1':'row[1]','KEY_READY':'key_ready'}
    outs.update({f'IO_DATA_{i}':f'read_data[{i}]' for i in range(8)})
    return ins,outs


def design(defs):
    parts=[];gates=[];cache={};muxes=[]
    def part(kind,fs,ref=None):
        ref=ref or f'U{sum(p["part"] not in ("R","C","J8") for p in parts)+1}'
        pins={pin:fs.get(s['name']) for pin,s in defs[kind]['pins'].items()}
        for pin,s in defs[kind]['pins'].items():
            if s['name'] in ('VCC','GND'):pins[pin]='+5V' if s['name']=='VCC' else 'GND'
        p={'reference':ref,'part':kind,'nets':pins};parts.append(p);return p
    def gate(kind,*args,name=None):
        if kind in ('SN74AHC08','SN74AHC32'):args=tuple(sorted(args))
        key=kind,args
        if key in cache:return cache[key]
        out=name or f'G_{len(gates)}';cache[key]=out;gates.append((kind,args,out));return out
    def AND(a,b,name=None):return gate('SN74AHC08',a,b,name=name)
    def OR(a,b,name=None):return gate('SN74AHC32',a,b,name=name)
    def NOT(a,name=None):return gate('SN74AHC04',a,name=name)
    def mux(a,b,select,out):muxes.append((a,b,select,out))
    active_write=AND('ACCESS_SAFE','IO_COMMIT')
    enables=[AND(active_write,f'IO_SEL_{i}') for i in range(4)]
    regs=['VB_0','VB_1','EB','ROW_0','ROW_1','BOOT_OFF']
    for i,(out,bit,enable) in enumerate([('VB_0',0,enables[0]),('VB_1',1,enables[0]),('EB',0,enables[1]),('ROW_0',0,enables[3]),('ROW_1',1,enables[3])]):
        mux(out,f'WDATA_{bit}',enable,f'NEXT_{i}')
    OR('BOOT_OFF',AND(enables[2],'WDATA_0'),'NEXT_5');NOT('BOOT_OFF','BOOT')
    part('SN74HC174',{'CLK':'CLK','CLR_N':'BANK_RESET_N',**{f'D{i}':f'NEXT_{i}' for i in range(6)},**{f'Q{i}':regs[i] for i in range(6)}})
    # Inactive rows are high impedance, active row drives only low. No diode
    # or disassembly is assumed inside any membrane.
    part('SN74HC139',{'G0_N':NOT('ACCESS_SAFE'),'A0':'ROW_0','B0':'ROW_1','G1_N':'+5V','A1':'GND','B1':'GND',
      **{f'Y0_{i}':f'ROW_OE_{i}_N' for i in range(4)},**{f'Y1_{i}':None for i in range(4)}})
    part('SN74AHC125',{**{f'A{i}':'GND' for i in range(4)},**{f'OE{i}_N':f'ROW_OE_{i}_N' for i in range(4)},**{f'Y{i}':f'ROW_WIRE_{i}' for i in range(4)}})
    # Schmitt inputs tolerate slow RC column edges. Polarity is inverted here
    # and restored after the return mux, preserving active-low column ABI.
    for group in range(3):
        fs={}
        for i in range(6):
            bit=group*6+i;fs[f'A{i}']=f'COL_WIRE_{bit}' if bit<16 else 'GND';fs[f'Y{i}']=f'KEY_INV_{bit}' if bit<16 else None
        part('SN74AHC14',fs)
    # Two stages per column. These are digital package models, not a proof of
    # analog metastability resolution; first-stage apertures need CDC analysis.
    for stage in range(2):
        for bank in range(2):
            fs={'CLK':'CLK','OE_N':'GND'}
            for i in range(8):
                bit=bank*8+i;fs[f'D{i}']=f'KEY_INV_{bit}' if stage==0 else f'KEY_SYNC1_{bit}';fs[f'Q{i}']=f'KEY_SYNC{stage+1}_{bit}'
            part('SN74AHC574',fs)
    # Saturate at 8192 backend clocks after bank reset or each ROW write. At
    # the selected 25.175MHz/4 backend this is about 1.302ms. A separate access
    # controller must wait for KEY_READY before acknowledging column reads.
    timer_clear=AND('BANK_RESET_N',NOT(enables[3]));timer_enable=NOT('KEY_READY')
    for nib in range(4):
        fs={'CLK':'CLK','CLR_N':timer_clear,'LOAD_N':'+5V','ENP':timer_enable,'ENT':'+5V' if nib==0 else f'QUIET_CARRY_{nib-1}',
            'RCO':f'QUIET_CARRY_{nib}' if nib<3 else None}
        for bit in range(4):fs[f'D{bit}']='GND';fs[f'Q{bit}']='KEY_READY' if nib*4+bit==13 else None
        part('SN74LV161A',fs)
    # 8:1 complemented return tree: default, VB, EB, BOOT_OFF, low/high columns,
    # default/default. ROW reads and unimplemented IO return FF as before.
    s0=OR(OR('IO_SEL_0','IO_SEL_2'),'IO_SEL_5');s1=OR('IO_SEL_1','IO_SEL_2');s2=OR('IO_SEL_4','IO_SEL_5')
    leaves=[['GND']*8,[NOT('VB_0'),NOT('VB_1')]+['+5V']*6,[NOT('EB')]+['+5V']*7,['BOOT']+['+5V']*7,
      [f'KEY_SYNC2_{i}' for i in range(8)],[f'KEY_SYNC2_{i+8}' for i in range(8)],['GND']*8,['GND']*8]
    for level,select in enumerate((s0,s1,s2)):
        next_leaves=[]
        for pair in range(len(leaves)//2):
            outputs=[f'RETURN_{level}_{pair}_{i}' for i in range(8)]
            for i in range(8):mux(leaves[pair*2][i],leaves[pair*2+1][i],select,outputs[i])
            next_leaves.append(outputs)
        leaves=next_leaves
    for i in range(8):NOT(leaves[0][i],f'IO_DATA_{i}')
    # Pack muxes by select, ensuring physical channel ties are explicit.
    for select in dict.fromkeys(x[2] for x in muxes):
        rows=[m for m in muxes if m[2]==select]
        for first in range(0,len(rows),4):
            fs={'SELECT':select,'G_N':'GND'}
            for i in range(4):
                m=rows[first+i] if first+i<len(rows) else None
                fs[f'A{i}']=m[0] if m else 'GND';fs[f'B{i}']=m[1] if m else 'GND';fs[f'Y{i}']=m[3] if m else None
            part('SN74AHCT157',fs)
    for kind in ('SN74AHC08','SN74AHC32','SN74AHC04'):
        rows=[g for g in gates if g[0]==kind];cap=6 if kind=='SN74AHC04' else 4
        for first in range(0,len(rows),cap):
            fs={}
            for i in range(cap):
                g=rows[first+i] if first+i<len(rows) else None;fs[f'A{i}']=g[1][0] if g else 'GND'
                if cap==4:fs[f'B{i}']=g[1][1] if g else 'GND'
                fs[f'Y{i}']=g[2] if g else None
            part(kind,fs)
    buffers=[]
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
            for pin,s in defs[p['part']]['pins'].items():
                if s['name']==f'A{i}':p['nets'][pin]=n
                if s['name']==f'Y{i}':p['nets'][pin]=out
            for target,pin in targets[first:first+4]:target['nets'][pin]=out
    chips=list(parts)
    for i,p in enumerate(chips):
        p.update(x=round((60+98*(i%10))/1.27)*1.27,y=round((70+85*(i//10))/1.27)*1.27)
        parts.append({'reference':f'C{i+1}','part':'C','nets':{'1':'+5V','2':'GND'},'x':p['x']+31.75,'y':p['y']-27.94})
    for i in range(16):
        part('R',{'1':'+5V','2':f'COL_WIRE_{i}'},f'R{i+1}').update(value='150k',x=round((40+45*i)/1.27)*1.27,y=450.85)
    # Weak row bias supplies inactive-output leakage locally, rather than
    # allowing several Hi-Z-driver leakage paths to discharge one column.
    # Every inactive output driver remains Hi-Z; no push-pull high is driven.
    for i in range(4):
        part('R',{'1':'+5V','2':f'ROW_WIRE_{i}'},f'R{i+17}').update(value='100k',x=round((790+45*i)/1.27)*1.27,y=450.85)
    for bank in range(4):
        fs={f'PIN{i+1}':f'ROW_WIRE_{i}' for i in range(4)};fs.update({f'PIN{i+5}':f'COL_WIRE_{bank*4+i}' for i in range(4)})
        part('J8',fs,f'J{bank+1}').update(x=round((90+190*bank)/1.27)*1.27,y=520.7)
    return parts


def package_symbol(kind,spec):
    if kind=='J8':
        locations={str(i+1):(-10.16,8.89-i*2.54,0) for i in range(8)}
        text='(symbol "NET15:J8" (pin_names (offset 0.508)) (in_bom yes) (on_board yes) (property "Reference" "J" (at 0 15 0) (effects (font (size 1 1)))) (property "Value" "J8" (at 0 13 0) (effects (font (size 1 1)))) (symbol "J8_0_1" (rectangle (start -5.08 11.43) (end 5.08 -11.43) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol "J8_1_1" '
        for pin,(x,y,a) in locations.items():
            name=spec['pins'][pin]['name'];text+=f'(pin passive line (at {x} {y} {a}) (length 5.08) (name "{name}" (effects (font (size 1 1)))) (number "{pin}" (effects (font (size 1 1)))))'
        return text+'))',locations
    if kind=='R':return tuple(x.replace('NET13:','NET15:') if isinstance(x,str) else x for x in emitter_source.package_symbol(kind,spec))
    return tuple(x.replace('NET02:','NET15:') if isinstance(x,str) else x for x in old_symbol(kind,spec))


_emitter=inspect.getsource(emitter_source.emit).replace('memory_bus','mmio_keyboard').replace('NET13','NET15').replace('NET-13','NET-15').replace('paper "A1"','paper "A0"').replace('ISA-1 SRAM / EEPROM data front-end','ISA-1 MMIO / four intact membrane connectors').replace("'3.3k' if kind=='R'","p['value'] if kind=='R'")
exec(_emitter,globals())


def convert(source_path=None,destination=None):
    source_path=source_path or VERIFY/'mmio_keyboard.xml';destination=destination or OUT/'mmio_keyboard_netlist.sv'
    defs=json.loads((OUT/'package-functions.json').read_text());parts=json.loads((OUT/'design.json').read_text())['parts'];expected={p['reference']:p for p in parts}
    root=ET.parse(source_path).getroot();actual={};nets=set()
    for net in root.findall('./nets/net'):
        n=net.get('name').removeprefix('/');nets.add(n)
        for node in net.findall('node'):
            key=node.get('ref'),node.get('pin')
            if key in actual:raise ValueError('Multiple nets '+str(key))
            actual[key]=n
    ins,outs=ports();drivers={n:['external'] for n in [*ins,'+5V','GND']};loads={};lines=[];seen=set()
    for comp in root.findall('./components/comp'):
        ref=comp.get('ref');p=expected[ref];kind=p['part'];seen.add(ref);fs={}
        value='100nF' if kind=='C' else p['value'] if kind=='R' else kind
        if comp.findtext('value')!=value:raise ValueError('Value changed '+ref)
        for pin,s in defs[kind]['pins'].items():
            n=actual.get((ref,pin));name=s['name'];typ=s['type']
            if typ in ('input','power_in','passive') and kind!='C' and (not n or n.startswith('unconnected-')):raise ValueError('Floating input '+ref+'/'+pin)
            if name in ('VCC','GND') and n!={'VCC':'+5V','GND':'GND'}[name]:raise ValueError('Wrong power '+ref)
            if n and not n.startswith('unconnected-'):fs[name]=sig(n)
            if typ=='input':loads.setdefault(n,[]).append(ref+'/'+pin)
            if typ=='output' and name in fs:drivers.setdefault(n,[]).append(ref+'/'+pin)
        def vec(prefix,w):return '{'+','.join(fs.get(f'{prefix}{i}',f'{ref}_unused_{prefix}{i}') for i in reversed(range(w)))+'}'
        if kind in ('C','J8'):continue
        if kind=='R':
            if fs['1']!="1'b1" or not re.fullmatch(r'n_(COL|ROW)_WIRE_\d+',fs['2']):raise ValueError('Pull-up wiring '+ref)
            drivers.setdefault(actual[ref,'2'],[]).append('weak pull-up');lines.append(f"pullup({fs['2']});");continue
        if kind=='SN74HC174':lines.append(f"hc174_model #(.TIMED(TIMED)) {ref}({fs['CLK']},{fs['CLR_N']},{vec('D',6)},{vec('Q',6)});")
        elif kind=='SN74LV161A':lines.append(f"net14b_lv161 #(.TIMED(TIMED)) {ref}({fs['CLK']},{fs['CLR_N']},{fs['LOAD_N']},{fs['ENP']},{fs['ENT']},{vec('D',4)},{vec('Q',4)},{fs.get('RCO',ref+'_unused_RCO')},checks);")
        elif kind=='SN74HC139':
            for i in range(2):lines.append(f"hc139_model #(.T_PD(TIMED?44:0)) {ref}_{i}({{{fs[f'B{i}']},{fs[f'A{i}']}}},{fs[f'G{i}_N']},{vec(f'Y{i}_',4)});")
        elif kind=='SN74AHC574':lines.append(f"net14b_ahc574 #(.TIMED(TIMED)) {ref}({fs['CLK']},{fs['OE_N']},{vec('D',8)},{vec('Q',8)},checks);")
        elif kind=='SN74AHCT157':lines.append(f"assign #MUX_T {vec('Y',4)}={fs['G_N']} ? 4'b0 : {fs['SELECT']} ? {vec('B',4)} : {vec('A',4)};")
        elif kind in ('SN74AHC04','SN74AHC14'):
            for i in range(6):
                if f'Y{i}' in fs:lines.append(f"assign #{'SCHMITT_T' if kind=='SN74AHC14' else 'GATE_T'} {fs[f'Y{i}']}=~{fs[f'A{i}']};")
        elif kind in ('SN74AHC08','SN74AHC32'):
            op='&' if kind=='SN74AHC08' else '|'
            for i in range(4):
                if f'Y{i}' in fs:lines.append(f"assign #GATE_T {fs[f'Y{i}']}={fs[f'A{i}']} {op} {fs[f'B{i}']};")
        elif kind=='SN74AHC125':
            for i in range(4):
                if f'Y{i}' not in fs:continue
                if fs[f'Y{i}'].startswith('n_ROW_WIRE_') and fs[f'A{i}']!="1'b0":raise ValueError('Row driver not low-only '+ref)
                lines.append(f"assign #GATE_T {fs[f'Y{i}']}={fs[f'OE{i}_N']} ? 1'bz : {fs[f'A{i}']};")
        else:raise ValueError('No model '+kind)
    if seen!=set(expected):raise ValueError('Inventory mismatch')
    for n in loads:
        if len(drivers.get(n,[]))!=1:raise ValueError('Driver count '+str(n))
    for n in outs:
        if len(drivers.get(n,[]))!=1:raise ValueError('Undriven output '+n)
    for n,v in drivers.items():
        if len(v)!=1 and not (re.fullmatch(r'ROW_WIRE_[0-3]',n) and len(v)==2 and v.count('weak pull-up')==1):raise ValueError('Multiple drivers '+n)
    for p in parts:
        if p['part']=='J8':
            bank=int(p['reference'][1:])-1
            for i in range(8):
                want=f'ROW_WIRE_{i}' if i<4 else f'COL_WIRE_{bank*4+i-4}'
                if actual.get((p['reference'],str(i+1)))!=want:raise ValueError('Membrane connector pin map '+p['reference'])
    header=['`timescale 1ns/1ps','// GENERATED from native pin XML. Schmitt logic only, not analog RC/CDC/debounce approval.',
      'module mmio_keyboard_netlist #(parameter TIMED=0)(input wire clk,bank_reset_n,access_safe,io_commit,input wire [5:0] io_select,input wire [7:0] write_data,inout wire [3:0] row_wires,inout wire [15:0] column_wires,output wire boot,eb,output wire [1:0] vb,row,output wire [7:0] read_data,output wire key_ready);',
      'localparam GATE_T=TIMED?10:0,MUX_T=TIMED?12:0,SCHMITT_T=TIMED?12:0;wire checks=bank_reset_n && access_safe;']
    header+=['wire '+sig(n)+';' for n in sorted(nets|set(ins)) if n not in ('+5V','GND') and not n.startswith('unconnected-')]
    spares=sorted(set(re.findall(r'\bU\d+_unused_\w+','\n'.join(lines))))
    header+=['wire '+n+';' for n in spares]
    header += [f'assign {sig(n)}={v};' for n,v in ins.items()]
    lines += [f'tran({sig(f"ROW_WIRE_{i}")},row_wires[{i}]);' for i in range(4)]
    lines += [f'tran({sig(f"COL_WIRE_{i}")},column_wires[{i}]);' for i in range(16)]
    lines += [f'assign {v}={sig(n)};' for n,v in outs.items()]+['endmodule']
    destination.write_text('\n'.join(header+lines)+'\n')
    failures=[]
    for p in parts:
        for pin,n in p['nets'].items():
            got=actual.get((p['reference'],pin))
            if n is not None and got!=n:failures.append([p['reference'],pin,n,got])
            if n is None and got and not got.startswith('unconnected-'):failures.append([p['reference'],pin,'NC',got])
    return {'components':len(parts),'ics':sum(p['part'] not in ('C','R','J8') for p in parts),'pins':sum(len(p['nets']) for p in parts),'no_connects':sum(n is None for p in parts for n in p['nets'].values()),'max_signal_input_loads':max(len(v) for n,v in loads.items() if n not in ('+5V','GND')),'failures':failures,'scope':'Pin/connector graph and selected digital models; physical matrix R/C/settling/CDC/protection/firmware approval pending'}


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=definitions();parts=design(defs);emit(defs,parts)
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n');(OUT/'design.json').write_text(json.dumps({'iteration':'NET-15','parts':parts},indent=2)+'\n')
    cmd=[KICAD,'sch','export','netlist','--format','kicadxml','-o',str(VERIFY/'mmio_keyboard.xml'),str(OUT/'mmio_keyboard.kicad_sch')]
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    report=convert();report.update(command=cmd,kicad=subprocess.check_output([KICAD,'version'],text=True).strip())
    (VERIFY/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return int(bool(report['failures']) or report['max_signal_input_loads']>4)


if __name__=='__main__':raise SystemExit(main())
