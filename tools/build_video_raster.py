"""NET-14B native pin circuit: one-hot clocks, asynchronous raster counters,
CMOS capture after the NET-13 TTL receiver. Not a fabrication release."""
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
import build_memory_bus as source

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/video_raster';VERIFY=ROOT/'verification/net14b'


def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net14b/'+s))


def definitions():
    defs={k:copy.deepcopy(v) for k,v in source.definitions().items() if k in ('SN74AHC08','SN74AHC32','SN74AHC04','SN74AHC125','C')}
    def add(kind,ins,outs,vcc,gnd):
        pins={str(p):{'name':n,'type':'input'} for p,n in ins.items()}
        pins.update({str(p):{'name':n,'type':'output'} for p,n in outs.items()})
        pins[str(vcc)]={'name':'VCC','type':'power_in'};pins[str(gnd)]={'name':'GND','type':'power_in'}
        defs[kind]={'pins':pins,'datasheet':'https://www.ti.com/lit/ds/symlink/'+kind.lower()+'.pdf','source':'Explicit TI package pin map; zero-based logical channels'}
    add('SN74LV161A',{1:'CLR_N',2:'CLK',3:'D0',4:'D1',5:'D2',6:'D3',7:'ENP',9:'LOAD_N',10:'ENT'},
        {14:'Q0',13:'Q1',12:'Q2',11:'Q3',15:'RCO'},16,8)
    add('SN74AHC74',{1:'CLR0_N',2:'D0',3:'CLK0',4:'PRE0_N',13:'CLR1_N',12:'D1',11:'CLK1',10:'PRE1_N'},
        {5:'Q0',6:'QB0',9:'Q1',8:'QB1'},14,7)
    add('SN74AHC574',{1:'OE_N',11:'CLK',**{i+2:f'D{i}' for i in range(8)}},
        {19-i:f'Q{i}' for i in range(8)},20,10)
    return defs


def ports():
    ins={'MASTER':'master','RESET_N':'reset_n','POWER_GOOD':'power_good'}
    ins.update({f'VIDEO_DATA_{i}':f'video_data[{i}]' for i in range(8)})
    outs={'BACKEND':'backend_clk','P3':'capture_clk','SLOT':'slot','VISIBLE':'visible','HSYNC_N':'hsync_n','VSYNC_N':'vsync_n','READY':'ready'}
    for prefix,port,width in [('H','h',8),('V','v',10),('PIXEL','pixel',8)]:
        outs.update({f'{prefix}_{i}':f'{port}[{i}]' for i in range(width)})
    return ins,outs


