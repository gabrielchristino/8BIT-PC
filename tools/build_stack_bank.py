"""NET-02: native KiCad -> exported XML -> pin-connected simulation model.

The package pin functions are transcribed from TI datasheets (not guessed from
symbol graphics). No footprint, ERC/DRC, or timing approval is implied.
"""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"hardware/stack_bank"
VERIFY = ROOT/"verification/net02"


def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "isa1/net02/"+name))


def definitions():
    result = {}
    def part(name, filename, ins, outs, vcc, gnd):
        pins = {str(p): {"name": n, "type": "input"} for p,n in ins.items()}
        pins.update({str(p): {"name": n,"type": "output"} for p,n in outs.items()})
        pins[str(vcc)]={"name":"VCC","type":"power_in"}
        pins[str(gnd)]={"name":"GND","type":"power_in"}
        result[name]={"datasheet":"https://www.ti.com/lit/ds/symlink/"+filename,
                      "pins":pins,"source":"TI package pin configuration; channels renamed to zero-based indices"}
    part("SN74HC273","sn74hc273.pdf",
         {1:"CLR_N",11:"CLK",**{p:f"D{i}" for i,p in enumerate([3,4,7,8,13,14,17,18])}},
         {p:f"Q{i}" for i,p in enumerate([2,5,6,9,12,15,16,19])},20,10)
    part("CD74HC283","cd74hc283.pdf",
         {7:"CIN",**{p:f"A{i}" for i,p in enumerate([5,3,14,12])},
          **{p:f"B{i}" for i,p in enumerate([6,2,15,11])}},
         {9:"COUT",**{p:f"S{i}" for i,p in enumerate([4,1,13,10])}},16,8)
    part("SN74HC157","sn74hc157.pdf",
         {1:"SELECT",15:"G_N",**{p:f"A{i}" for i,p in enumerate([2,5,11,14])},
          **{p:f"B{i}" for i,p in enumerate([3,6,10,13])}},
         {p:f"Y{i}" for i,p in enumerate([4,7,9,12])},16,8)
    part("SN74HC04","sn74hc04.pdf",
         {p:f"A{i}" for i,p in enumerate([1,3,5,9,11,13])},
         {p:f"Y{i}" for i,p in enumerate([2,4,6,8,10,12])},14,7)
    part("SN74HC125","sn74hc125.pdf",
         {**{p:f"A{i}" for i,p in enumerate([2,5,9,12])},
          **{p:f"OE{i}_N" for i,p in enumerate([1,4,10,13])}},
         {p:f"Y{i}" for i,p in enumerate([3,6,8,11])},14,7)
    result["C"]={"datasheet":"", "pins":{"1":{"name":"1","type":"passive"},
                      "2":{"name":"2","type":"passive"}},"source":"Proposed 100nF bypass; not electrically sized"}
    return result


def design(defs):
    parts=[]
    def add(ref,kind,x,y,functions):
        mapping={str(p):functions.get(v["name"]) for p,v in defs[kind]["pins"].items()}
        if kind!="C":
            for p,v in defs[kind]["pins"].items():
                if v["name"]=="VCC":mapping[p]="+5V"
                if v["name"]=="GND":mapping[p]="GND"
        parts.append({"reference":ref,"part":kind,"x":x,"y":y,"nets":mapping})
    for bank in range(2):
        fs={"CLR_N":"RESET_N","CLK":"CLK"}
        for i in range(8):
            bit=bank*8+i
            fs[f"D{i}"]=f"D_{bit}"
            fs[f"Q{i}"]=f"SP_{bit}" if bit!=15 else "SP_15_N"
        add(f"U{bank+1}","SN74HC273",72+bank*90,57,fs)
    for n in range(4):
        fs={"SELECT":"UPDATE","G_N":"GND"}
        for i in range(4):
            bit=4*n+i
            fs[f"A{i}"]=f"SP_{bit}" if bit!=15 else "SP_15_N"
            fs[f"B{i}"]=f"SUM_{bit}" if bit!=15 else "SUM_15_N"
            fs[f"Y{i}"]=f"D_{bit}"
        add(f"U{n+3}","SN74HC157",62+90*n,137,fs)
        fs={"CIN":"GND" if n==0 else f"CARRY_{n}","COUT":f"CARRY_{n+1}" if n<3 else None}
        for i in range(4):
            bit=4*n+i
            fs[f"A{i}"]=f"SP_{bit}"
            fs[f"B{i}"]="+5V" if bit==0 else f"DOWN_{n}"
            fs[f"S{i}"]=f"SUM_{bit}"
        add(f"U{n+7}","CD74HC283",62+90*n,220,fs)
    add("U11","SN74HC04",282,57,
        {"A0":"SP_15_N","Y0":"SP_15","A1":"SUM_15","Y1":"SUM_15_N",
         **{f"A{i}":"GND" for i in range(2,6)}})
    add("U12","SN74HC125",350,57,
        {**{f"A{i}":"DOWN" for i in range(4)},**{f"Y{i}":f"DOWN_{i}" for i in range(4)},
         **{f"OE{i}_N":"GND" for i in range(4)}})
    for i,chip in enumerate(list(parts),1):
        add(f"C{i}","C",chip["x"]+32,chip["y"]-20,{"1":"+5V","2":"GND"})
    return parts


