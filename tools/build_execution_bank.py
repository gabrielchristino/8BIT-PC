"""NET-08: execution handshake, stack guards and fault control."""
import csv
import json
from pathlib import Path
import re
import subprocess
import uuid
import xml.etree.ElementTree as ET
from build_stack_bank import symbol as previous_symbol
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"hardware/execution_bank"
VERIFY=ROOT/"verification/net08"


def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,"isa1/net08/"+s))


def definitions():
    from build_microcode_bank import definitions as md
    from build_stack_bank import definitions as sd
    from build_transaction_bank import definitions as td
    base=md();base.update(sd());base.update(td())
    return {k:base[k] for k in ('SN74HC174','SN74HC08','SN74HC32','SN74HC04','SN74HC125','C')}


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
    def A(*items,name=None):return tree('SN74HC08',list(items),name)
    def O(*items,name=None):return tree('SN74HC32',list(items),name)
    safe=AND('RESET_N','POWER_GOOD','SAFE')
    executing=NOT(O('RESPONSE','DROP','X_LOAD'),'EXEC')
    running=A(safe,executing,'RUN',NOT('HALTED'),'X_READY',name='RUNNING')
    accept=AND(running,'CONTROL_READY','ACCEPT')
    memory='MEM_N_0' # Active-low decoder Y0 is high for every nonzero memory mode.
    normal=AND(accept,NOT('MEM_N_0'),'EXEC_ACCEPT')
    A(safe,running,NOT('MEM_N_0'),name='EXECUTE_PULSE')
    # All comparisons are explicit binary threshold gates, not behavioral HDL.
    low15=O(*[f'SP_{i}' for i in range(15)])
    low14=O(*[f'SP_{i}' for i in range(14)])
    zero=NOT(O('SP_15',low15))
    over=AND('SP_15',low15)
    below4000=NOT(O('SP_15','SP_14'))
    atmost4000=A(NOT('SP_15'),O(NOT('SP_14'),NOT(low14)))
    below2=NOT(O(*[f'SP_{i}' for i in range(1,16)]))
    below4002=A(NOT('SP_15'),O(NOT('SP_14'),NOT(O(*[f'SP_{i}' for i in range(1,14)]))))
    above7ffe=O('SP_15',A(*[f'SP_{i}' for i in range(15)]))
    op50_51=A(NOT('IR_7'),'IR_6',NOT('IR_5'),'IR_4',NOT('IR_3'),NOT('IR_2'),NOT('IR_1'))
    call=A(op50_51,NOT('IR_0'),NOT('STACK_CHECKED'))
    ret=A(op50_51,'IR_0',NOT('STACK_CHECKED'))
    push_bad=A(NOT('ADDR_N_5'),O(zero,over,AND('BOOT',atmost4000),AND(call,O(below2,AND('BOOT',below4002)))) ,name='PUSH_BAD')
    pop_bad=A(NOT('ADDR_N_4'),O('SP_15',AND('BOOT',below4000),AND(ret,above7ffe)),name='POP_BAD')
    bad=O(push_bad,pop_bad)
    access=A(accept,memory,NOT(bad),name='ACCESS')
    fault=A(accept,memory,bad,name='GUARD_FAULT')
    halted_word=AND(normal,'CW_HALT','HALT_EXEC')
    invalid=A(halted_word,NOT(A(*[f'IR_{i}' for i in range(8)])))
    x_start=A(normal,NOT('CW_HALT'),'USE_X',NOT('X_N_1'),name='X_START')
    x_resume=A('X_LOAD','RUN','CONTROL_READY',O('X_DONE','X_COMPLETED'),name='X_RESUME')
    normal_advance=A(normal,NOT('CW_HALT'),NOT(x_start))
    drop_advance=A('DROP','BUS_READY','CONTROL_READY')
    advancing=O(x_resume,normal_advance,drop_advance)
    normal_request=A('EXECUTE_PULSE',NOT('CW_HALT'),NOT(AND('USE_X',NOT('X_N_1'))))
    O(AND('DROP','BUS_READY'),A('X_LOAD','RUN',O('X_DONE','X_COMPLETED')),normal_request,name='ADVANCE_REQ')
    resp_d=O(access,A('RESPONSE',NOT('BUS_DONE')),name='RESP_D')
    drop_d=O(A('RESPONSE','BUS_DONE'),A('DROP',NOT(AND('BUS_READY','CONTROL_READY'))),name='DROP_D')
    x_d=O(x_start,AND('X_LOAD',NOT(x_resume)),name='X_D')
    comp_d=A('X_LOAD',NOT(x_resume),O('X_DONE','X_COMPLETED'),name='X_COMP_D')
    checked=A(NOT('DISPATCH'),O('STACK_CHECKED',AND(access,O(NOT('ADDR_N_4'),NOT('ADDR_N_5')))),name='CHECKED_D')
    halt_d=O('HALTED',fault,halted_word,name='HALTED_D')
    retire=O(fault,halted_word,A(advancing,'CW_END',NOT('DISPATCH')),name='RETIRED_D')
    error=O(fault,invalid)
    f0=O(A(error,O(AND(fault,push_bad),invalid)),AND(NOT(error),'FAULT_0'),name='FAULT_D0')
    f1=O(A(error,O(AND(fault,pop_bad),invalid)),AND(NOT(error),'FAULT_1'),name='FAULT_D1')
    A('USE_X',executing,'RUN',NOT('HALTED'),'CONTROL_READY',O(NOT('X_N_2'),NOT('X_N_3')),name='X_COUNT')
    O('RESPONSE','X_LOAD',name='STATE_0');O('DROP','X_LOAD',name='STATE_1')
    # RESP is also the held bus start, X_LOAD the held load request.
    for fs in [dict(zip(['RESPONSE','DROP','X_LOAD','X_COMPLETED','STACK_CHECKED','HALTED'],[resp_d,drop_d,x_d,comp_d,checked,halt_d])),dict(zip(['FAULT_0','FAULT_1','RETIRED'],[f0,f1,retire]))]:
        outputs=list(fs);part('SN74HC174',{'CLR_N':'SAFE','CLK':'CLK_CORE',**{f'D{i}':fs[outputs[i]] if i<len(outputs) else 'GND' for i in range(6)},**{f'Q{i}':outputs[i] if i<len(outputs) else None for i in range(6)}})
    part('SN74HC125',{'A0':'CLK','A1':'GND','A2':'GND','A3':'GND',**{f'OE{i}_N':'GND' for i in range(4)},'Y0':'CLK_CORE'})
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
    for i,p in enumerate(parts):p.update(x=60+98*(i%8),y=65+75*(i//8))
    chips=list(parts)
    if len(chips)>56:raise ValueError('A1 layout capacity exceeded')
    for i,p in enumerate(chips,1):
        cap={'reference':f'C{i}','part':'C','nets':{'1':'+5V','2':'GND'},'x':p['x']+31,'y':p['y']-25};parts.append(cap)
    return parts,gates


def package_symbol(kind,spec):
    text,locations=previous_symbol(kind,spec)
    return text.replace('NET02:','NET08:'),locations


def emit_schematic(defs,parts):
    prepared={k:package_symbol(k,v) for k,v in defs.items()};sheet=uid('sheet')
    lines=[f'(kicad_sch (version 20230121) (generator eeschema) (uuid {sheet}) (paper "A1")',
      '(title_block (title "ISA-1 execution handshake / guards / faults") (rev "NET-08") (date "2026-11-25") (comment 1 "PARTIAL EXECUTION CONTROL - NOT FOR PRODUCTION"))',
      '(lib_symbols '+" ".join(v[0] for v in prepared.values())+')'];rows=[]
    for p in parts:
        ref,kind,x,y=p['reference'],p['part'],p['x'],p['y'];value='100nF' if kind=='C' else kind
        ax,ay=(x+5,y-2) if kind=='C' else (x,y-(33 if kind=='AT28HC64B' else 25.4))
        props=f'(property "Reference" "{ref}" (at {ax} {ay} 0) (effects (font (size 1 1)))) (property "Value" "{value}" (at {ax} {ay+2.54} 0) (effects (font (size 1 1)))) '
        pp=' '.join(f'(pin "{pin}" (uuid {uid(ref+"/"+pin)}))' for pin in p['nets'])
        lines.append(f'(symbol (lib_id "NET08:{kind}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (uuid {uid(ref)}) {props}{pp} (instances (project "execution_bank" (path "/{sheet}" (reference "{ref}") (unit 1)))))')
        for pin,net in p['nets'].items():
            px,py,angle=prepared[kind][1][pin];px+=x;py=y-py
            rows.append({'reference':ref,'part':kind,'pin':pin,'function':defs[kind]['pins'][pin]['name'],'net':net or 'NC'})
            if net is None:lines.append(f'(no_connect (at {px} {py}) (uuid {uid(ref+"/nc/"+pin)}))')
            else:lines.append(f'(label "{net}" (at {px} {py} 0) (effects (font (size 0.9 0.9)) (justify {"right bottom" if angle==0 else "left bottom"})) (uuid {uid(ref+"/label/"+pin)}))')
    for y,t in [(15,'One-hot response/drop/X-load, implicit EXEC; held requests, stack preflight and fault/retire storage.'),(571,'ROM fields and transaction handshake external. Reset/power digital only; global timing and board validation pending.')]:
        lines.append(f'(text "{t}" (at 18 {y} 0) (effects (font (size 1.5 1.5)) (justify left)) (uuid {uid(t)}))')
    lines+=['(sheet_instances (path "/" (page "1")))',')'];(OUT/'execution_bank.kicad_sch').write_text('\n'.join(lines)+'\n')
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
    lines=['`timescale 1ns/1ps','// GENERATED from KiCad XML pin graph; no behavioral control FSM.',
      'module execution_bank_netlist #(parameter integer TIMED=0)(input wire clk,reset_n,power_good,run,control_ready,x_ready,x_done,use_x,boot,bus_ready,bus_done,dispatch,cw_end,cw_halt,input wire [7:0] ir,addr_n,input wire [3:0] mem_n,x_n,input wire [15:0] sp,output wire execute_pulse,advance_req,bus_start,x_load_request,x_count,stack_checked,halted,retired,output wire [1:0] fault,state);',
      'localparam GATE_T=TIMED?31:0,INV_T=TIMED?24:0,BUF_T=TIMED?36:0;']
    lines+=['wire '+n+';' for n in sorted(names)]
    ports={'CLK':'clk','RESET_N':'reset_n','POWER_GOOD':'power_good','RUN':'run','CONTROL_READY':'control_ready','X_READY':'x_ready','X_DONE':'x_done','USE_X':'use_x','BOOT':'boot','BUS_READY':'bus_ready','BUS_DONE':'bus_done','DISPATCH':'dispatch','CW_END':'cw_end','CW_HALT':'cw_halt',**{f'IR_{i}':f'ir[{i}]' for i in range(8)},**{f'ADDR_N_{i}':f'addr_n[{i}]' for i in range(8)},**{f'{p}_{i}':f'{v}[{i}]' for p,v in [('MEM_N','mem_n'),('X_N','x_n')] for i in range(4)},**{f'SP_{i}':f'sp[{i}]' for i in range(16)}}
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
        if kind=='SN74HC174':lines.append(f"hc174_model #(.TIMED(TIMED)) {ref}({fs['CLK']},{fs['CLR_N']},{vec('D',6)},{vec('Q',6)});")
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
    outputs={'EXECUTE_PULSE':'execute_pulse','ADVANCE_REQ':'advance_req','RESPONSE':'bus_start','X_LOAD':'x_load_request','X_COUNT':'x_count','STACK_CHECKED':'stack_checked','HALTED':'halted','RETIRED':'retired','FAULT_0':'fault[0]','FAULT_1':'fault[1]','STATE_0':'state[0]','STATE_1':'state[1]'}
    for n in outputs:
        if len(drivers.get(n,[]))!=1:raise ValueError('Missing output driver '+n)
    for n,v in outputs.items():lines.append(f'assign {v}={sig(n)};')
    lines.append('endmodule');destination.write_text('\n'.join(lines)+'\n');return actual,loads


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=definitions();parts,gates=design(defs);rows=emit_schematic(defs,parts)
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n');(OUT/'design.json').write_text(json.dumps({'iteration':'NET-08','parts':parts,'gates':gates},indent=2)+'\n')
    cmd=['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(VERIFY/'execution_bank.xml'),str(OUT/'execution_bank.kicad_sch')]
    result=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    actual,loads=convert(VERIFY/'execution_bank.xml',defs,OUT/'execution_bank_netlist.sv');failures=[]
    for r in rows:
        found=actual.get((r['reference'],r['pin']))
        if r['net']=='NC':
            if found and not found.startswith('unconnected-'):failures.append(r)
        elif found!=r['net']:failures.append({'expected':r,'actual':found})
    fanout=[{'net':n,'loads':len(v),'pins':v,'input_cap_budget_pf':10*len(v)} for n,v in loads.items() if n not in ('+5V','GND')]
    failures += [r for r in fanout if r['loads']>4]
    (VERIFY/'fanout.json').write_text(json.dumps({'assumption':'10 pF/input + 10 pF routing reserve; internal loads only','nets':sorted(fanout,key=lambda r:(-r['loads'],r['net']))},indent=2)+'\n')
    subprocess.run(['kicad-cli','sch','export','pdf','-o',str(VERIFY/'execution_bank.pdf'),str(OUT/'execution_bank.kicad_sch')],check=True,capture_output=True,text=True)
    report={'date':'2026-11-25','kicad':subprocess.check_output(['kicad-cli','version'],text=True).strip(),'command':cmd,'components':len(parts),'pins':len(rows),
      'no_connects':sum(r['net']=='NC' for r in rows),'max_signal_input_loads':max(r['loads'] for r in fanout),'stdout':result.stdout,'stderr':result.stderr,'failures':failures,'scope':'Pin graph and digital input load budget. Not ERC/DRC or complete-board timing.'}
    (VERIFY/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True);return int(bool(failures))


if __name__=='__main__':raise SystemExit(main())
