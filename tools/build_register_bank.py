"""NET-06: A/B/EA/flags and internal data selector."""
import csv
import json
from pathlib import Path
import re
import subprocess
import uuid
import xml.etree.ElementTree as ET
from build_stack_bank import symbol as previous_symbol
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"hardware/register_bank"
VERIFY=ROOT/"verification/net06"


def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,"isa1/net06/"+s))


def definitions():
    from build_microcode_bank import definitions as md
    from build_stack_bank import definitions as sd
    base=md();base.update(sd())
    return {k:base[k] for k in ('SN74HC273','SN74HC74','SN74HC157','SN74HC08','SN74HC32','SN74HC04','SN74HC125','C')}


def design(defs):
    parts=[];gates=[];cache={}
    def part(kind,fs):
        ref='U'+str(len(parts)+1)
        pins={p:fs.get(v['name']) for p,v in defs[kind]['pins'].items()}
        for p,v in defs[kind]['pins'].items():
            if v['name'] in ('VCC','GND'):pins[p]='+5V' if v['name']=='VCC' else 'GND'
        parts.append({'reference':ref,'part':kind,'nets':pins});return parts[-1]
    def gate(kind,*ins,name=None):
        if kind!='SN74HC04':ins=tuple(sorted(ins))
        key=(kind,ins)
        if key in cache and name is None:return cache[key]
        out=name or f'G_{len(gates)}';gates.append({'part':kind,'inputs':ins,'output':out});cache[key]=out;return out
    def AND(a,b,name=None):return gate('SN74HC08',a,b,name=name)
    def OR(a,b,name=None):return gate('SN74HC32',a,b,name=name)
    def NOT(a,name=None):return gate('SN74HC04',a,name=name)
    def XOR(a,b,name=None):return gate('SN74HC86',a,b,name=name)
    def tree(kind,items,name=None):
        if len(items)==1:return items[0]
        while len(items)>2:items=[gate(kind,*items[i:i+2]) if i+1<len(items) else items[i] for i in range(0,len(items),2)]
        return gate(kind,*items,name=name)
    for bank,prefix in enumerate(['A','B','EA_LO','EA_HI']):
        part('SN74HC273',{'CLR_N':'CLEAR_N','CLK':'CLK_REG',**{f'D{i}':f'{prefix}_D{i}' for i in range(8)},**{f'Q{i}':f'{prefix}_{i}' for i in range(8)}})
    part('SN74HC74',{'CLR0_N':'CLEAR_N','CLR1_N':'CLEAR_N','PRE0_N':'+5V','PRE1_N':'+5V','CLK0':'CLK_FLAGS','CLK1':'CLK_FLAGS','D0':'Z_D','D1':'C_D','Q0':'Z','Q1':'C'})
    def mux(a,b,sel,prefix):
        out=[f'{prefix}_{i}' for i in range(8)]
        for nibble in range(2):
            k=nibble*4
            part('SN74HC157',{'SELECT':sel,'G_N':'GND',**{f'A{i}':a[k+i] for i in range(4)},**{f'B{i}':b[k+i] for i in range(4)},**{f'Y{i}':out[k+i] for i in range(4)}})
        return out
    def bus(prefix):return [f'{prefix}_{i}' for i in range(8)]
    zero=['GND']*8
    p0=mux(zero,bus('A'),'SRC_0','PAIR0')
    p1=mux(bus('PC_HI'),bus('PC_LO'),'SRC_0','PAIR1')
    p2=mux(bus('MDR'),bus('ALU'),'SRC_0','PAIR2')
    q0=mux(p0,p1,'SRC_1','QUAD0');q1=mux(p2,zero,'SRC_1','QUAD1')
    value=mux(q0,q1,'SRC_2','VALUE')
    safe=AND('RESET_N','POWER_GOOD','SAFE')
    enabled=AND(safe,'EXEC_ENABLE','ACCEPT')
    for n,prefix in enumerate(['A','B','EA_LO','EA_HI'],1):
        enable=AND(enabled,NOT(f'DST_N_{n}'))
        mux(bus(prefix),value,enable,prefix+'_DUMMY')
        # Rename feedback outputs to actual D pins; no aliases in generated HDL.
        for p in parts[-2:]:
            for pin,net in p['nets'].items():
                if net and net.startswith(prefix+'_DUMMY_'):p['nets'][pin]=prefix+'_D'+net.rsplit('_',1)[1]
    value_zero=NOT(tree('SN74HC32',value),'VALUE_ZERO')
    z_enable=AND(enabled,'FLAGS_N_0')
    c_enable=AND(enabled,NOT('FLAGS_N_2'))
    OR(AND(NOT(z_enable),'Z'),AND(z_enable,value_zero),'Z_D')
    OR(AND(NOT(c_enable),'C'),AND(c_enable,'ALU_CARRY'),'C_D')
    # Buffered branches are positive, common-clock; no clock gating.
    part('SN74HC125',{'A0':'CLK','A1':'CLK','A2':safe,'A3':'GND',**{f'OE{i}_N':'GND' for i in range(4)},'Y0':'CLK_REG','Y1':'CLK_FLAGS','Y2':'CLEAR_N'})
    for kind in ('SN74HC08','SN74HC32','SN74HC04'):
        group=[g for g in gates if g['part']==kind];cap=6 if kind=='SN74HC04' else 4
        for start in range(0,len(group),cap):
            fs={}
            for i in range(cap):
                g=group[start+i] if start+i<len(group) else None;fs[f'A{i}']=g['inputs'][0] if g else 'GND'
                if cap==4:fs[f'B{i}']=g['inputs'][1] if g else 'GND'
                fs[f'Y{i}']=g['output'] if g else None
            part(kind,fs)
    # Split digital input fanout in groups <=4, recursively including buffers.
    buffers=[]
    while True:
        loads={}
        for p in parts:
            for pin,net in p['nets'].items():
                if defs[p['part']]['pins'][pin]['type']=='input' and net not in ('GND','+5V'):loads.setdefault(net,[]).append((p,pin))
        overloaded=next(((n,v) for n,v in loads.items() if len(v)>4),None)
        if overloaded is None:break
        n,targets=overloaded
        for offset in range(0,len(targets),4):
            if not buffers or buffers[-1]['used']==4:
                p=part('SN74HC125',{**{f'A{i}':'GND' for i in range(4)},**{f'OE{i}_N':'GND' for i in range(4)}});buffers.append({'part':p,'used':0})
            group=buffers[-1];channel=group['used'];group['used']+=1
            out=f'BUF_{len(buffers)}_{channel}';pins=group['part']['nets']
            for pin,spec in defs['SN74HC125']['pins'].items():
                if spec['name']==f'A{channel}':pins[pin]=n
                if spec['name']==f'Y{channel}':pins[pin]=out
            for p,pin in targets[offset:offset+4]:p['nets'][pin]=out
    for i,p in enumerate(parts):p.update(x=60+110*(i%7),y=65+78*(i//7))
    chips=list(parts)
    if len(chips)>49:raise ValueError('A1 layout capacity exceeded')
    for i,p in enumerate(chips,1):
        cap={'reference':f'C{i}','part':'C','nets':{'1':'+5V','2':'GND'},'x':p['x']+31,'y':p['y']-25};parts.append(cap)
    return parts,gates


def package_symbol(kind,spec):
    text,locations=previous_symbol(kind,spec)
    return text.replace('NET02:','NET06:'),locations


def emit_schematic(defs,parts):
    prepared={k:package_symbol(k,v) for k,v in defs.items()};sheet=uid('sheet')
    lines=[f'(kicad_sch (version 20230121) (generator eeschema) (uuid {sheet}) (paper "A1")',
      '(title_block (title "ISA-1 A / B / EA / flags / data mux") (rev "NET-06") (date "2026-11-25") (comment 1 "PARTIAL REGISTER DATAPATH - NOT FOR PRODUCTION"))',
      '(lib_symbols '+" ".join(v[0] for v in prepared.values())+')'];rows=[]
    for p in parts:
        ref,kind,x,y=p['reference'],p['part'],p['x'],p['y'];value='100nF' if kind=='C' else kind
        ax,ay=(x+5,y-2) if kind=='C' else (x,y-(33 if kind=='AT28HC64B' else 25.4))
        props=f'(property "Reference" "{ref}" (at {ax} {ay} 0) (effects (font (size 1 1)))) (property "Value" "{value}" (at {ax} {ay+2.54} 0) (effects (font (size 1 1)))) '
        pp=' '.join(f'(pin "{pin}" (uuid {uid(ref+"/"+pin)}))' for pin in p['nets'])
        lines.append(f'(symbol (lib_id "NET06:{kind}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (uuid {uid(ref)}) {props}{pp} (instances (project "register_bank" (path "/{sheet}" (reference "{ref}") (unit 1)))))')
        for pin,net in p['nets'].items():
            px,py,angle=prepared[kind][1][pin];px+=x;py=y-py
            rows.append({'reference':ref,'part':kind,'pin':pin,'function':defs[kind]['pins'][pin]['name'],'net':net or 'NC'})
            if net is None:lines.append(f'(no_connect (at {px} {py}) (uuid {uid(ref+"/nc/"+pin)}))')
            else:lines.append(f'(label "{net}" (at {px} {py} 0) (effects (font (size 0.9 0.9)) (justify {"right bottom" if angle==0 else "left bottom"})) (uuid {uid(ref+"/label/"+pin)}))')
    for y,t in [(15,'A/B/EA: HC273 + feedback HC157. Z/C: HC74. Positive common clock; enables only on accepted execution.'),(571,'Data selector: zero, A, PC high/low, MDR, ALU, zero, zero. PC/address selection/global timing/PCB remain pending.')]:
        lines.append(f'(text "{t}" (at 18 {y} 0) (effects (font (size 1.5 1.5)) (justify left)) (uuid {uid(t)}))')
    lines+=['(sheet_instances (path "/" (page "1")))',')'];(OUT/'register_bank.kicad_sch').write_text('\n'.join(lines)+'\n')
    with (OUT/'pinmap.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    return rows


def convert(xml_path,defs,destination):
    root=ET.parse(xml_path).getroot();nets=set();actual={}
    for net in root.findall('./nets/net'):
        n=net.get('name').removeprefix('/');nets.add(n)
        for node in net.findall('node'):
            key=(node.get('ref'),node.get('pin'))
            if key in actual:raise ValueError('Multiple nets for pin')
            actual[key]=n
    def sig(n):return "1'b1" if n=='+5V' else "1'b0" if n=='GND' else 'n_'+re.sub(r'[^A-Za-z0-9_]','_',n)
    names=[sig(n) for n in nets if n not in ('+5V','GND')]
    if len(names)!=len(set(names)):raise ValueError('Net name collision')
    lines=['`timescale 1ns/1ps','// GENERATED from KiCad XML pin graph; partial register datapath.',
      'module register_bank_netlist #(parameter integer TIMED=0)(input wire clk,reset_n,power_good,exec_enable,input wire [2:0] src,input wire [7:0] dst_n,input wire [3:0] flags_n,input wire [15:0] pc,input wire [7:0] mdr,alu_result,input wire alu_carry,output wire [7:0] a,b,value,output wire [15:0] ea,output wire z,c);',
      'localparam GATE_T=TIMED?31:0,INV_T=TIMED?24:0,BUF_T=TIMED?36:0,MUX_T=TIMED?38:0,CQ_T=TIMED?40:0;']
    lines+=['wire '+n+';' for n in sorted(names)]
    ports={'CLK':'clk','RESET_N':'reset_n','POWER_GOOD':'power_good','EXEC_ENABLE':'exec_enable','ALU_CARRY':'alu_carry',**{f'SRC_{i}':f'src[{i}]' for i in range(3)},**{f'DST_N_{i}':f'dst_n[{i}]' for i in range(8)},**{f'FLAGS_N_{i}':f'flags_n[{i}]' for i in range(4)},**{f'PC_LO_{i}':f'pc[{i}]' for i in range(8)},**{f'PC_HI_{i}':f'pc[{8+i}]' for i in range(8)},**{f'MDR_{i}':f'mdr[{i}]' for i in range(8)},**{f'ALU_{i}':f'alu_result[{i}]' for i in range(8)}}
    drivers={n:['external'] for n in [*ports,'+5V','GND']};inputs=[];loads={}
    for n,v in ports.items():
        if n in nets:lines.append(f'assign {sig(n)}={v};')
    for c in root.findall('./components/comp'):
        ref=c.get('ref');kind='C' if ref.startswith('C') else c.findtext('value');fs={}
        if kind not in defs:raise ValueError('Unknown IC '+kind)
        for pin,spec in defs[kind]['pins'].items():
            n=actual.get((ref,pin));typ=spec['type']
            if typ in ('input','power_in') and (not n or n.startswith('unconnected-')):raise ValueError(f'Floating input {ref}/{pin}')
            if spec['name'] in ('VCC','GND') and n!={'VCC':'+5V','GND':'GND'}[spec['name']]:raise ValueError('Wrong power '+ref)
            if n:fs[spec['name']]=sig(n)
            if typ=='input':inputs.append((ref,pin,n));loads.setdefault(n,[]).append(ref+'/'+pin)
            if typ in ('output','bidirectional') and n:drivers.setdefault(n,[]).append(ref+'/'+pin)
        def vec(prefix,count):return '{'+','.join(fs[f'{prefix}{i}'] for i in reversed(range(count)))+'}'
        if kind=='SN74HC273':lines.append(f"hc273_functional #(.T_CQ(CQ_T),.T_CLR(CQ_T),.CHECKS(TIMED)) {ref}({fs['CLK']},{fs['CLR_N']},{vec('D',8)},{vec('Q',8)});")
        elif kind=='SN74HC74':
            for i in range(2):
                lines.append(f"hc74_model #(.TIMED(TIMED)) {ref}_{i}({fs[f'CLK{i}']},{fs[f'CLR{i}_N']},{fs[f'PRE{i}_N']},{fs[f'D{i}']},{fs.get(f'Q{i}','')},{fs.get(f'QN{i}','')});")
                if fs[f'PRE{i}_N']!="1'b1":raise ValueError('Flag preset must be inactive')
                lines.append(f"if(TIMED) dff_timing #(.WIDTH(1),.RECOVERY(6),.CLEAR_PULSE(25)) {ref}_check_{i}({fs[f'CLK{i}']},{fs[f'CLR{i}_N']},{fs[f'D{i}']});")
        elif kind=='SN74HC157':lines.append(f"sn74hc157_model #(.T_PD(MUX_T)) {ref}({vec('A',4)},{vec('B',4)},{fs['SELECT']},{fs['G_N']},{vec('Y',4)});")
        elif kind in ('SN74HC08','SN74HC32','SN74HC86'):
            op={'SN74HC08':'&','SN74HC32':'|','SN74HC86':'^'}[kind]
            for i in range(4):
                if f'Y{i}' in fs:lines.append(f"assign #GATE_T {fs[f'Y{i}']}={fs[f'A{i}']} {op} {fs[f'B{i}']};")
        elif kind=='SN74HC04':
            for i in range(6):
                if f'Y{i}' in fs:lines.append(f"assign #INV_T {fs[f'Y{i}']}=~{fs[f'A{i}']};")
        elif kind=='SN74HC125':
            for i in range(4):
                if f'Y{i}' in fs:lines.append(f"assign #BUF_T {fs[f'Y{i}']}=({fs[f'OE{i}_N']}) ? 1'bz : {fs[f'A{i}']};")
    for ref,pin,n in inputs:
        if len(drivers.get(n,[]))!=1:raise ValueError(f'Driver count {ref}/{pin} {n}')
    for n,v in drivers.items():
        if len(v)!=1:raise ValueError('Multiple drivers '+n)
    outputs={'Z':'z','C':'c',**{f'A_{i}':f'a[{i}]' for i in range(8)},**{f'B_{i}':f'b[{i}]' for i in range(8)},**{f'VALUE_{i}':f'value[{i}]' for i in range(8)},**{f'EA_LO_{i}':f'ea[{i}]' for i in range(8)},**{f'EA_HI_{i}':f'ea[{8+i}]' for i in range(8)}}
    for n in outputs:
        if len(drivers.get(n,[]))!=1:raise ValueError('Missing output driver '+n)
    for n,v in outputs.items():lines.append(f'assign {v}={sig(n)};')
    lines.append('endmodule');destination.write_text('\n'.join(lines)+'\n');return actual,loads


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=definitions();parts,gates=design(defs);rows=emit_schematic(defs,parts)
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n');(OUT/'design.json').write_text(json.dumps({'iteration':'NET-06','parts':parts,'gates':gates},indent=2)+'\n')
    cmd=['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(VERIFY/'register_bank.xml'),str(OUT/'register_bank.kicad_sch')]
    result=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    actual,loads=convert(VERIFY/'register_bank.xml',defs,OUT/'register_bank_netlist.sv');failures=[]
    for r in rows:
        found=actual.get((r['reference'],r['pin']))
        if r['net']=='NC':
            if found and not found.startswith('unconnected-'):failures.append(r)
        elif found!=r['net']:failures.append({'expected':r,'actual':found})
    fanout=[{'net':n,'loads':len(v),'pins':v,'input_cap_budget_pf':10*len(v)} for n,v in loads.items() if n not in ('+5V','GND')]
    failures += [r for r in fanout if r['loads']>4]
    (VERIFY/'fanout.json').write_text(json.dumps({'assumption':'10 pF/input + 10 pF routing reserve; internal loads only','nets':sorted(fanout,key=lambda r:(-r['loads'],r['net']))},indent=2)+'\n')
    subprocess.run(['kicad-cli','sch','export','pdf','-o',str(VERIFY/'register_bank.pdf'),str(OUT/'register_bank.kicad_sch')],check=True,capture_output=True,text=True)
    report={'date':'2026-11-25','kicad':subprocess.check_output(['kicad-cli','version'],text=True).strip(),'command':cmd,'components':len(parts),'pins':len(rows),
      'no_connects':sum(r['net']=='NC' for r in rows),'max_signal_input_loads':max(r['loads'] for r in fanout),'stdout':result.stdout,'stderr':result.stderr,'failures':failures,'scope':'Pin graph and digital input load budget. Not ERC/DRC or complete-board timing.'}
    (VERIFY/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True);return int(bool(failures))


if __name__=='__main__':raise SystemExit(main())