def symbol(kind,spec):
    locations={}
    # Rectangular complete-package symbols keep every physical pin explicit.
    for typ,x,angle in (("input",-17.78,0),("output",17.78,180)):
        entries=[(p,v) for p,v in spec["pins"].items() if v["type"]==typ]
        for i,(p,v) in enumerate(entries):locations[p]=(x,(len(entries)-1)*1.27-i*2.54,angle)
    if kind=="C":locations={"1":(0,3.81,270),"2":(0,-3.81,90)}
    else:
        for p,v in spec["pins"].items():
            if v["name"]=="VCC":locations[p]=(0,20.32,270)
            if v["name"]=="GND":locations[p]=(0,-20.32,90)
    ref="C" if kind=="C" else "U"
    body=(f'(rectangle (start -12.7 17.78) (end 12.7 -17.78) (stroke (width 0.254) (type default)) (fill (type background)))'
          if kind!="C" else '(polyline (pts (xy -2 1) (xy 2 1)) (stroke (width 0.4) (type default)) (fill (type none))) '
          '(polyline (pts (xy -2 -1) (xy 2 -1)) (stroke (width 0.4) (type default)) (fill (type none)))')
    text=f'(symbol "NET02:{kind}" (pin_names (offset 0.508)) (in_bom yes) (on_board yes) '
    text+=f'(property "Reference" "{ref}" (at 0 24 0) (effects (font (size 1.27 1.27)))) '
    text+=f'(property "Value" "{kind}" (at 0 22 0) (effects (font (size 1.27 1.27)))) '
    text+=f'(property "Datasheet" {json.dumps(spec["datasheet"])} (at 0 0 0) (effects (font (size 1 1)) hide)) '
    text+=f'(symbol "{kind}_0_1" {body}) (symbol "{kind}_1_1" '
    for p,v in spec["pins"].items():
        x,y,angle=locations[p]
        length=5.08 if kind!="C" else 2.81
        text+=f'(pin {v["type"]} line (at {x} {y} {angle}) (length {length}) '
        text+=f'(name "{v["name"]}" (effects (font (size 1 1)))) (number "{p}" (effects (font (size 1 1))))) '
    return text+'))', locations


