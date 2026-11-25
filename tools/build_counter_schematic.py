"""Create a self-contained, partial KiCad schematic from verified candidate pin maps.

Run under Ubuntu with the kicad-symbols package. No PCB or production release.
"""
import copy
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hardware/counter_load_candidate"
VERIFY = ROOT / "verification/rev9842"


class Atom(str):
    pass


def parse(text):
    tokens = iter(re.findall(r'"(?:[^"\\]|\\.)*"|[()]|[^\s()]+', text))
    def node(token):
        if token == "(":
            out = []
            for token in tokens:
                if token == ")":
                    return out
                out.append(node(token))
            raise ValueError("Unclosed expression")
        return json.loads(token) if token.startswith('"') else Atom(token)
    return node(next(tokens))


def dump(node):
    if isinstance(node, list):
        return "(" + " ".join(map(dump, node)) + ")"
    return str(node) if isinstance(node, Atom) else json.dumps(node)


def child(node, tag):
    return next(n for n in node if isinstance(n, list) and n[0] == tag)


def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "isa1/rev9842/" + name))


def flatten(symbols, name):
    own = copy.deepcopy(symbols[name])
    base = next((n for n in own if isinstance(n, list) and n[0] == "extends"), None)
    if base:
        inherited = flatten(symbols, base[1])
        overridden = {n[1] for n in own if isinstance(n, list) and n[0] == "property"}
        own += [n for n in inherited[2:] if isinstance(n, list)
                and not (n[0] == "property" and n[1] in overridden)]
        own.remove(base)
    return own


