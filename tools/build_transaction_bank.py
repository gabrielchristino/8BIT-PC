"""NET-03: explicit transaction control ICs -> KiCad -> pin-connected HDL."""
import csv
import json
from pathlib import Path
import re
import subprocess
import uuid
import xml.etree.ElementTree as ET
from build_stack_bank import definitions as stack_definitions, symbol

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"hardware/transaction_bank"
VERIFY=ROOT/"verification/net03"


def uid(name):return str(uuid.uuid5(uuid.NAMESPACE_URL,"isa1/net03/"+name))


def definitions():
    defs=stack_definitions()
    defs={k:defs[k] for k in ("SN74HC04","SN74HC125","C")}
    def add(kind,ins,outs,vcc,gnd):
        pins={str(p):{"name":n,"type":"input"} for p,n in ins.items()}
        pins.update({str(p):{"name":n,"type":"output"} for p,n in outs.items()})
        pins[str(vcc)]={"name":"VCC","type":"power_in"};pins[str(gnd)]={"name":"GND","type":"power_in"}
        defs[kind]={"datasheet":"https://www.ti.com/lit/ds/symlink/"+kind.lower()+".pdf","pins":pins,
                    "source":"TI package pin functions, zero-based channel indices"}
    add("SN74HC174",{1:"CLR_N",9:"CLK",**{p:f"D{i}" for i,p in enumerate([3,4,6,11,13,14])}},
        {p:f"Q{i}" for i,p in enumerate([2,5,7,10,12,15])},16,8)
    add("SN74HC74",{1:"CLR0_N",2:"D0",3:"CLK0",4:"PRE0_N",10:"PRE1_N",11:"CLK1",12:"D1",13:"CLR1_N"},
        {5:"Q0",6:"QN0",9:"Q1",8:"QN1"},14,7)
    add("SN74HC377",{1:"EN_N",11:"CLK",**{p:f"D{i}" for i,p in enumerate([3,4,7,8,13,14,17,18])}},
        {p:f"Q{i}" for i,p in enumerate([2,5,6,9,12,15,16,19])},20,10)
    for kind in ("SN74HC08","SN74HC32"):
        add(kind,{**{p:f"A{i}" for i,p in enumerate([1,4,9,12])},**{p:f"B{i}" for i,p in enumerate([2,5,10,13])}},
            {p:f"Y{i}" for i,p in enumerate([3,6,8,11])},14,7)
    return defs