def design(defs):
    parts=[];gates=[];cache={};ffs=[]
    def part(kind,fs):
        ref=f'U{len(parts)+1}';pins={p:fs.get(s['name']) for p,s in defs[kind]['pins'].items()}
        for p,s in defs[kind]['pins'].items():
            if s['name'] in ('VCC','GND'):pins[p]='+5V' if s['name']=='VCC' else 'GND'
        p={'reference':ref,'part':kind,'nets':pins};parts.append(p);return p
    def gate(kind,*args,name=None):
        if kind!='SN74AHC04':args=tuple(sorted(args))
        if kind=='SN74AHC08':
            if 'GND' in args:return 'GND'
            if '+5V' in args:return next((a for a in args if a!='+5V'),'+5V')
        if kind=='SN74AHC32':
            if '+5V' in args:return '+5V'
            if 'GND' in args:return next((a for a in args if a!='GND'),'GND')
        key=kind,args
        if key in cache:return cache[key]
        n=name or f'G_{len(gates)}';gates.append((kind,args,n));cache[key]=n;return n
    def AND(a,b,name=None):return gate('SN74AHC08',a,b,name=name)
    def OR(a,b,name=None):return gate('SN74AHC32',a,b,name=name)
    def NOT(a):
        if a in ('GND','+5V'):return '+5V' if a=='GND' else 'GND'
        return gate('SN74AHC04',a)
    def all_of(items):
        items=list(items)
        while len(items)>1:items=[AND(items[i],items[i+1]) if i+1<len(items) else items[i] for i in range(0,len(items),2)]
        return items[0]
    def eq(prefix,width,value):return all_of(f'{prefix}_{i}' if value>>i&1 else NOT(f'{prefix}_{i}') for i in range(width))
    def lt(prefix,width,value):
        result='GND'
        for i in range(width):
            n=NOT(f'{prefix}_{i}')
            result=OR(n,result) if value>>i&1 else AND(n,result)
        return result
    def ff(d,clock,q,clr,pre='+5V'):
        ffs.append({'D':d,'CLK':clock,'Q':q,'CLR_N':clr,'PRE_N':pre})
    rawsafe=AND('RESET_N','POWER_GOOD','SAFE')
    # Asynchronous assertion, two-master-edge release before distributing reset.
    # Metastability/MTBF and physical brownout sequencing are separate analyses.
    ff('+5V','MASTER','RESET_STAGE1',rawsafe)
    ff('RESET_STAGE1','MASTER','LOCAL_RESET_N',rawsafe)
    safe='LOCAL_RESET_N';unsafe=NOT(safe)
    # One-hot ring: phase 3 is preset during reset, phases 0..2 cleared.
    # Every runtime clock output comes from a FF, never a decoded clock gate.
    for i in range(4):ff(f'P{(i-1)%4}','MASTER',f'P{i}',safe if i!=3 else '+5V',safe if i==3 else '+5V')
    ff(OR('P1','P2'),'MASTER','BACKEND',safe)
    ff('+5V','P0','RUN',safe)
    ff('+5V','P3','READY',safe)
    hlast=eq('H',8,199);vlast=eq('V',10,524)
    vload=NOT(AND(hlast,vlast));hload=NOT(hlast);ven=AND('RUN',hlast)
    # All five raster counters share phase-0 clock, with synchronous enables
    # and synchronous zero load. Asynchronous CLR works with stopped clocks.
    for prefix,width,enable,load in [('H',8,'RUN',hload),('V',10,ven,vload)]:
        for nib in range((width+3)//4):
            ent='+5V' if nib==0 else f'{prefix}_CARRY_{nib-1}'
            fs={'CLK':'P0','CLR_N':safe,'LOAD_N':load,'ENP':enable,'ENT':ent,'RCO':f'{prefix}_CARRY_{nib}'}
            for bit in range(4):fs[f'D{bit}']='GND';fs[f'Q{bit}']=f'{prefix}_{nib*4+bit}' if nib*4+bit<width else None
            part('SN74LV161A',fs)
    active=AND(lt('H',8,160),lt('V',10,480))
    # 164..187 = high group 101 and low three-bit group H[4:2] in 1..6.
    # Balanced explicit terms avoid the slow serial magnitude-comparator chain.
    high101=all_of(['H_7',NOT('H_6'),'H_5'])
    low_nonzero=OR(OR('H_4','H_3'),'H_2')
    low_not7=NOT(all_of(['H_4','H_3','H_2']))
    hs=NOT(all_of([high101,low_nonzero,low_not7]))
    vs=NOT(all_of(f'V_{i}' if (490>>i)&1 else NOT(f'V_{i}') for i in range(1,10)))
    # Register from the previous H before the phase-0 counters update:
    # H=160..191 predicts current H=161..192. This gives the controller a
    # complete half-cycle; phase-1 capture was too late through its input gates.
    slot=high101
    ff(slot,'P0','SLOT',safe)
    # Pixel data is captured directly from the CMOS output of HCT244. Blank
    # only after capture, avoiding extra logic in the SRAM->capture path.
    for prefix,inputs in [('COLOR',[f'VIDEO_DATA_{i}' for i in range(8)]),('META',[active,hs,vs]+['GND']*5)]:
        fs={'CLK':'P3','OE_N':'GND'}
        for i in range(8):fs[f'D{i}']=inputs[i];fs[f'Q{i}']=f'{prefix}_{i}' if prefix=='COLOR' or i<3 else None
        part('SN74AHC574',fs)
    enabled=AND(safe,'READY');shown=AND(enabled,'META_0','VISIBLE')
    for i in range(8):AND(shown,f'COLOR_{i}',f'PIXEL_{i}')
    NOT_enabled=NOT(enabled)
    OR(NOT_enabled,'META_1','HSYNC_N');OR(NOT_enabled,'META_2','VSYNC_N')
    # Pack individual FFs, retaining explicit unused-pin ties.
    for first in range(0,len(ffs),2):
        fs={}
        for i in range(2):
            f=ffs[first+i] if first+i<len(ffs) else {'D':'GND','CLK':'GND','CLR_N':safe,'PRE_N':'+5V','Q':None}
            for name in ('D','CLK','Q','CLR_N','PRE_N'):fs[name.replace('_N',str(i)+'_N') if name.endswith('_N') else name+str(i)]=f[name]
            fs[f'QB{i}']=None
        part('SN74AHC74',fs)
    for kind in ('SN74AHC08','SN74AHC32','SN74AHC04'):
        gs=[g for g in gates if g[0]==kind];cap=6 if kind=='SN74AHC04' else 4
        for first in range(0,len(gs),cap):
            fs={}
            for i in range(cap):
                g=gs[first+i] if first+i<len(gs) else None;fs[f'A{i}']=g[1][0] if g else 'GND'
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
    return parts


def package_symbol(kind,spec):
    return tuple(x.replace('NET02:','NET14B:') if isinstance(x,str) else x for x in old_symbol(kind,spec))


# Reuse the already-tested native schematic emitter, with separate identity,
# filenames, sheet and titles. No generated or historical source is modified.
_emitter=inspect.getsource(source.emit).replace('memory_bus','video_raster').replace('NET13','NET14B').replace('NET-13','NET-14B').replace('paper "A1"','paper "A0"').replace('ISA-1 SRAM / EEPROM data front-end','ISA-1 raster / registered video clocks / capture')
exec(_emitter,globals())


def convert(source_path=None,destination=None):
    source_path=source_path or VERIFY/'video_raster.xml';destination=destination or OUT/'video_raster_netlist.sv'
    defs=json.loads((OUT/'package-functions.json').read_text());parts=json.loads((OUT/'design.json').read_text())['parts'];expected={p['reference']:p for p in parts}
    root=ET.parse(source_path).getroot();actual={};nets=set()
    for n in root.findall('./nets/net'):
        name=n.get('name').removeprefix('/');nets.add(name)
        for p in n.findall('node'):
            key=(p.get('ref'),p.get('pin'))
            if key in actual:raise ValueError('Multiple nets '+str(key))
            actual[key]=name
    ins,outs=ports();drivers={n:['external'] for n in [*ins,'+5V','GND']};loads={};lines=[];seen=set()
    for c in root.findall('./components/comp'):
        ref=c.get('ref');p=expected[ref];kind=p['part'];seen.add(ref);fs={}
        if c.findtext('value')!=('100nF' if kind=='C' else kind):raise ValueError('Value changed '+ref)
        for pin,s in defs[kind]['pins'].items():
            n=actual.get((ref,pin));typ=s['type'];name=s['name']
            if typ in ('input','power_in') and (not n or n.startswith('unconnected-')):raise ValueError('Floating input '+ref+'/'+pin)
            if name in ('VCC','GND') and n!={'VCC':'+5V','GND':'GND'}[name]:raise ValueError('Wrong power '+ref)
            if n and not n.startswith('unconnected-'):fs[name]=sig(n)
            if typ=='input':loads.setdefault(n,[]).append(ref+'/'+pin)
            if typ=='output' and name in fs:drivers.setdefault(n,[]).append(ref+'/'+pin)
        def vec(prefix,w):return '{'+','.join(fs.get(f'{prefix}{i}',f'{ref}_unused_{prefix}{i}') for i in reversed(range(w)))+'}'
        if kind=='C':continue
        if kind=='SN74LV161A':
            lines.append(f"net14b_lv161 #(.TIMED(TIMED)) {ref}({fs['CLK']},{fs['CLR_N']},{fs['LOAD_N']},{fs['ENP']},{fs['ENT']},{vec('D',4)},{vec('Q',4)},{fs['RCO']},checks);")
        elif kind=='SN74AHC574':lines.append(f"net14b_ahc574 #(.TIMED(TIMED)) {ref}({fs['CLK']},{fs['OE_N']},{vec('D',8)},{vec('Q',8)},checks);")
        elif kind=='SN74AHC74':
            for i in range(2):
                q=fs.get(f'Q{i}');qb=fs.get(f'QB{i}')
                if q is None and qb is None:continue
                early=int(q==sig('P3'))
                lines.append(f"net14b_ahc74 #(.TIMED(TIMED),.EARLY({early} && EARLY_CAPTURE)) {ref}_{i}({fs[f'CLK{i}']},{fs[f'CLR{i}_N']},{fs[f'PRE{i}_N']},{fs[f'D{i}']},{q or ref+'_unused_q'+str(i)},{qb or ref+'_unused_qb'+str(i)},checks);")
        elif kind in ('SN74AHC08','SN74AHC32'):
            op='&' if kind=='SN74AHC08' else '|'
            for i in range(4):
                if f'Y{i}' in fs:lines.append(f"assign #GATE_T {fs[f'Y{i}']}={fs[f'A{i}']} {op} {fs[f'B{i}']};")
        elif kind=='SN74AHC04':
            for i in range(6):
                if f'Y{i}' in fs:lines.append(f"assign #GATE_T {fs[f'Y{i}']}=~{fs[f'A{i}']};")
        elif kind=='SN74AHC125':
            for i in range(4):
                if f'Y{i}' in fs:lines.append(f"assign #GATE_T {fs[f'Y{i}']}={fs[f'OE{i}_N']} ? 1'bz : {fs[f'A{i}']};")
        else:raise ValueError('No model '+kind)
    if seen!=set(expected):raise ValueError('Inventory mismatch')
    for n,uses in loads.items():
        if len(drivers.get(n,[]))!=1:raise ValueError('Driver count '+str(n))
    for n in outs:
        if len(drivers.get(n,[]))!=1:raise ValueError('Undriven output '+n)
    if any(len(v)!=1 for v in drivers.values()):raise ValueError('Multiple drivers')
    header=['`timescale 1ns/1ps','// GENERATED from actual KiCad XML; selected package models, no PCB approval.',
      'module video_raster_netlist #(parameter TIMED=0,EARLY_CAPTURE=0)(input wire master,reset_n,power_good,input wire [7:0] video_data,output wire backend_clk,capture_clk,slot,visible,hsync_n,vsync_n,ready,output wire [7:0] h,output wire [9:0] v,output wire [7:0] pixel);',
      'localparam GATE_T=TIMED?10:0;wire checks=reset_n && power_good;']
    header+=['wire '+sig(n)+';' for n in sorted(nets|set(ins)) if n not in ('+5V','GND') and not n.startswith('unconnected-')]
    # Explicit spare counter/register outputs remain local wires.
    import re
    spares=sorted(set(re.findall(r'\bU\d+_unused_\w+', '\n'.join(lines))))
    header+=['wire '+n+';' for n in spares]
    header += [f'assign {sig(n)}={value};' for n,value in ins.items()]
    lines += [f'assign {value}={sig(n)};' for n,value in outs.items()]+['endmodule']
    destination.write_text('\n'.join(header+lines)+'\n')
    failures=[]
    for p in parts:
        for pin,n in p['nets'].items():
            got=actual.get((p['reference'],pin))
            if n is not None and got!=n:failures.append([p['reference'],pin,n,got])
            if n is None and got and not got.startswith('unconnected-'):failures.append([p['reference'],pin,'NC',got])
    return {'components':len(parts),'ics':sum(p['part']!='C' for p in parts),'pins':sum(len(p['nets']) for p in parts),'no_connects':sum(n is None for p in parts for n in p['nets'].values()),'max_signal_input_loads':max(len(v) for n,v in loads.items() if n not in ('+5V','GND')),'failures':failures,'scope':'Native pin graph; electrical and clock/PVT qualification remain open'}


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=definitions();parts=design(defs);emit(defs,parts)
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n')
    (OUT/'design.json').write_text(json.dumps({'iteration':'NET-14B','parts':parts},indent=2)+'\n')
    cmd=[KICAD,'sch','export','netlist','--format','kicadxml','-o',str(VERIFY/'video_raster.xml'),str(OUT/'video_raster.kicad_sch')]
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    report=convert();report.update(command=cmd,kicad=subprocess.check_output([KICAD,'version'],text=True).strip())
    (VERIFY/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
    return int(bool(report['failures']) or report['max_signal_input_loads']>4)


if __name__=='__main__':raise SystemExit(main())