def pins(node):
    for item in node:
        if isinstance(item, list):
            if item[0] == "pin":
                at = child(item, "at")
                yield dict(number=str(child(item, "number")[1]),
                           name=child(item, "name")[1], x=float(at[1]),
                           y=float(at[2]), angle=float(at[3]))
            else:
                yield from pins(item)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    VERIFY.mkdir(parents=True, exist_ok=True)
    library_paths = [Path("/usr/share/kicad/symbols") / (n + ".kicad_sym")
                     for n in ("74xx", "Device")]
    symbols = {}
    for library in library_paths:
        symbols.update({n[1]: n for n in parse(library.read_text())[1:]
                        if isinstance(n, list) and n[0] == "symbol"})
    specs = [("SN74HC191", "74LS191", "sn74hc191.pdf"),
             ("SN74HC157", "74LS157", "sn74hc157.pdf"),
             ("SN74HC377", "74LS377", "sn74hc377.pdf"), ("C", "C", "")]
    prepared = {}
    for part, base, datasheet in specs:
        symbol = flatten(symbols, base)
        symbol[1] = "ISA1:" + part
        symbol = [n for n in symbol if not (isinstance(n, list) and
                  n[0] == "property" and str(n[1]).startswith("ki_"))]
        for item in symbol[2:]:
            if not isinstance(item, list):
                continue
            if item[0] == "symbol":
                item[1] = re.sub(r"^.*(?=_[0-9]+_[0-9]+$)", part, item[1])
            elif item[0] == "property" and item[1] == "Value":
                item[2] = part
            elif item[0] == "property" and item[1] == "Datasheet" and datasheet:
                item[2] = "https://www.ti.com/lit/ds/symlink/" + datasheet
        prepared[part] = symbol
    parts = []
    for i in range(4):
        offset = i * 4
        net = {1:f"PRESET_{offset+1}",2:f"X_{offset+1}",3:f"X_{offset}",
               4:f"CTEN_{i}_N",5:"X_DIR",6:f"X_{offset+2}",7:f"X_{offset+3}",
               8:"GND",9:f"PRESET_{offset+3}",10:f"PRESET_{offset+2}",
               11:"X_LOAD_N",12:f"TERMINAL_{i}" if i<3 else None,
               13:None,14:"CLK",15:f"PRESET_{offset}",16:"+5V"}
        parts.append((f"U{i+1}","SN74HC191",70+i*90,65,net))
        net={1:"SELECT_DATA",8:"GND",15:"GND",16:"+5V"}
        for bit,pa,pb,py in ((0,2,3,4),(1,5,6,7),(2,11,10,9),(3,14,13,12)):
            net[pa]="GND"
            net[pb]=f"SAVED_{offset+bit}"
            net[py]=f"PRESET_{offset+bit}"
        parts.append((f"U{i+7}","SN74HC157",70+i*90,160,net))
    for bank in range(2):
        net={1:"CAPTURE_N",10:"GND",11:"CLK",20:"+5V"}
        for bit,pd,pq in ((0,3,2),(1,4,5),(2,7,6),(3,8,9),
                          (4,13,12),(5,14,15),(6,17,16),(7,18,19)):
            net[pd]=f"EA_{bank*8+bit}"
            net[pq]=f"SAVED_{bank*8+bit}"
        parts.append((f"U{bank+5}","SN74HC377",120+bank*140,245,net))
    for i,(_,_,x,y,_) in enumerate(list(parts)):
        parts.append((f"C{i+1}","C",x+25,y-18,{1:"+5V",2:"GND"}))

    sheet_id=uid("sheet")
    text=[f'(kicad_sch (version 20230121) (generator eeschema) (uuid {sheet_id}) (paper "A3")',
          '(title_block (title "ISA-1 - banco X candidato") (rev "9.8.4.2") (comment 1 "PARTIAL - NOT FOR PRODUCTION"))',
          '(lib_symbols '+" ".join(dump(n) for n in prepared.values())+')']
    rows=[]
    for ref,part,x,y,net in parts:
        pin_list=list(pins(prepared[part]))
        if set(map(int,(p["number"] for p in pin_list))) != set(net):
            raise ValueError(f"Pin mismatch for {ref}")
        value="100nF" if part=="C" else part
        attrs=f'(property "Reference" "{ref}" (at {x-18} {y-22} 0) (effects (font (size 1.27 1.27)))) '
        attrs+=f'(property "Value" "{value}" (at {x-18} {y-19.5} 0) (effects (font (size 1.27 1.27))))'
        if part=="C":
            attrs=f'(property "Reference" "{ref}" (at {x+4} {y-2} 0) (effects (font (size 1 1)))) '
            attrs+=f'(property "Value" "100nF" (at {x+5} {y+1} 0) (effects (font (size 1 1))))'
        pp=" ".join(f'(pin "{p["number"]}" (uuid {uid(ref+"/pin/"+p["number"])}))' for p in pin_list)
        text.append(f'(symbol (lib_id "ISA1:{part}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) '
                    f'(uuid {uid(ref)}) {attrs} {pp} (instances (project "counter_load_bank" '
                    f'(path "/{sheet_id}" (reference "{ref}") (unit 1)))))')
        for pin in pin_list:
            number=int(pin["number"]);px=round(x+pin["x"],4);py=round(y-pin["y"],4)
            name=net[number]
            rows.append(dict(reference=ref,part=part,pin=number,pin_name=pin["name"],
                             net=name or "NC",source="TI datasheet pinout; KiCad graphical symbol"
                             if part!="C" else "Engineering assumption; KiCad capacitor symbol"))
            if name is None:
                text.append(f'(no_connect (at {px} {py}) (uuid {uid(ref+"/nc/"+str(number))}))')
            else:
                justify="right bottom" if pin["x"]<0 else "left bottom"
                text.append(f'(label "{name}" (at {px} {py} 0) (effects (font (size 1 1)) '
                            f'(justify {justify})) (uuid {uid(ref+"/label/"+str(number))}))')
    for title,y in (("ESQUEMA PARCIAL - controle, portas e integracao CPU ainda pendentes",18),
                    ("U1-U4: quatro contadores com clock comum; RCO nao utilizado",30),
                    ("U7-U10: selecao entre valor inicial zero e dados capturados",125),
                    ("U5-U6: captura de EA antes da carga assincrona",210)):
        text.append(f'(text "{title}" (at 20 {y} 0) (effects (font (size 1.5 1.5)) '
                    f'(justify left)) (uuid {uid(title)}))')
    text += ['(sheet_instances (path "/" (page "1")))', ')']
    schematic=OUT/"counter_load_bank.kicad_sch"
    schematic.write_text("\n".join(text)+"\n")
    with (OUT/"pinmap.csv").open("w",newline="") as output:
        writer=csv.DictWriter(output,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    export=VERIFY/"counter_load_bank.xml"
    command=["kicad-cli","sch","export","netlist","--format","kicadxml","-o",str(export),str(schematic)]
    result=subprocess.run(command,capture_output=True,text=True,timeout=60)
    if result.returncode:
        raise RuntimeError(result.stdout+result.stderr)
    actual={}
    for net in ET.parse(export).getroot().findall("./nets/net"):
        for pin in net.findall("node"):
            actual[(pin.get("ref"),int(pin.get("pin")))]=net.get("name")
    failures=[]
    for row in rows:
        found=actual.get((row["reference"],row["pin"]))
        if found and found.startswith("/"):
            found=found[1:]  # KiCad qualifies local labels with the root sheet path.
        if row["net"]!="NC" and found!=row["net"]:
            failures.append(dict(expected=row,actual=found))
        if row["net"]=="NC" and found and not found.startswith("unconnected-"):
            failures.append(dict(expected=row,actual=found))
    report={"kicad":subprocess.check_output(["kicad-cli","version"],text=True).strip(),
            "components":len(parts),"pins":len(rows),"non_connected_pins":sum(r["net"]=="NC" for r in rows),
            "library_sources":[{"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in library_paths],
            "export_stdout":result.stdout,"export_stderr":result.stderr,"failures":failures,
            "scope":"Partial bank only; reference controller is NOT physically mapped; no ERC/PCB release"}
    (VERIFY/"schematic-check.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="failures"},indent=2))
    print(json.dumps({"failure_count":len(failures),"first_failures":failures[:3]}))
    return int(bool(failures))


if __name__=="__main__":
    raise SystemExit(main())