def design(defs):
    parts=[];gates=[];cache={}
    def part(ref,kind,functions):
        nets={p:functions.get(v["name"]) for p,v in defs[kind]["pins"].items()}
        if kind!="C":
            for p,v in defs[kind]["pins"].items():
                if v["name"] in ("VCC","GND"):nets[p]="+5V" if v["name"]=="VCC" else "GND"
        p={"reference":ref,"part":kind,"nets":nets};parts.append(p);return p
    def gate(kind,*inputs,name=None):
        if kind!="SN74HC04":inputs=tuple(sorted(inputs))
        key=(kind,inputs)
        if key in cache:return cache[key]
        net=name or f"G_{len(gates)}"
        gates.append({"part":kind,"inputs":inputs,"output":net});cache[key]=net;return net
    def AND(a,b,name=None):return gate("SN74HC08",a,b,name=name)
    def OR(a,b,name=None):return gate("SN74HC32",a,b,name=name)
    def NOT(a,name=None):return gate("SN74HC04",a,name=name)
    def any_of(inputs):
        layer=list(inputs)
        while len(layer)>1:layer=[OR(layer[i],layer[i+1]) if i+1<len(layer) else layer[i] for i in range(0,len(layer),2)]
        return layer[0]
    safe=AND("RESET_N","POWER_GOOD","SAFE")
    idle=NOT(any_of([f"P_{i}" for i in range(6)]),"IDLE")
    any_ack=any_of(["ACK_RAW","ACK1","ACK2"])
    no_ack=NOT(any_ack,"ACK_IDLE")
    ready=AND(AND(idle,no_ack),"SAFE_GUARD","READY")
    accept=AND(ready,"START","ACCEPT")
    not_ack=NOT("ACK2","ACK2_N")
    active_ack=AND("P_2","ACK2")
    next_active=OR("P_1",AND("P_2",not_ack))
    next_drain=OR(active_ack,AND("P_3","ACK2"))
    next_done=AND("P_3",not_ack)
    next_lock=OR("P_4",AND("P_5",OR("START",any_ack)))
    req=AND("P_2","SAFE_GUARD","REQUEST")
    AND(req,"WRITE_HELD","WRITE_ENABLE")
    AND("P_4","SAFE_GUARD","DONE")
    cap_n=NOT(AND("P_0","SAFE_CAPTURE"),"CAPTURE_N")
    read_n=NOT(AND(active_ack,"SAFE_CAPTURE"),"READ_CAPTURE_N")
    part("U1","SN74HC174",{"CLK":"CLK_CTRL","CLR_N":"CLEAR_STATE_N",
        **{f"D{i}":n for i,n in enumerate([accept,"P_0",next_active,next_drain,next_done,next_lock])},
        **{f"Q{i}":f"P_{i}" for i in range(6)}})
    part("U2","SN74HC74",{"CLK0":"CLK_CTRL","CLK1":"CLK_CTRL","CLR0_N":"CLEAR_SYNC_N","CLR1_N":"CLEAR_SYNC_N",
        "PRE0_N":"+5V","PRE1_N":"+5V","D0":"ACK_RAW","Q0":"ACK1","D1":"ACK1","Q1":"ACK2"})
    for bank in range(2):
        part(f"U{bank+3}","SN74HC377",{"CLK":"CLK_ADDR","EN_N":cap_n,
             **{f"D{i}":f"ISSUE_ADDR_{bank*8+i}" for i in range(8)},**{f"Q{i}":f"ADDR_{bank*8+i}" for i in range(8)}})
    part("U5","SN74HC377",{"CLK":"CLK_WRITE","EN_N":cap_n,
         **{f"D{i}":f"ISSUE_DATA_{i}" for i in range(8)},**{f"Q{i}":f"WDATA_{i}" for i in range(8)}})
    part("U6","SN74HC377",{"CLK":"CLK_WRITE","EN_N":cap_n,"D0":"ISSUE_WRITE","Q0":"WRITE_HELD",
         **{f"D{i}":"GND" for i in range(1,8)}})
    part("U7","SN74HC377",{"CLK":"CLK_READ","EN_N":read_n,
         **{f"D{i}":f"BUS_RDATA_{i}" for i in range(8)},**{f"Q{i}":f"RDATA_{i}" for i in range(8)}})
    part("U8","SN74HC125",{**{f"A{i}":"CLK" for i in range(4)},**{f"OE{i}_N":"GND" for i in range(4)},
         **{f"Y{i}":n for i,n in enumerate(["CLK_CTRL","CLK_ADDR","CLK_WRITE","CLK_READ"])}})
    part("U9","SN74HC125",{**{f"A{i}":safe for i in range(4)},**{f"OE{i}_N":"GND" for i in range(4)},
         **{f"Y{i}":n for i,n in enumerate(["CLEAR_STATE_N","CLEAR_SYNC_N","SAFE_GUARD","SAFE_CAPTURE"])}})
    next_ref=10
    for kind in ("SN74HC08","SN74HC32","SN74HC04"):
        group=[g for g in gates if g["part"]==kind];capacity=6 if kind=="SN74HC04" else 4
        for start in range(0,len(group),capacity):
            fs={}
            for i in range(capacity):
                g=group[start+i] if start+i<len(group) else None
                fs[f"A{i}"]=g["inputs"][0] if g else "GND"
                if capacity==4:fs[f"B{i}"]=g["inputs"][1] if g else "GND"
                fs[f"Y{i}"]=g["output"] if g else None
            part(f"U{next_ref}",kind,fs);next_ref+=1
    for i,p in enumerate(parts):p.update(x=64+110*(i%5),y=61+83*(i//5))
    for i,p in enumerate(list(parts),1):
        c=part(f"C{i}","C",{"1":"+5V","2":"GND"});c.update(x=p["x"]+33,y=p["y"]-19)
    return parts,gates


def emit_schematic(defs,parts):
    prepared={k:symbol(k,v) for k,v in defs.items()}
    prepared={k:(text.replace("NET02:","NET03:"),pos) for k,(text,pos) in prepared.items()}
    sheet=uid("sheet")
    lines=[f'(kicad_sch (version 20230121) (generator eeschema) (uuid {sheet}) (paper "A2")',
      '(title_block (title "ISA-1 transaction controller and retained payload") (rev "NET-03") (date "2026-11-25") (comment 1 "PARTIAL - CMOS PORTS - NOT FOR PRODUCTION"))',
      '(lib_symbols '+" ".join(v[0] for v in prepared.values())+')']
    rows=[]
    for p in parts:
        ref,kind,x,y=p["reference"],p["part"],p["x"],p["y"]
        value="100nF" if kind=="C" else kind
        ax,ay=(x+5,y-2) if kind=="C" else (x,y-25.4)
        props=f'(property "Reference" "{ref}" (at {ax} {ay} 0) (effects (font (size 1 1)))) '
        props+=f'(property "Value" "{value}" (at {ax} {ay+2.54} 0) (effects (font (size 1 1)))) '
        pins=" ".join(f'(pin "{pin}" (uuid {uid(ref+"/"+pin)}))' for pin in p["nets"])
        lines.append(f'(symbol (lib_id "NET03:{kind}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) '
          f'(uuid {uid(ref)}) {props}{pins} (instances (project "transaction_bank" (path "/{sheet}" (reference "{ref}") (unit 1)))))')
        for pin,net in p["nets"].items():
            px,py,angle=prepared[kind][1][pin];px+=x;py=y-py
            rows.append({"reference":ref,"part":kind,"pin":pin,"function":defs[kind]["pins"][pin]["name"],"net":net or "NC"})
            if net is None:lines.append(f'(no_connect (at {px} {py}) (uuid {uid(ref+"/nc/"+pin)}))')
            else:
                justify="right bottom" if angle==0 else "left bottom"
                lines.append(f'(label "{net}" (at {px} {py} 0) (effects (font (size 0.9 0.9)) (justify {justify})) (uuid {uid(ref+"/label/"+pin)}))')
    for y,text in [(17,"P0 CAPTURE -> P1 SETTLE -> P2 ACTIVE -> P3 DRAIN -> P4 DONE -> P5 LOCK -> all-zero IDLE."),
                   (391,"ACK: two ideal synchronizer FFs. START held high cannot repeat. Payload valid only after capture. CMOS input levels required.")]:
        lines.append(f'(text "{text}" (at 18 {y} 0) (effects (font (size 1.5 1.5)) (justify left)) (uuid {uid(text)}))')
    lines+=['(sheet_instances (path "/" (page "1")))',')']
    (OUT/"transaction_bank.kicad_sch").write_text("\n".join(lines)+"\n")
    with (OUT/"pinmap.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    return rows


def convert(xml_path,defs,destination):
    root=ET.parse(xml_path).getroot();actual={};nets=set()
    for net in root.findall("./nets/net"):
        name=net.get("name").removeprefix("/");nets.add(name)
        for node in net.findall("node"):
            key=(node.get("ref"),node.get("pin"))
            if key in actual:raise ValueError("Multiple pin nets")
            actual[key]=name
    def sig(n):
        if n=="+5V":return "1'b1"
        if n=="GND":return "1'b0"
        return "n_"+re.sub(r"[^A-Za-z0-9_]","_",n)
    names=[sig(n) for n in nets if n not in ("+5V","GND")]
    if len(names)!=len(set(names)):raise ValueError("Net name collision")
    lines=['`timescale 1ns/1ps','// GENERATED from KiCad-exported pin XML; no behavioral FSM.',
      'module transaction_bank_netlist #(parameter integer TIMED=0)(input wire clk,reset_n,power_good,start,issue_write,ack_raw,',
      'input wire [15:0] issue_address,input wire [7:0] issue_data,bus_rdata,',
      'output wire ready,done,request,write_enable,output wire [15:0] address,output wire [7:0] write_data,read_data,output wire [5:0] phase);',
      'localparam GATE_T=TIMED?25:0, INV_T=TIMED?24:0, BUF_T=TIMED?36:0, CQ_T=TIMED?40:0;']
    lines += ["wire "+n+";" for n in sorted(names)]
    ports={"CLK":"clk","RESET_N":"reset_n","POWER_GOOD":"power_good","START":"start","ISSUE_WRITE":"issue_write","ACK_RAW":"ack_raw"}
    ports.update({f"ISSUE_ADDR_{i}":f"issue_address[{i}]" for i in range(16)})
    ports.update({f"ISSUE_DATA_{i}":f"issue_data[{i}]" for i in range(8)})
    ports.update({f"BUS_RDATA_{i}":f"bus_rdata[{i}]" for i in range(8)})
    drivers={n:["external"] for n in [*ports,"+5V","GND"]};inputs=[];fanout={}
    for n,value in ports.items():lines.append(f"assign {sig(n)}={value};")
    for comp in root.findall("./components/comp"):
        ref=comp.get("ref");kind="C" if ref.startswith("C") else comp.findtext("value")
        if kind not in defs:raise ValueError("Unsupported "+kind)
        fs={}
        for pin,spec in defs[kind]["pins"].items():
            n=actual.get((ref,pin))
            if spec["type"] in ("input","power_in") and (not n or n.startswith("unconnected-")):raise ValueError(f"Floating input {ref}/{pin}")
            if spec["name"] in ("VCC","GND") and n!={"VCC":"+5V","GND":"GND"}[spec["name"]]:raise ValueError("Wrong power "+ref)
            if n:fs[spec["name"]]=sig(n)
            if spec["type"]=="input":inputs.append((ref,pin,n));fanout.setdefault(n,[]).append(ref+"/"+pin)
            if spec["type"]=="output" and n:drivers.setdefault(n,[]).append(ref+"/"+pin)
        def vec(prefix,n):return '{'+','.join(fs[f'{prefix}{i}'] for i in reversed(range(n)))+'}'
        if kind=="SN74HC174":lines.append(f"hc174_model #(.TIMED(TIMED)) {ref}({fs['CLK']},{fs['CLR_N']},{vec('D',6)},{vec('Q',6)});")
        elif kind=="SN74HC74":
            for i in range(2):
                lines.append(f"hc74_model #(.TIMED(TIMED)) {ref}_{i}({fs[f'CLK{i}']},{fs[f'CLR{i}_N']},{fs[f'PRE{i}_N']},{fs[f'D{i}']},{fs[f'Q{i}']},{fs.get(f'QN{i}','')});")
                if i==1:lines.append(f"if(TIMED) dff_timing #(.WIDTH(1),.RECOVERY(6),.CLEAR_PULSE(25)) {ref}_sync2_check({fs[f'CLK{i}']},{fs[f'CLR{i}_N']},{fs[f'D{i}']});")
        elif kind=="SN74HC377":
            lines.append(f"sn74hc377_model #(.T_CQ(CQ_T)) {ref}({fs['CLK']},{fs['EN_N']},{vec('D',8)},{vec('Q',8)});")
            lines.append(f"if(TIMED) hc377_timing {ref}_check({fs['CLK']},{fs['EN_N']},{vec('D',8)},reset_n && power_good);")
        elif kind in ("SN74HC08","SN74HC32"):
            op='&' if kind=="SN74HC08" else '|'
            for i in range(4):
                if f'Y{i}' in fs:lines.append(f"assign #GATE_T {fs[f'Y{i}']} = {fs[f'A{i}']} {op} {fs[f'B{i}']};")
        elif kind=="SN74HC04":
            for i in range(6):
                if f'Y{i}' in fs:lines.append(f"assign #INV_T {fs[f'Y{i}']} = ~{fs[f'A{i}']};")
        elif kind=="SN74HC125":
            for i in range(4):
                if f'Y{i}' in fs:lines.append(f"assign #BUF_T {fs[f'Y{i}']} = ({fs[f'OE{i}_N']}) ? 1'bz : {fs[f'A{i}']};")
    for ref,pin,n in inputs:
        if len(drivers.get(n,[]))!=1:raise ValueError(f"Driver count at {ref}/{pin}: {n}")
    for n,items in drivers.items():
        if len(items)!=1:raise ValueError("Multiple drivers "+n)
    outputs={"READY":"ready","DONE":"done","REQUEST":"request","WRITE_ENABLE":"write_enable"}
    outputs.update({f"ADDR_{i}":f"address[{i}]" for i in range(16)})
    outputs.update({f"WDATA_{i}":f"write_data[{i}]" for i in range(8)})
    outputs.update({f"RDATA_{i}":f"read_data[{i}]" for i in range(8)})
    outputs.update({f"P_{i}":f"phase[{i}]" for i in range(6)})
    for n,value in outputs.items():lines.append(f"assign {value}={sig(n)};")
    lines.append('endmodule');destination.write_text("\n".join(lines)+"\n")
    return actual,fanout


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=definitions();parts,gates=design(defs);rows=emit_schematic(defs,parts)
    (OUT/"package-functions.json").write_text(json.dumps(defs,indent=2)+"\n")
    (OUT/"design.json").write_text(json.dumps({"iteration":"NET-03","parts":parts,"gates":gates},indent=2)+"\n")
    command=["kicad-cli","sch","export","netlist","--format","kicadxml","-o",str(VERIFY/"transaction_bank.xml"),str(OUT/"transaction_bank.kicad_sch")]
    exported=subprocess.run(command,capture_output=True,text=True,timeout=60)
    if exported.returncode:raise RuntimeError(exported.stdout+exported.stderr)
    actual,fanout=convert(VERIFY/"transaction_bank.xml",defs,OUT/"transaction_bank_netlist.sv")
    failures=[]
    for r in rows:
        found=actual.get((r["reference"],r["pin"]))
        if r["net"]=="NC":
            if found and not found.startswith("unconnected-"):failures.append(r)
        elif found!=r["net"]:failures.append({"expected":r,"actual":found})
    loads=[{"net":n,"loads":len(v),"pins":v,"input_cap_budget_pf":10*len(v)} for n,v in fanout.items() if n not in ("+5V","GND")]
    overloaded=[n for n in loads if n["loads"]>4]
    if overloaded:failures+=overloaded
    (VERIFY/"fanout.json").write_text(json.dumps({"assumption":"10 pF per input; 10 pF routing reserve up to 50 pF output model; layout not measured","nets":sorted(loads,key=lambda r:(-r['loads'],r['net']))},indent=2)+"\n")
    subprocess.run(["kicad-cli","sch","export","pdf","-o",str(VERIFY/"transaction_bank.pdf"),str(OUT/"transaction_bank.kicad_sch")],check=True,capture_output=True,text=True)
    report={"date":"2026-11-25","kicad":subprocess.check_output(["kicad-cli","version"],text=True).strip(),"command":command,
        "components":len(parts),"pins":len(rows),"no_connects":sum(r['net']=='NC' for r in rows),"max_signal_input_loads":max(n['loads'] for n in loads),
        "stdout":exported.stdout,"stderr":exported.stderr,"failures":failures,"scope":"Pin graph, functional model and capacitive budget. Not ERC/DRC, MTBF or board electrical approval."}
    (VERIFY/"schematic-check.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report),flush=True);return int(bool(failures))


if __name__=="__main__":raise SystemExit(main())
