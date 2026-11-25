"""NET-04: explicit microsequencer, read-only control EEPROMs and word register."""
import copy
import csv
import json
from pathlib import Path
import re
import subprocess
import uuid
import xml.etree.ElementTree as ET
from build_transaction_bank import definitions as previous_definitions
from build_stack_bank import symbol as previous_symbol
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"hardware/microcode_bank"
VERIFY=ROOT/"verification/net04"


def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,"isa1/net04/"+s))


def definitions():
    defs=previous_definitions()
    defs={k:defs[k] for k in ("SN74HC74","SN74HC377","SN74HC08","SN74HC32","SN74HC04","SN74HC125","C")}
    defs["SN74HCT377"]=copy.deepcopy(defs["SN74HC377"])
    defs["SN74HCT377"]["datasheet"]="https://www.ti.com/lit/ds/symlink/sn74hct377.pdf"
    def add(kind,ins,outs,vcc,gnd):
        pins={str(p):{"name":n,"type":"input"} for p,n in ins.items()}
        pins.update({str(p):{"name":n,"type":"output"} for p,n in outs.items()})
        pins[str(vcc)]={"name":"VCC","type":"power_in"};pins[str(gnd)]={"name":"GND","type":"power_in"}
        defs[kind]={"datasheet":"https://www.ti.com/lit/ds/symlink/"+kind.lower()+".pdf","pins":pins,"source":"Manufacturer package pinout; zero-based channel indices"}
    add("SN74HC161",{1:"CLR_N",2:"CLK",3:"D0",4:"D1",5:"D2",6:"D3",7:"ENP",9:"LOAD_N",10:"ENT"},
        {14:"Q0",13:"Q1",12:"Q2",11:"Q3",15:"RCO"},16,8)
    add("SN74HC138",{1:"A",2:"B",3:"C",4:"G2A_N",5:"G2B_N",6:"G1"},
        {p:f"Y{i}" for i,p in enumerate([15,14,13,12,11,10,9,7])},16,8)
    add("SN74HC139",{1:"G0_N",2:"A0",3:"B0",15:"G1_N",14:"A1",13:"B1"},
        {**{p:f"Y0_{i}" for i,p in enumerate([4,5,6,7])},**{p:f"Y1_{i}" for i,p in enumerate([12,11,10,9])}},16,8)
    defs["SN74HC86"]=copy.deepcopy(defs["SN74HC08"]);defs["SN74HC86"]["datasheet"]="https://www.ti.com/lit/ds/symlink/sn74hc86.pdf"
    from build_stack_bank import definitions as sd
    defs["SN74HC157"]=sd()["SN74HC157"]
    add("AT28HC64B",{2:"A12",3:"A7",4:"A6",5:"A5",6:"A4",7:"A3",8:"A2",9:"A1",10:"A0",20:"CE_N",21:"A10",22:"OE_N",23:"A11",24:"A9",25:"A8",27:"WE_N"},
        {p:f"IO{i}" for i,p in enumerate([11,12,13,15,16,17,18,19])},28,14)
    mem=defs["AT28HC64B"]
    for p in [11,12,13,15,16,17,18,19]:mem["pins"][str(p)]["type"]="bidirectional"
    for p in [1,26]:mem["pins"][str(p)]={"name":f"NC{p}","type":"passive"}
    mem["datasheet"]="https://ww1.microchip.com/downloads/en/DeviceDoc/doc0274.pdf"
    mem["source"]="Microchip/Atmel 0274L, 28-pin SOIC pinout only; read-only, -120 candidate"
    return defs


