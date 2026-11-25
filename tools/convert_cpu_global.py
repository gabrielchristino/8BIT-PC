"""NET-10 simulation model from the actually exported joined KiCad graph."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from build_cpu_global import ROOT,OUT,VERIFY,sig,vec


def convert(source=None,destination=None):
    source=source or VERIFY/'cpu_global.xml';destination=destination or OUT/'cpu_global_netlist.sv'
    defs=json.loads((OUT/'package-functions.json').read_text())
    design=json.loads((OUT/'design.json').read_text());parts={p['reference']:p for p in design['parts']}
    xml=ET.parse(source).getroot();actual={};nets=set();drivers={};inputs=[]
    for net in xml.findall('./nets/net'):
        n=net.get('name').removeprefix('/');nets.add(n)
        for node in net.findall('node'):
            key=(node.get('ref'),node.get('pin'))
            if key in actual:raise ValueError('Pin in multiple nets '+str(key))
            actual[key]=n
    external={'CLK':'clk','RESET_N':'reset_n','POWER_GOOD':'power_good','RUN':'run','BOOT':'boot','ACKNOWLEDGE':'acknowledge',**{f'READ_DATA_{i}':f'read_data[{i}]' for i in range(8)}}
    drivers={n:['external'] for n in [*external,'+5V','GND']}
    outputs={'REQUEST':'request','WRITE_ENABLE':'write_enable','Z':'z','C':'c','HALTED':'halted','RETIRED':'retired'}
    for n,v,k in [('ADDRESS','address',16),('WRITE_DATA','write_data',8),('PC','pc',16),('SP','sp',16),('X','x',16),('A','a',8),('B','b',8),('FAULT','fault',2),('CONTROL_ADDRESS','control_address',13),('CW','control_word',32)]:outputs.update({f'{n}_{i}':f'{v}[{i}]' for i in range(k)})
    header=['`timescale 1ns/1ps','// GENERATED from actual joined KiCad XML, including distribution buffers. CPU only.',
      'module isa1_cpu #(parameter ROM_PREFIX="control_lane",parameter integer TIMED=0,USE_HC191=0)(',
      'input wire clk,reset_n,power_good,run,boot,output wire request,write_enable,output wire [15:0] address,output wire [7:0] write_data,input wire acknowledge,input wire [7:0] read_data,',
      'output wire [15:0] pc,sp,x,output wire [7:0] a,b,output wire z,c,halted,retired,output wire [1:0] fault,output wire [12:0] control_address,output wire [31:0] control_word);',
      'localparam GATE_T=TIMED?31:0,INV_T=TIMED?24:0,BUF_T=TIMED?36:0,MUX_T=TIMED?38:0,SUM_T=TIMED?58:0,CARRY_T=TIMED?49:0,DEC_T=TIMED?45:0;',
      'initial if(USE_HC191!=0)$fatal(1,"Joined graph is main synchronous-X configuration only");']
    lines=[];observers={};seen=set()
    for comp in xml.findall('./components/comp'):
        ref=comp.get('ref')
        if ref not in parts:raise ValueError('Unknown exported component '+ref)
        p=parts[ref];kind=p['part'];seen.add(ref)
        if comp.findtext('value')!=('100nF' if kind=='C' else kind):raise ValueError('Part value changed '+ref)
        fs={}
        for pin,spec in defs[kind]['pins'].items():
            n=actual.get((ref,pin));typ=spec['type'];name=spec['name']
            if typ in ('input','power_in') and (not n or n.startswith('unconnected-')):raise ValueError(f'Floating input {ref}/{pin}')
            if name in ('VCC','GND') and n!={'VCC':'+5V','GND':'GND'}[name]:raise ValueError('Power connection '+ref)
            if not n and typ in ('output','bidirectional'):n=f'NC_{ref}_{pin}';nets.add(n)
            if n:fs[name]=sig(n)
            if typ=='input':inputs.append((ref,pin,n))
            if typ in ('output','bidirectional') and n:drivers.setdefault(n,[]).append(ref+'/'+pin)
            if pin in p.get('unused_output_observers',{}) and n:observers[p['unused_output_observers'][pin]]=sig(n)
        def v(prefix,k):return '{'+','.join(fs[f'{prefix}{i}'] for i in reversed(range(k)))+'}'
        if kind=='C':continue
        if kind=='SN74HC273':lines.append(f"hc273_functional #(.T_CQ(TIMED?40:0),.T_CLR(TIMED?40:0),.CHECKS(TIMED)) {ref}({fs['CLK']},{fs['CLR_N']},{v('D',8)},{v('Q',8)});")
        elif kind=='SN74HC174':lines.append(f"hc174_model #(.TIMED(TIMED)) {ref}({fs['CLK']},{fs['CLR_N']},{v('D',6)},{v('Q',6)});")
        elif kind=='SN74HC74':
            for i in range(2):
                lines.append(f"hc74_model #(.TIMED(TIMED)) {ref}_{i}({fs[f'CLK{i}']},{fs[f'CLR{i}_N']},{fs[f'PRE{i}_N']},{fs[f'D{i}']},{fs.get(f'Q{i}','')},{fs.get(f'QN{i}','')});")
                if p['group']=='registers':lines.append(f"if(TIMED) dff_timing #(.WIDTH(1),.RECOVERY(6),.CLEAR_PULSE(25)) {ref}_check_{i}({fs[f'CLK{i}']},{fs[f'CLR{i}_N']},{fs[f'D{i}']});")
        elif kind=='SN74HC161':lines.append(f"hc161_model #(.TIMED(TIMED)) {ref}({fs['CLK']},{fs['CLR_N']},{fs['LOAD_N']},{fs['ENP']},{fs['ENT']},{v('D',4)},{v('Q',4)},{fs.get('RCO','')});")
        elif kind in ('SN74HC377','SN74HCT377'):
            delay=38 if kind=='SN74HCT377' else 40
            lines.append(f"sn74hc377_model #(.T_CQ(TIMED?{delay}:0)) {ref}({fs['CLK']},{fs['EN_N']},{v('D',8)},{v('Q',8)});")
            checker='hct377_timing' if kind=='SN74HCT377' else 'hc377_timing'
            lines.append(f"if(TIMED) {checker} {ref}_check({fs['CLK']},{fs['EN_N']},{v('D',8)},reset_n && power_good);")
        elif kind=='SN74HC157':lines.append(f"sn74hc157_model #(.T_PD(MUX_T)) {ref}({v('A',4)},{v('B',4)},{fs['SELECT']},{fs['G_N']},{v('Y',4)});")
        elif kind=='CD74HC283':lines.append(f"hc283_functional #(.T_SUM(SUM_T),.T_CARRY(CARRY_T)) {ref}({v('A',4)},{v('B',4)},{fs['CIN']},{v('S',4)},{fs.get('COUT','')});")
        elif kind=='SN74HC138':lines.append(f"hc138_model #(.T_PD(DEC_T)) {ref}({{{fs['C']},{fs['B']},{fs['A']}}},{fs['G1']},{fs['G2A_N']},{fs['G2B_N']},{v('Y',8)});")
        elif kind=='SN74HC139':
            for i in range(2):lines.append(f"hc139_model #(.T_PD(DEC_T)) {ref}_{i}({{{fs[f'B{i}']},{fs[f'A{i}']}}},{fs[f'G{i}_N']},{v(f'Y{i}_',4)});")
        elif kind=='AT28HC64B':
            if (fs['WE_N'],fs['OE_N'],fs['CE_N'])!=("1'b1","1'b0","1'b0"):raise ValueError('Control ROM mode changed')
            lane=int(p['origin_reference'][1:])-11
            if p['group']!='micro' or lane not in range(4):raise ValueError('Control ROM origin missing')
            lines.append(f"at28hc64_read #(.FILE({{ROM_PREFIX,\"{lane}.hex\"}}),.T_ACC(TIMED?120:0)) {ref}({v('A',13)},{v('IO',8)});")
        elif kind in ('SN74HC08','SN74HC32','SN74HC86'):
            op={'SN74HC08':'&','SN74HC32':'|','SN74HC86':'^'}[kind]
            for i in range(4):lines.append(f"assign #GATE_T {fs[f'Y{i}']}={fs[f'A{i}']} {op} {fs[f'B{i}']};")
        elif kind=='SN74HC04':
            for i in range(6):lines.append(f"assign #INV_T {fs[f'Y{i}']}=~{fs[f'A{i}']};")
        elif kind=='SN74HC125':
            for i in range(4):lines.append(f"assign #BUF_T {fs[f'Y{i}']}={fs[f'OE{i}_N']} ? 1'bz : {fs[f'A{i}']};")
        else:raise ValueError('No package model '+kind)
    if seen!=set(parts):raise ValueError('Exported part inventory mismatch')
    for ref,pin,n in inputs:
        if len(drivers.get(n,[]))!=1:raise ValueError(f'Driver count {ref}/{pin}: {n}')
    for n,d in drivers.items():
        if len(d)!=1:raise ValueError('Multiple drivers '+n)
    names=[sig(n) for n in nets if n not in ('+5V','GND')]
    if len(names)!=len(set(names)):raise ValueError('SV name collision')
    header+=['wire '+n+';' for n in sorted(names)]
    header+=[f'assign {sig(n)}={port};' for n,port in external.items()]
    for n,port in outputs.items():
        if len(drivers.get(n,[]))!=1:raise ValueError('Missing public output '+n)
        lines.append(f'assign {port}={sig(n)};')
    # Simulation-only observation aliases of existing nodes/pads, no extra gates or loads.
    lines.append(f"wire bus_start={sig('BUS_START')};")
    lines.append('wire [7:0] ir={'+','.join(sig(f'IR_{i}') for i in reversed(range(8)))+'};')
    lines.append('wire [1:0] state={'+observers['execution__STATE_1']+','+observers['execution__STATE_0']+'};')
    lines.append('endmodule');destination.write_text('\n'.join(header+lines)+'\n')
    report={'date':'2026-11-25','components':len(seen),'digital_inputs':len(inputs),'drivers':len(drivers),'scope':'Exact exported pin graph with external CPU boundary drivers; no peripheral electrical or PVT signoff','failures':[]}
    (VERIFY/'conversion-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return 0


if __name__=='__main__':raise SystemExit(convert())