def emit_schematic(defs,parts):
    prepared={k:symbol(k,v) for k,v in defs.items()}
    sheet=uid("sheet")
    lines=[f'(kicad_sch (version 20230121) (generator eeschema) (uuid {sheet}) (paper "A3")',
       '(title_block (title "ISA-1 SP: registrador e soma compartilhada") (rev "NET-02") (date "2026-11-25") (comment 1 "PARTIAL: controller, guards and bus latch external. NOT FOR PRODUCTION"))',
       '(lib_symbols '+" ".join(v[0] for v in prepared.values())+')']
    rows=[]
    for part in parts:
        ref,kind,x,y=part["reference"],part["part"],part["x"],part["y"]
        value="100nF" if kind=="C" else kind
        atx,aty=(x+5,y-2) if kind=="C" else (x,y-25.4)
        properties=f'(property "Reference" "{ref}" (at {atx} {aty} 0) (effects (font (size 1 1)))) '
        properties+=f'(property "Value" "{value}" (at {atx} {aty+2.54} 0) (effects (font (size 1 1)))) '
        pp=" ".join(f'(pin "{p}" (uuid {uid(ref+"/"+p)}))' for p in part["nets"])
        lines.append(f'(symbol (lib_id "NET02:{kind}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) '
           f'(uuid {uid(ref)}) {properties}{pp} (instances (project "stack_bank" (path "/{sheet}" (reference "{ref}") (unit 1)))))')
        for pin,net in part["nets"].items():
            px,py,angle=prepared[kind][1][pin];px+=x;py=y-py
            rows.append({"reference":ref,"part":kind,"pin":pin,"function":defs[kind]["pins"][pin]["name"],"net":net or "NC"})
            if net is None:
                lines.append(f'(no_connect (at {px} {py}) (uuid {uid(ref+"/nc/"+pin)}))')
            else:
                justify="right bottom" if angle==0 else "left bottom"
                lines.append(f'(label "{net}" (at {px} {py} 0) (effects (font (size 0.9 0.9)) (justify {justify})) (uuid {uid(ref+"/label/"+pin)}))')
    for y,text in [(17,"SP empty = 8000h; Q15 inverted. Common clock. U12 buffers DOWN per nibble."),
                   (95,"Feedback muxes: UPDATE=0 hold, UPDATE=1 store encoded SUM."),
                   (179,"Four adders: B=0001h when DOWN=0, FFFFh when DOWN=1; C_IN=0."),
                   (264,"External: UPDATE pulse only after confirmed stack transaction; latch bus address before WAIT.")]:
        lines.append(f'(text "{text}" (at 17 {y} 0) (effects (font (size 1.4 1.4)) (justify left)) (uuid {uid(text)}))')
    lines+=['(sheet_instances (path "/" (page "1")))',')']
    (OUT/"stack_bank.kicad_sch").write_text("\n".join(lines)+"\n")
    with (OUT/"pinmap.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    return rows


def convert(xml_path,defs,destination):
    root=ET.parse(xml_path).getroot()
    actual={}
    nets=set()
    for node in root.findall("./nets/net"):
        name=node.get("name").removeprefix("/")
        nets.add(name)
        for pin in node.findall("node"):
            key=(pin.get("ref"),pin.get("pin"))
            if key in actual:raise ValueError("Pin in multiple nets: "+str(key))
            actual[key]=name
    def signal(net):
        if net=="+5V":return "1'b1"
        if net=="GND":return "1'b0"
        return "n_"+re.sub(r"[^A-Za-z0-9_]","_",net)
    names=[signal(n) for n in nets if n not in ("+5V","GND")]
    if len(names)!=len(set(names)):raise ValueError("Net name collision")
    lines=['`timescale 1ns/1ps', '// GENERATED FROM KiCad-exported XML. Do not edit.',
           'module stack_bank_netlist #(parameter integer TIMED=0)(input wire clk,reset_n,update,down, output wire [15:0] sp,sum);',
           'localparam CQ_T=TIMED?40:0, SUM_T=TIMED?58:0, CARRY_T=TIMED?49:0, MUX_T=TIMED?38:0, INV_T=TIMED?24:0, BUF_T=TIMED?36:0;']
    lines += ["wire "+name+";" for name in sorted(names)]
    external={"CLK":"clk","RESET_N":"reset_n","UPDATE":"update","DOWN":"down"}
    drivers={n:["external"] for n in [*external,"+5V","GND"]}
    inputs=[]
    for n,value in external.items():lines.append(f"assign {signal(n)}={value};")
    components=[]
    for comp in root.findall("./components/comp"):
        ref=comp.get("ref");value=comp.findtext("value")
        kind="C" if ref.startswith("C") else value
        if kind not in defs:raise ValueError("Unsupported component "+kind)
        funcs={}
        for pin,spec in defs[kind]["pins"].items():
            net=actual.get((ref,pin))
            if spec["type"] in ("input","power_in") and (not net or net.startswith("unconnected-")):
                raise ValueError(f"Floating input {ref}/{pin}")
            if spec["name"] in ("VCC","GND") and net!={"VCC":"+5V","GND":"GND"}[spec["name"]]:
                raise ValueError("Wrong power connection "+ref)
            if not net:continue
            funcs[spec["name"]]=signal(net)
            if spec["type"]=="output":drivers.setdefault(net,[]).append(ref+"/"+pin)
            if spec["type"]=="input":inputs.append((ref,pin,net))
        def vec(prefix,n):return '{'+','.join(funcs[f'{prefix}{i}'] for i in reversed(range(n)))+'}'
        if kind=="SN74HC273":
            lines.append(f"hc273_functional #(.T_CQ(CQ_T),.T_CLR(CQ_T),.CHECKS(TIMED)) {ref}(.clk({funcs['CLK']}),.clr_n({funcs['CLR_N']}),.d({vec('D',8)}),.q({vec('Q',8)}));")
        elif kind=="CD74HC283":
            lines.append(f"hc283_functional #(.T_SUM(SUM_T),.T_CARRY(CARRY_T)) {ref}(.a({vec('A',4)}),.b({vec('B',4)}),.cin({funcs['CIN']}),.s({vec('S',4)}),.cout({funcs.get('COUT','')}));")
        elif kind=="SN74HC157":
            lines.append(f"sn74hc157_model #(.T_PD(MUX_T)) {ref}({vec('A',4)},{vec('B',4)},{funcs['SELECT']},{funcs['G_N']},{vec('Y',4)});")
        elif kind=="SN74HC04":
            for i in range(6):
                if f"Y{i}" in funcs:lines.append(f"assign #INV_T {funcs[f'Y{i}']}=~{funcs[f'A{i}']};")
        elif kind=="SN74HC125":
            for i in range(4):lines.append(f"assign #BUF_T {funcs[f'Y{i}']} = ({funcs[f'OE{i}_N']}) ? 1'bz : {funcs[f'A{i}']};")
        components.append({"reference":ref,"part":kind})
    for ref,pin,net in inputs:
        if len(drivers.get(net,[]))!=1:raise ValueError(f"Missing/multiple drivers at {ref}/{pin}: {net}")
    for net,source in drivers.items():
        if len(source)!=1:raise ValueError("Multiple output drivers: "+net)
    for i in range(16):
        lines.append(f"assign sp[{i}]={signal(f'SP_{i}')};")
        lines.append(f"assign sum[{i}]={signal(f'SUM_{i}')};")
    lines.append('endmodule')
    destination.write_text("\n".join(lines)+"\n")
    return actual,components


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=definitions();parts=design(defs)
    (OUT/"package-functions.json").write_text(json.dumps(defs,indent=2)+"\n")
    (OUT/"design.json").write_text(json.dumps({"iteration":"NET-02","parts":parts},indent=2)+"\n")
    rows=emit_schematic(defs,parts)
    command=["kicad-cli","sch","export","netlist","--format","kicadxml","-o",str(VERIFY/"stack_bank.xml"),str(OUT/"stack_bank.kicad_sch")]
    compiled=subprocess.run(command,capture_output=True,text=True,timeout=60)
    if compiled.returncode:raise RuntimeError(compiled.stdout+compiled.stderr)
    actual,components=convert(VERIFY/"stack_bank.xml",defs,OUT/"stack_bank_netlist.sv")
    failures=[]
    for r in rows:
        found=actual.get((r["reference"],r["pin"]))
        if r["net"]=="NC":
            if found and not found.startswith("unconnected-"):failures.append(r)
        elif found!=r["net"]:failures.append({"expected":r,"actual":found})
    report={"date":"2026-11-25","kicad":subprocess.check_output(["kicad-cli","version"],text=True).strip(),
            "command":command,"stdout":compiled.stdout,"stderr":compiled.stderr,
            "components":len(components),"pins":len(rows),"no_connects":sum(r["net"]=="NC" for r in rows),
            "failures":failures,"scope":"Pin netlist and functional HDL generation; not ERC or timing closure"}
    (VERIFY/"schematic-check.json").write_text(json.dumps(report,indent=2)+"\n")
    subprocess.run(["kicad-cli","sch","export","pdf","-o",str(VERIFY/"stack_bank.pdf"),str(OUT/"stack_bank.kicad_sch")],check=True,capture_output=True,text=True)
    print(json.dumps(report),flush=True)
    return int(bool(failures))


if __name__=="__main__":raise SystemExit(main())
