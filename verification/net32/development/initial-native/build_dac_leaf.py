"""NET32 standalone experimental DAC leaf. Never regenerates NET30 inputs."""
import csv
import hashlib
import json
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET
from build_cpu_global import KICAD
from limited_process import run_limited

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/vga_dac_experiment'
VERIFY=ROOT/'verification/net32/native'
NAME='vga_dac_experiment'
BASE='793d391819712b85bae46fd2d6e9f9d9092b21c7'

def uid(name):return str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net32/'+name))
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n',newline='\n')

def configuration():
    contract=json.loads((ROOT/'engineering/net31/dac_contract.json').read_text())
    pins={}
    for pin,name in contract['facts']['pinout'].items():
        kind=('no_connect' if name=='NC' else 'power_in' if name in ('AVDD','DVDD','ACOM','DCOM') else
              'output' if name in ('IOUTA','IOUTB') else 'input' if name.startswith('DB') or name in ('CLOCK','SLEEP','REFLO') else 'passive')
        pins[pin]={'name':name,'type':kind}
    defs={'AD9760ARUZ':{'pins':pins,'datasheet':contract['source']['url'],'source_revision':'B; transcription, not local PDF'},
          'R':{'pins':{'1':{'name':'1','type':'passive'},'2':{'name':'2','type':'passive'}},'datasheet':''},
          'C':{'pins':{'1':{'name':'1','type':'passive'},'2':{'name':'2','type':'passive'}},'datasheet':''}}
    parts=[]
    def add(ref,kind,value,nets,x,y,role):
        assert set(nets)==set(defs[kind]['pins'])
        parts.append({'reference':ref,'part':kind,'value':value,'nets':nets,'x':x,'y':y,'role':role})
    for index,color in enumerate('RGB'):
        x=60+130*index
        fs={**{f'DB{bit}':f'{color}_DB_{bit}' for bit in range(10)},
            'AVDD':'DAC_VDD','DVDD':'DAC_VDD','ACOM':'GND','DCOM':'GND','SLEEP':'GND','REFLO':'GND',
            'REFIO':color+'_REFIO','FSADJ':color+'_FSADJ','COMP1':color+'_COMP1','COMP2':color+'_COMP2',
            'IOUTB':'GND','IOUTA':color+'_ANALOG','CLOCK':'DAC_CLOCK'}
        add('U'+str(index+1),'AD9760ARUZ','AD9760ARUZ',
            {pin:fs.get(spec['name']) for pin,spec in pins.items()},x,65,'experimental channel '+color)
        caps=[('DAC_VDD','GND','digital supply'),('DAC_VDD','GND','analog supply'),
              (color+'_REFIO','GND','internal reference'),(color+'_COMP1','DAC_VDD','COMP1 to AVDD'),
              (color+'_COMP2','GND','COMP2 to ACOM')]
        for ci,(a,b,role) in enumerate(caps):
            add('C'+str(index*5+ci+1),'C','100nF',{'1':a,'2':b},x-30+(ci%3)*30,120+(ci//3)*20,role)
        add('R'+str(index*2+1),'R','2.32k',{'1':color+'_FSADJ','2':'GND'},x-20,175,
            '0.1 percent diagnostic RSET; deliberately not calibrated final white')
        add('R'+str(index*2+2),'R','75',{'1':color+'_ANALOG','2':'GND'},x+20,175,
            '1 percent local shunt; monitor external; not series termination')
    return defs,parts

def symbol(kind,spec):
    loc={}
    if kind=='AD9760ARUZ':
        for n in range(1,29):
            left=n<=14;row=n-1 if left else 28-n
            loc[str(n)]=(-17.78 if left else 17.78,(6.5-row)*2.54,0 if left else 180)
        body='(rectangle (start -12.7 19.05) (end 12.7 -19.05) (stroke (width 0.254) (type default)) (fill (type background)))'
    else:
        loc={'1':(-5.08,0,0),'2':(5.08,0,180)}
        body=('(rectangle (start -2.54 1.27) (end 2.54 -1.27) (stroke (width 0.254) (type default)) (fill (type none)))' if kind=='R' else
              '(polyline (pts (xy -1 2) (xy -1 -2)) (stroke (width 0.35) (type default)) (fill (type none))) (polyline (pts (xy 1 2) (xy 1 -2)) (stroke (width 0.35) (type default)) (fill (type none)))')
    ref='U' if kind=='AD9760ARUZ' else kind
    text=f'(symbol "NET32:{kind}" (pin_names (offset 0.508)) (in_bom yes) (on_board yes) (property "Reference" "{ref}" (at 0 25 0) (effects (font (size 1 1)))) (property "Value" "{kind}" (at 0 22 0) (effects (font (size 1 1)))) (property "Datasheet" {json.dumps(spec["datasheet"])} (at 0 0 0) (effects (font (size 1 1)) hide)) (symbol "{kind}_0_1" {body}) (symbol "{kind}_1_1" '
    for pin,s in spec['pins'].items():
        x,y,angle=loc[pin]
        text+=f'(pin {s["type"]} line (at {x:.3f} {y:.3f} {angle}) (length {5.08 if ref=="U" else 2.54}) (name "{s["name"]}" (effects (font (size 1 1)))) (number "{pin}" (effects (font (size 1 1)))))'
    return text+'))',loc

def emit(defs,parts):
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    prepared={kind:symbol(kind,spec) for kind,spec in defs.items()};sheet=uid('sheet')
    (OUT/'dac_packages.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor) '+' '.join(v[0].replace('(symbol "NET32:','(symbol "') for v in prepared.values())+')\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "NET32") (type "KiCad") (uri "${KIPRJMOD}/dac_packages.kicad_sym") (options "") (descr "Experimental DAC leaf, not production")))\n')
    save(OUT/(NAME+'.kicad_pro'),{'meta':{'filename':NAME+'.kicad_pro','version':1}})
    lines=[f'(kicad_sch (version 20230121) (generator eeschema) (uuid {sheet}) (paper "A3")',
        '(title_block (title "ISA-1 standalone DAC experiment - no connector or protection") (date "2026-11-27") (rev "NET32") (comment 1 "DIAGNOSTIC RSET - UNCALIBRATED WHITE - NOT FOR PRODUCTION"))',
        '(lib_symbols '+' '.join(v[0] for v in prepared.values())+')'];rows=[]
    for p in parts:
        ref,kind,x,y=p['reference'],p['part'],p['x'],p['y'];height=25 if ref.startswith('U') else 7
        props=f'(property "Reference" "{ref}" (at {x} {y-height} 0) (effects (font (size 1 1)))) (property "Value" "{p["value"]}" (at {x} {y-height+2.54} 0) (effects (font (size 1 1))))'
        pin_ids=' '.join(f'(pin "{pin}" (uuid {uid(ref+"/"+pin)}))' for pin in p['nets'])
        lines.append(f'(symbol (lib_id "NET32:{kind}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (uuid {uid(ref)}) {props} {pin_ids} (instances (project "{NAME}" (path "/{sheet}" (reference "{ref}") (unit 1)))))')
        for pin,net in p['nets'].items():
            dx,dy,angle=prepared[kind][1][pin];px,py=x+dx,y-dy
            rows.append({'reference':ref,'part':kind,'pin':pin,'function':defs[kind]['pins'][pin]['name'],'net':net or 'NC'})
            if net is None:lines.append(f'(no_connect (at {px:.3f} {py:.3f}) (uuid {uid(ref+"/nc/"+pin)}))')
            else:lines.append(f'(label "{net}" (at {px:.3f} {py:.3f} 0) (effects (font (size 0.65 0.65)) (justify {"right bottom" if angle==0 else "left bottom"})) (uuid {uid(ref+"/label/"+pin)}))')
    lines+=['(sheet_instances (path "/" (page "1")))',')']
    (OUT/(NAME+'.kicad_sch')).write_text('\n'.join(lines)+'\n')
    with (OUT/'pinmap.csv').open('w',newline='') as target:
        writer=csv.DictWriter(target,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    save(OUT/'package-functions.json',defs)
    save(OUT/'design.json',{'date':'2026-11-27','base_git_commit':BASE,'status':'standalone diagnostic experiment, not integrated or calibrated','parts':parts})

def read_xml(path):
    root=ET.parse(path).getroot();actual={}
    for net in root.findall('./nets/net'):
        for pin in net.findall('node'):
            key=pin.get('ref'),pin.get('pin');assert key not in actual
            actual[key]=net.get('name').removeprefix('/')
    return root,actual

def validate(path,defs,parts):
    root,actual=read_xml(path)
    components={c.get('ref'):c for c in root.findall('./components/comp')}
    assert set(components)=={p['reference'] for p in parts}
    for p in parts:
        ref=p['reference'];assert components[ref].findtext('value')==p['value']
        for pin,net in p['nets'].items():
            if net is None:assert actual.get((ref,pin),'unconnected-').startswith('unconnected-')
            else:assert actual.get((ref,pin))==net,(ref,pin,net,actual.get((ref,pin)))
    return root,actual

def convert_xml(actual,parts):
    lines=['`timescale 1ns/1ps','// XML-derived digital latch projection only; all analog elements excluded.',
        'module net32_dac_leaf(input wire clk,input wire [9:0] r,g,b,output wire [9:0] red,green,blue);']
    for index,color in enumerate('RGB'):
        ref='U'+str(index+1)
        assert actual[(ref,'28')]=='DAC_CLOCK'
        bits=[]
        for bit in range(9,-1,-1):
            pin=str(10-bit);net=actual[(ref,pin)]
            assert net==f'{color}_DB_{bit}'
            bits.append(color.lower()+'['+str(int(net.rsplit('_',1)[1]))+']')
        lines.append('net31_dac_latch '+ref+'(clk,{'+','.join(bits)+'},'+['red','green','blue'][index]+');')
    lines+=['endmodule']
    (OUT/(NAME+'_digital.sv')).write_text('\n'.join(lines)+'\n')

def main():
    defs,parts=configuration();emit(defs,parts)
    commands={}
    for label,args in [('export',['sch','export','netlist','--format','kicadxml','-o',str(VERIFY/(NAME+'.xml'))]),
                       ('erc',['sch','erc','--format','json','-o',str(VERIFY/'erc.json')]),
                       ('svg',['sch','export','svg','-o',str(VERIFY/'svg')])]:
        commands[label]=run_limited([KICAD,*args,str(OUT/(NAME+'.kicad_sch'))],ROOT,timeout=120,memory_mb=2048,cpu_seconds=90,output_mb=4)
        save(VERIFY/'commands.json',commands)
        assert commands[label]['exit']==0 and not commands[label]['wall_timeout'],commands[label]
    root,actual=validate(VERIFY/(NAME+'.xml'),defs,parts);convert_xml(actual,parts)
    erc=json.loads((VERIFY/'erc.json').read_text())
    violations=[v for sheet in erc['sheets'] for v in sheet['violations']]
    sources=['tools/build_dac_leaf.py','tools/build_cpu_global.py','tools/limited_process.py','engineering/net31/dac_contract.json']
    report={'date':'2026-11-27','base_git_commit':BASE,'components':len(parts),'dac_packages':3,
        'pins':sum(len(p['nets']) for p in parts),'no_connects':15,
        'all_component_values_and_pins_equal_xml':True,'erc_unwaived_count':len(violations),
        'erc_approved':False,'footprints_assigned':False,'native_integrated_into_net30':False,
        'sources':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in sources],
        'failures':[],'production_released':False}
    save(VERIFY/'schematic-check.json',report)
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()