def design(defs):
    parts=[];gates=[];cache={}
    def part(ref,kind,fs,**extra):
        pins={p:fs.get(v['name']) for p,v in defs[kind]['pins'].items()}
        for p,v in defs[kind]['pins'].items():
            if v['name'] in ('VCC','GND'):pins[p]='+5V' if v['name']=='VCC' else 'GND'
        result={'reference':ref,'part':kind,'nets':pins,**extra};parts.append(result);return result
    def gate(kind,*inputs,name=None):
        if kind!='SN74HC04':inputs=tuple(sorted(inputs))
        key=(kind,inputs)
        if key in cache:return cache[key]
        net=name or f'G_{len(gates)}';gates.append({'part':kind,'inputs':inputs,'output':net});cache[key]=net;return net
    def AND(a,b,name=None):return gate('SN74HC08',a,b,name=name)
    def OR(a,b,name=None):return gate('SN74HC32',a,b,name=name)
    def NOT(a,name=None):return gate('SN74HC04',a,name=name)
    def XOR(a,b,name=None):return gate('SN74HC86',a,b,name=name)
    safe=AND('RESET_N','POWER_GOOD','SAFE')
    fetch=NOT('EXEC_BANK','FETCH')
    match=NOT(XOR('ADDRESS_TOKEN','WORD_TOKEN'),'WORD_MATCH')
    ready=AND(match,'SAFE_QUAL','CONTROL_READY')
    no_halt=NOT('CW_25')
    actual=AND(AND('ADVANCE_REQ',ready),no_halt,'ACTUAL_ADVANCE')
    step1=AND('STEP_0',NOT(OR('STEP_1',OR('STEP_2','STEP_3'))))
    dispatch=AND(actual,AND(fetch,step1),'DISPATCH')
    boundary=OR(dispatch,AND(actual,'CW_24'))
    load_n=NOT(boundary,'STEP_LOAD_N')
    exec_d=OR(dispatch,AND('EXEC_BANK',load_n))
    addr_d=XOR('ADDRESS_TOKEN',actual)
    ir_n=NOT(dispatch,'IR_EN_N')
    neg=NOT('CLK','NEG_CLK_RAW')
    sp_valid=NOT(AND('SP_N_1','SP_N_2'))
    AND(AND(AND('EXECUTE_PULSE',ready),no_halt),sp_valid,'SP_UPDATE')
    NOT(AND('SP_N_2','ADDR_N_5'),'SP_DOWN')
    part('U1','SN74HC161',{'CLR_N':'CLEAR_SEQ_N','CLK':'CLK_SEQ','LOAD_N':load_n,'ENP':actual,'ENT':'+5V',
       **{f'D{i}':'GND' for i in range(4)},**{f'Q{i}':f'STEP_{i}' for i in range(4)}})
    part('U2','SN74HC74',{'CLK0':'CLK_SEQ','CLK1':'CLK_SEQ','CLR0_N':'CLEAR_SEQ_N','CLR1_N':'CLEAR_SEQ_N',
       'PRE0_N':'+5V','PRE1_N':'+5V','D0':exec_d,'Q0':'EXEC_BANK','D1':addr_d,'Q1':'ADDRESS_TOKEN'})
    part('U3','SN74HC74',{'CLK0':'CLK_WORD1','CLR0_N':'+5V','PRE0_N':'CLEAR_WORD_N','D0':'ADDRESS_TOKEN','Q0':'WORD_TOKEN',
       'CLK1':'GND','CLR1_N':'CLEAR_WORD_N','PRE1_N':'+5V','D1':'GND'})
    part('U4','SN74HC377',{'CLK':'CLK_IR','EN_N':ir_n,**{f'D{i}':f'OPCODE_{i}' for i in range(8)},**{f'Q{i}':f'IR_{i}' for i in range(8)}})
    for bank in range(2):
        part(f'U{bank+5}','SN74HC157',{'SELECT':fetch,'G_N':'GND',**{f'A{i}':f'IR_{bank*4+i}' for i in range(4)},
           **{f'B{i}':'GND' for i in range(4)},**{f'Y{i}':f'ROM_A{4+bank*4+i}' for i in range(4)}})
    for lane in range(4):
        part(f'U{lane+7}','SN74HCT377',{'CLK':'CLK_WORD0' if lane<2 else 'CLK_WORD1','EN_N':'WORD_EN_N',
            **{f'D{i}':f'ROM_D{lane}_{i}' for i in range(8)},**{f'Q{i}':f'CW_{lane*8+i}' for i in range(8)}})
        part(f'U{lane+11}','AT28HC64B',{'CE_N':'GND','OE_N':'GND','WE_N':'+5V',
            **{f'A{i}':f'ROM_A{i}' for i in range(13)},**{f'IO{i}':f'ROM_D{lane}_{i}' for i in range(8)}},lane=lane)
    part('U15','SN74HC125',{'A0':'CLK','A1':'CLK','A2':neg,'A3':neg,
       **{f'OE{i}_N':'GND' for i in range(4)},**{f'Y{i}':n for i,n in enumerate(['CLK_SEQ','CLK_IR','CLK_WORD0','CLK_WORD1'])}})
    part('U16','SN74HC125',{'A0':safe,'A1':safe,'A2':safe,'A3':'GND',**{f'OE{i}_N':'GND' for i in range(4)},
       'Y0':'CLEAR_SEQ_N','Y1':'CLEAR_WORD_N','Y2':'SAFE_QUAL'})
    part('U17','SN74HC125',{**{f'A{i}':f'STEP_{i}' for i in range(4)},**{f'OE{i}_N':'GND' for i in range(4)},**{f'Y{i}':f'ROM_A{i}' for i in range(4)}})
    part('U18','SN74HC125',{'A0':fetch,'A1':match,'A2':'GND','A3':'GND',**{f'OE{i}_N':'GND' for i in range(4)},'Y0':'ROM_A12','Y1':'WORD_EN_N'})
    ref=19
    for prefix,shift in [('ADDR_N',0),('SRC_N',3),('DST_N',6),('PC_N',11),('ALU_N',18),('ALU_N',18)]:
        # The first ALU decoder enables with bit21 low; the second with it high.
        bank=sum(1 for p in parts if p.get('decoder')=='ALU_N') if prefix=='ALU_N' else 0
        fs={'A':f'CW_{shift}','B':f'CW_{shift+1}','C':f'CW_{shift+2}','G1':'CW_21' if bank else '+5V',
            'G2A_N':'CW_21' if prefix=='ALU_N' and bank==0 else 'GND','G2B_N':'GND',
            **{f'Y{i}':f'{prefix}_{bank*8+i}' for i in range(8)}}
        part(f'U{ref}','SN74HC138',fs,decoder=prefix);ref+=1
    for fields in [[('MEM_N',9),('SP_N',14)],[('X_N',16),('FLAGS_N',22)]]:
        fs={}
        for bank,(prefix,shift) in enumerate(fields):fs.update({f'G{bank}_N':'GND',f'A{bank}':f'CW_{shift}',f'B{bank}':f'CW_{shift+1}',
            **{f'Y{bank}_{i}':f'{prefix}_{i}' for i in range(4)}})
        part(f'U{ref}','SN74HC139',fs);ref+=1
    for kind in ('SN74HC08','SN74HC32','SN74HC04','SN74HC86'):
        group=[g for g in gates if g['part']==kind];capacity=6 if kind=='SN74HC04' else 4
        for start in range(0,len(group),capacity):
            fs={}
            for i in range(capacity):
                g=group[start+i] if start+i<len(group) else None;fs[f'A{i}']=g['inputs'][0] if g else 'GND'
                if capacity==4:fs[f'B{i}']=g['inputs'][1] if g else 'GND'
                fs[f'Y{i}']=g['output'] if g else None
            part(f'U{ref}',kind,fs);ref+=1
    for i,p in enumerate(parts):p.update(x=64+110*(i%7),y=65+100*(i//7))
    for i,p in enumerate(list(parts),1):
        c=part(f'C{i}','C',{'1':'+5V','2':'GND'});c.update(x=p['x']+34,y=p['y']-25)
    return parts,gates


def package_symbol(kind,spec):
    if kind!='AT28HC64B':
        text,locations=previous_symbol(kind,spec);return text.replace('NET02:','NET04:'),locations
    # Complete 28-pin SOIC/PDIP package; NCs explicit, IO pins bidirectional.
    locations={};left=[(p,v) for p,v in spec['pins'].items() if v['type']=='input'];right=[(p,v) for p,v in spec['pins'].items() if v['type']=='bidirectional']
    for entries,x,angle in [(left,-17.78,0),(right,17.78,180)]:
        for i,(p,_) in enumerate(entries):locations[p]=(x,(len(entries)-1)*1.27-i*2.54,angle)
    locations.update({'1':(17.78,-16.51,180),'26':(17.78,-19.05,180),'28':(0,27.94,270),'14':(0,-27.94,90)})
    text=f'(symbol "NET04:{kind}" (pin_names (offset 0.508)) (in_bom yes) (on_board yes) '
    text+=f'(property "Reference" "U" (at 0 32 0) (effects (font (size 1 1)))) (property "Value" "{kind}" (at 0 30 0) (effects (font (size 1 1)))) '
    text+=f'(symbol "{kind}_0_1" (rectangle (start -12.7 24.13) (end 12.7 -24.13) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol "{kind}_1_1" '
    for p,v in spec['pins'].items():
        x,y,angle=locations[p];length=3.81 if p in ('14','28') else 5.08
        text+=f'(pin {v["type"]} line (at {x} {y} {angle}) (length {length}) (name "{v["name"]}" (effects (font (size 1 1)))) (number "{p}" (effects (font (size 1 1))))) '
    return text+'))',locations


def emit_schematic(defs,parts):
    prepared={k:package_symbol(k,v) for k,v in defs.items()};sheet=uid('sheet')
    lines=[f'(kicad_sch (version 20230121) (generator eeschema) (uuid {sheet}) (paper "A1")',
      '(title_block (title "ISA-1 microsequencer and registered control ROM") (rev "NET-04") (date "2026-11-25") (comment 1 "PARTIAL - READ ONLY ROMs - NOT FOR PRODUCTION"))',
      '(lib_symbols '+" ".join(v[0] for v in prepared.values())+')'];rows=[]
    for p in parts:
        ref,kind,x,y=p['reference'],p['part'],p['x'],p['y'];value='100nF' if kind=='C' else kind
        ax,ay=(x+5,y-2) if kind=='C' else (x,y-(33 if kind=='AT28HC64B' else 25.4))
        props=f'(property "Reference" "{ref}" (at {ax} {ay} 0) (effects (font (size 1 1)))) (property "Value" "{value}" (at {ax} {ay+2.54} 0) (effects (font (size 1 1)))) '
        pp=' '.join(f'(pin "{pin}" (uuid {uid(ref+"/"+pin)}))' for pin in p['nets'])
        lines.append(f'(symbol (lib_id "NET04:{kind}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (uuid {uid(ref)}) {props}{pp} (instances (project "microcode_bank" (path "/{sheet}" (reference "{ref}") (unit 1)))))')
        for pin,net in p['nets'].items():
            px,py,angle=prepared[kind][1][pin];px+=x;py=y-py
            rows.append({'reference':ref,'part':kind,'pin':pin,'function':defs[kind]['pins'][pin]['name'],'net':net or 'NC'})
            if net is None:lines.append(f'(no_connect (at {px} {py}) (uuid {uid(ref+"/nc/"+pin)}))')
            else:lines.append(f'(label "{net}" (at {px} {py} 0) (effects (font (size 0.9 0.9)) (justify {"right bottom" if angle==0 else "left bottom"})) (uuid {uid(ref+"/label/"+pin)}))')
    for y,t in [(17,'Positive phase: address/IR. Opposite phase: capture only a new ROM word; hold through WAIT.'),(553,'Four original 8 KiB lanes. WE tied high. AT28HC64B-120 -> HCT377 -> HC logic. Clock skew, PCB and global control pending.')]:
        lines.append(f'(text "{t}" (at 18 {y} 0) (effects (font (size 1.5 1.5)) (justify left)) (uuid {uid(t)}))')
    lines+=['(sheet_instances (path "/" (page "1")))',')'];(OUT/'microcode_bank.kicad_sch').write_text('\n'.join(lines)+'\n')
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
    lines=['`timescale 1ns/1ps','// GENERATED from KiCad exported pin XML. No behavioral sequencer.',
      'module microcode_bank_netlist #(parameter integer TIMED=0,parameter ROM_PREFIX="control_lane")(',
      'input wire clk,reset_n,power_good,advance_req,execute_pulse,input wire [7:0] opcode,',
      'output wire control_ready,execute_clk,dispatch,fetch,actual_advance,output wire [3:0] step,output wire [7:0] ir,',
      'output wire [12:0] rom_address,output wire [31:0] control_word,output wire sp_update,sp_down,',
      'output wire [7:0] addr_n,src_n,dst_n,pc_n,output wire [3:0] mem_n,sp_n,x_n,flags_n,output wire [15:0] alu_n);',
      'localparam GATE_T=TIMED?25:0,INV_T=TIMED?24:0,BUF_T=TIMED?36:0,MUX_T=TIMED?38:0,DEC_T=TIMED?45:0;']
    lines+=['wire '+n+';' for n in sorted(names)]
    ports={'CLK':'clk','RESET_N':'reset_n','POWER_GOOD':'power_good','ADVANCE_REQ':'advance_req','EXECUTE_PULSE':'execute_pulse',**{f'OPCODE_{i}':f'opcode[{i}]' for i in range(8)}}
    drivers={n:['external'] for n in [*ports,'+5V','GND']};inputs=[];loads={}
    for n,v in ports.items():lines.append(f'assign {sig(n)}={v};')
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
        if kind=='SN74HC161':lines.append(f"hc161_model #(.TIMED(TIMED)) {ref}({fs['CLK']},{fs['CLR_N']},{fs['LOAD_N']},{fs['ENP']},{fs['ENT']},{vec('D',4)},{vec('Q',4)},{fs.get('RCO','')});")
        elif kind=='SN74HC74':
            for i in range(2):lines.append(f"hc74_model #(.TIMED(TIMED)) {ref}_{i}({fs[f'CLK{i}']},{fs[f'CLR{i}_N']},{fs[f'PRE{i}_N']},{fs[f'D{i}']},{fs.get(f'Q{i}','')},{fs.get(f'QN{i}','')});")
        elif kind in ('SN74HC377','SN74HCT377'):
            t=38 if kind=='SN74HCT377' else 40
            lines.append(f"sn74hc377_model #(.T_CQ(TIMED?{t}:0)) {ref}({fs['CLK']},{fs['EN_N']},{vec('D',8)},{vec('Q',8)});")
            if kind=='SN74HCT377':lines.append(f"if(TIMED) hct377_timing {ref}_check({fs['CLK']},{fs['EN_N']},{vec('D',8)},reset_n && power_good);")
        elif kind=='AT28HC64B':
            if fs['WE_N']!="1'b1" or fs['OE_N']!="1'b0" or fs['CE_N']!="1'b0":raise ValueError('Control EEPROM must be read-only/enabled')
            lane=int(ref[1:])-11
            if lane not in range(4):raise ValueError('Unexpected control ROM lane')
            lines.append(f"at28hc64_read #(.FILE({{ROM_PREFIX,\"{lane}.hex\"}}),.T_ACC(TIMED?120:0)) {ref}({vec('A',13)},{vec('IO',8)});")
        elif kind=='SN74HC157':lines.append(f"sn74hc157_model #(.T_PD(MUX_T)) {ref}({vec('A',4)},{vec('B',4)},{fs['SELECT']},{fs['G_N']},{vec('Y',4)});")
        elif kind=='SN74HC138':lines.append(f"hc138_model #(.T_PD(DEC_T)) {ref}({{{fs['C']},{fs['B']},{fs['A']}}},{fs['G1']},{fs['G2A_N']},{fs['G2B_N']},{vec('Y',8)});")
        elif kind=='SN74HC139':
            for i in range(2):lines.append(f"hc139_model #(.T_PD(DEC_T)) {ref}_{i}({{{fs[f'B{i}']},{fs[f'A{i}']}}},{fs[f'G{i}_N']},{vec(f'Y{i}_',4)});")
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
    outputs={'CONTROL_READY':'control_ready','CLK_SEQ':'execute_clk','DISPATCH':'dispatch','FETCH':'fetch','ACTUAL_ADVANCE':'actual_advance','SP_UPDATE':'sp_update','SP_DOWN':'sp_down'}
    for pref,var,count in [('STEP_','step',4),('IR_','ir',8),('ROM_A','rom_address',13),('CW_','control_word',32),('ADDR_N_','addr_n',8),('SRC_N_','src_n',8),('DST_N_','dst_n',8),('PC_N_','pc_n',8),('MEM_N_','mem_n',4),('SP_N_','sp_n',4),('X_N_','x_n',4),('FLAGS_N_','flags_n',4),('ALU_N_','alu_n',16)]:
        outputs.update({f'{pref}{i}':f'{var}[{i}]' for i in range(count)})
    for n,v in outputs.items():lines.append(f'assign {v}={sig(n)};')
    lines.append('endmodule');destination.write_text('\n'.join(lines)+'\n');return actual,loads


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=definitions();parts,gates=design(defs);rows=emit_schematic(defs,parts)
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n');(OUT/'design.json').write_text(json.dumps({'iteration':'NET-04','parts':parts,'gates':gates},indent=2)+'\n')
    cmd=['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(VERIFY/'microcode_bank.xml'),str(OUT/'microcode_bank.kicad_sch')]
    result=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    actual,loads=convert(VERIFY/'microcode_bank.xml',defs,OUT/'microcode_bank_netlist.sv');failures=[]
    for r in rows:
        found=actual.get((r['reference'],r['pin']))
        if r['net']=='NC':
            if found and not found.startswith('unconnected-'):failures.append(r)
        elif found!=r['net']:failures.append({'expected':r,'actual':found})
    fanout=[{'net':n,'loads':len(v),'pins':v,'input_cap_budget_pf':10*len(v)} for n,v in loads.items() if n not in ('+5V','GND')]
    failures += [r for r in fanout if r['loads']>4]
    (VERIFY/'fanout.json').write_text(json.dumps({'assumption':'10 pF/input + 10 pF routing reserve; internal loads only','nets':sorted(fanout,key=lambda r:(-r['loads'],r['net']))},indent=2)+'\n')
    subprocess.run(['kicad-cli','sch','export','pdf','-o',str(VERIFY/'microcode_bank.pdf'),str(OUT/'microcode_bank.kicad_sch')],check=True,capture_output=True,text=True)
    report={'date':'2026-11-25','kicad':subprocess.check_output(['kicad-cli','version'],text=True).strip(),'command':cmd,'components':len(parts),'pins':len(rows),
      'no_connects':sum(r['net']=='NC' for r in rows),'max_signal_input_loads':max(r['loads'] for r in fanout),'stdout':result.stdout,'stderr':result.stderr,'failures':failures,'scope':'Pin graph, read-only ROM mode and load budget. Not ERC/DRC or complete-board timing.'}
    (VERIFY/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True);return int(bool(failures))


if __name__=='__main__':raise SystemExit(main())
