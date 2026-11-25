"""NET-10 joins accepted CPU package graphs and budgets inter-block fanout.

Main configuration only (synchronous X); no behavioral CPU arithmetic/FSM.
Separate artifacts: prior stages and alternative HC191 remain unchanged.
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
from build_microcode_bank import package_symbol
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/cpu_global';VERIFY=ROOT/'verification/net10'
KICAD='/home/gabri/.local/opt/isa1-kicad-10.0.8/squashfs-root/usr/bin/kicad-cli'


def uid(n):return str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net10/'+n))
def vec(n,k):return [f'{n}_{i}' for i in range(k)]
CW=vec('CW',32)


def configuration():
    common={'clk':'CLK_EXEC','reset_n':'RESET_N','power_good':'POWER_GOOD'}
    return [
      ('sp','stack_bank','stack_bank_netlist.sv',{'clk':'CLK','reset_n':'SAFE_CORE','update':'SP_UPDATE','down':'SP_DOWN','sp':vec('SP',16),'sum':vec('STACK_SUM',16)}),
      ('bus','transaction_bank','transaction_bank_netlist.sv',{'clk':'CLK','reset_n':'RESET_N','power_good':'POWER_GOOD','start':'BUS_START','issue_write':'WRITE_MODE','ack_raw':'ACKNOWLEDGE','issue_address':vec('ADDRESS_MUX',16),'issue_data':vec('VALUE',8),'bus_rdata':vec('READ_DATA',8),'ready':'BUS_READY','done':'BUS_DONE','request':'REQUEST','write_enable':'WRITE_ENABLE','address':vec('ADDRESS',16),'write_data':vec('WRITE_DATA',8),'read_data':vec('MDR',8)}),
      ('micro','microcode_bank','microcode_bank_netlist.sv',{'clk':'CLK','reset_n':'RESET_N','power_good':'POWER_GOOD','advance_req':'ADVANCE_REQ','execute_pulse':'EXECUTE_PULSE','opcode':vec('MDR',8),'control_ready':'CONTROL_READY','execute_clk':'CLK_EXEC','dispatch':'DISPATCH','fetch':'FETCH','step':vec('STEP',4),'ir':vec('IR',8),'rom_address':vec('CONTROL_ADDRESS',13),'control_word':CW,'sp_update':'SP_UPDATE','sp_down':'SP_DOWN','addr_n':vec('ADDR_N',8),'src_n':vec('SRC_N',8),'dst_n':vec('DST_N',8),'pc_n':vec('PC_N',8),'mem_n':vec('MEM_N',4),'sp_n':vec('SP_N',4),'x_n':vec('X_N',4),'flags_n':vec('FLAGS_N',4),'alu_n':vec('ALU_N',16)}),
      ('alu','alu_bank','alu_bank_netlist.sv',{'a':vec('A',8),'b':vec('B',8),'op':CW[18:22],'carry_in':'C','result':vec('ALU',8),'carry_out':'ALU_CARRY'}),
      ('registers','register_bank','register_bank_netlist.sv',{**common,'exec_enable':'EXEC_ACCEPT','src':CW[3:6],'dst_n':vec('DST_N',8),'flags_n':vec('FLAGS_N',4),'pc':vec('PC',16),'mdr':vec('MDR',8),'alu_result':vec('ALU',8),'alu_carry':'ALU_CARRY','a':vec('A',8),'b':vec('B',8),'value':vec('VALUE',8),'ea':vec('EA',16),'z':'Z','c':'C'}),
      ('address','address_bank','address_bank_netlist.sv',{**common,'exec_enable':'EXEC_ACCEPT','addr_sel':CW[:3],'pc_n':vec('PC_N',8),'z':'Z','ea':vec('EA',16),'x':vec('X',16),'sp':vec('SP',16),'stack_sum':vec('STACK_SUM',16),'pc':vec('PC',16),'address':vec('ADDRESS_MUX',16)}),
      ('execution','cpu_execution_glue','execution_bank_net09.sv',{**common,'run':'RUN','control_ready':'CONTROL_READY','x_ready':'+5V','x_done':'GND','use_x':'GND','boot':'BOOT','bus_ready':'BUS_READY','bus_done':'BUS_DONE','dispatch':'DISPATCH','cw_end':CW[24],'cw_halt':CW[25],'ir':vec('IR',8),'addr_n':vec('ADDR_N',8),'mem_n':vec('MEM_N',4),'x_n':vec('X_N',4),'sp':vec('SP',16),'execute_pulse':'EXECUTE_PULSE','advance_req':'ADVANCE_REQ','bus_start':'BUS_START','stack_checked':'STACK_CHECKED','halted':'HALTED','retired':'RETIRED','fault':vec('FAULT',2),'execute_accept':'EXEC_ACCEPT','write_mode':'WRITE_MODE'}),
      ('x','x_register_bank','x_register_bank_netlist.sv',{**common,'exec_enable':'EXEC_ACCEPT','x_n':vec('X_N',4),'ea':vec('EA',16),'x':vec('X',16)})]


def sig(n):return "1'b1" if n=='+5V' else "1'b0" if n=='GND' else 'n_'+re.sub(r'[^A-Za-z0-9_]','_',n)


def merge():
    parts=[];defs={};origins=[];refs={};ic=0;cap=0
    for group,directory,hdl,bindings in configuration():
        folder=ROOT/'hardware'/directory
        schema=json.loads((folder/'package-functions.json').read_text());data=json.loads((folder/'design.json').read_text())
        for k,s in schema.items():
            if k in defs and defs[k]['pins']!=s['pins']:raise ValueError('Inconsistent package '+k)
            defs[k]=s
        netnames={sig(n):n for p in data['parts'] for n in p['nets'].values() if n}
        aliases={}
        def resolve(port):
            m=re.fullmatch(r'(\w+)(?:\[(\d+)\])?',port)
            if not m or m[1] not in bindings:return None
            value=bindings[m[1]]
            if m[2] is not None:
                if not isinstance(value,list):raise ValueError('Scalar used as bus '+port)
                return value[int(m[2])]
            if isinstance(value,list):raise ValueError('Bus used as scalar '+port)
            return value
        for line in (folder/hdl).read_text().splitlines():
            m=re.fullmatch(r'assign\s+(n_\w+)\s*=\s*(\w+(?:\[\d+\])?)\s*;',line)
            if m and m[1] in netnames:
                n=resolve(m[2])
                if n is not None:aliases[netnames[m[1]]]=n
            m=re.fullmatch(r'assign\s+(\w+(?:\[\d+\])?)\s*=\s*(n_\w+)\s*;',line)
            if m and m[2] in netnames:
                n=resolve(m[1])
                if n is not None:aliases[netnames[m[2]]]=n
        # The wrapper's reset_n && power_good is this existing physical gate.
        if group=='execution':aliases['SAFE']='SAFE_CORE'
        for original in data['parts']:
            p=copy.deepcopy(original);old=p['reference'];kind=p['part']
            if kind=='C':cap+=1;ref=f'C{cap}'
            else:ic+=1;ref=f'U{ic}'
            p.update(reference=ref,group=group,origin_reference=old,origin_directory=directory)
            refs[group+'/'+old]=ref
            for pin,n in p['nets'].items():
                if n is not None:p['nets'][pin]=n if n in ('+5V','GND') else aliases.get(n,group+'__'+n)
            parts.append(p)
        for name in ('design.json','package-functions.json',hdl):
            path=folder/name;origins.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    return defs,parts,origins,refs


def loads_of(parts,defs):
    result={}
    for p in parts:
        for pin,n in p['nets'].items():
            if defs[p['part']]['pins'][pin]['type']=='input' and n not in ('GND','+5V'):
                result.setdefault(n,[]).append((p,pin))
    return result


def mark_unused_outputs(parts,defs):
    public=set(['REQUEST','WRITE_ENABLE','RETIRED','Z','C','HALTED',*vec('ADDRESS',16),*vec('WRITE_DATA',8),*vec('PC',16),*vec('SP',16),*vec('X',16),*vec('A',8),*vec('B',8),*vec('FAULT',2),*vec('CONTROL_ADDRESS',13),*vec('CW',32)])
    loads=loads_of(parts,defs);removed=[]
    for p in parts:
        for pin,n in list(p['nets'].items()):
            if n and defs[p['part']]['pins'][pin]['type']=='output' and not loads.get(n) and n not in public:
                removed.append({'reference':p['reference'],'pin':pin,'former_net':n})
                p.setdefault('unused_output_observers',{})[pin]=n;p['nets'][pin]=None
    return removed


def distribute(parts,defs):
    initial=loads_of(parts,defs)
    overloaded=[{'net':n,'loads':len(v),'pins':[p['reference']+'/'+pin for p,pin in v]} for n,v in initial.items() if len(v)>4]
    buffers=[];ic=max(int(p['reference'][1:]) for p in parts if p['part']!='C');cap=max(int(p['reference'][1:]) for p in parts if p['part']=='C')
    while True:
        over=next(((n,v) for n,v in loads_of(parts,defs).items() if len(v)>4),None)
        if over is None:break
        n,targets=over
        for start in range(0,len(targets),4):
            if not buffers or buffers[-1]['used']==4:
                ic+=1;cap+=1;kind='SN74HC125';pins={}
                for pin,spec in defs[kind]['pins'].items():
                    name=spec['name'];pins[pin]='+5V' if name=='VCC' else 'GND' if name=='GND' or spec['type']=='input' else None
                p={'reference':f'U{ic}','part':kind,'nets':pins,'group':'distribution','origin_reference':None,'origin_directory':None}
                parts.append(p);parts.append({'reference':f'C{cap}','part':'C','nets':{'1':'+5V','2':'GND'},'group':'distribution','origin_reference':None,'origin_directory':None})
                buffers.append({'part':p,'used':0})
            b=buffers[-1];ch=b['used'];b['used']+=1;out=f'GLOBAL_BUF_{len(buffers)}_{ch}'
            for pin,spec in defs['SN74HC125']['pins'].items():
                if spec['name']==f'A{ch}':b['part']['nets'][pin]=n
                if spec['name']==f'Y{ch}':b['part']['nets'][pin]=out
            for p,pin in targets[start:start+4]:p['nets'][pin]=out
    final=loads_of(parts,defs)
    report={'before_overloaded_nets':overloaded,'added_buffer_packages':len(buffers),'max_input_loads':max(map(len,final.values())),
      'scope':'All CPU inter-block input pins, no PCB extraction or system peripherals yet','nets':[{'net':n,'loads':len(v),'pins':[p['reference']+'/'+pin for p,pin in v]} for n,v in sorted(final.items())]}
    return report


def emit(defs,parts):
    prepared={k:package_symbol(k,v) for k,v in defs.items()}
    prepared={k:(text.replace('NET04:','NET10:'),loc) for k,(text,loc) in prepared.items()}
    library='(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor) '+ ' '.join(v[0].replace('(symbol "NET10:', '(symbol "') for v in prepared.values()) + ')\n'
    (OUT/'cpu_packages.kicad_sym').write_text(library)
    (OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "NET10") (type "KiCad") (uri "${KIPRJMOD}/cpu_packages.kicad_sym") (options "") (descr "ISA-1 explicit package pin definitions")))\n')
    rootid=uid('root');root=[f'(kicad_sch (version 20230121) (generator eeschema) (uuid {rootid}) (paper "A4")',
      '(title_block (title "ISA-1 joined CPU pin graph") (rev "NET-10") (date "2026-11-25") (comment 1 "CPU ONLY - MEMORY / PERIPHERALS / POWER / PCB PENDING"))']
    rows=[]
    for page,group in enumerate(dict.fromkeys(p['group'] for p in parts),2):
        selected=[p for p in parts if p['group']==group];sheetid=uid('sheet/'+group);fileid=uid('file/'+group)
        root.append(f'(sheet (at {25+85*((page-2)%3)} {45+40*((page-2)//3)}) (size 65 20) (stroke (width 0.1524) (type default)) (fill (color 0 0 0 0)) (uuid {sheetid}) '
          f'(property "Sheetname" "{group}" (at {25+85*((page-2)%3)} {43+40*((page-2)//3)} 0) (effects (font (size 1.27 1.27)) (justify left bottom))) '
          f'(property "Sheetfile" "{group}.kicad_sch" (at {25+85*((page-2)%3)} {67+40*((page-2)//3)} 0) (effects (font (size 1.27 1.27)) (justify left top))) '
          f'(instances (project "cpu_global" (path "/{rootid}" (page "{page}")))))')
        lines=[f'(kicad_sch (version 20230121) (generator eeschema) (uuid {fileid}) (paper "A1")',
          f'(title_block (title "ISA-1 CPU: {group}") (rev "NET-10") (date "2026-11-25") (comment 1 "PARTIAL CPU ONLY - NOT FOR PRODUCTION"))',
          '(lib_symbols '+' '.join(v[0] for v in prepared.values())+')']
        chips=[p for p in selected if p['part']!='C'];positions={}
        if len(chips)>56:raise ValueError('Sheet capacity '+group)
        for i,p in enumerate(chips):positions[p['reference']]=(round((60+98*(i%8))/1.27)*1.27,round((65+75*(i//8))/1.27)*1.27)
        caps=[p for p in selected if p['part']=='C']
        if len(caps)!=len(chips):raise ValueError('Bypass count '+group)
        # Match capacitor placement to corresponding local order; electrical nets are unchanged.
        for cap,chip in zip(caps,chips):
            x,y=positions[chip['reference']];positions[cap['reference']]=(x+31.75,y-25.4)
        for p in selected:
            ref,kind=p['reference'],p['part'];x,y=positions[ref];value='100nF' if kind=='C' else kind
            ax,ay=(x+5,y-2) if kind=='C' else (x,y-(33 if kind=='AT28HC64B' else 25.4))
            props=f'(property "Reference" "{ref}" (at {ax} {ay} 0) (effects (font (size 1 1)))) (property "Value" "{value}" (at {ax} {ay+2.54} 0) (effects (font (size 1 1)))) '
            pp=' '.join(f'(pin "{pin}" (uuid {uid(ref+"/"+pin)}))' for pin in p['nets'])
            lines.append(f'(symbol (lib_id "NET10:{kind}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (uuid {uid(ref)}) {props}{pp} (instances (project "cpu_global" (path "/{rootid}/{sheetid}" (reference "{ref}") (unit 1)))))')
            for pin,n in p['nets'].items():
                px,py,angle=prepared[kind][1][pin];px+=x;py=y-py
                rows.append({'reference':ref,'part':kind,'pin':pin,'function':defs[kind]['pins'][pin]['name'],'net':n or 'NC','group':group})
                if n is None:lines.append(f'(no_connect (at {px} {py}) (uuid {uid(ref+"/nc/"+pin)}))')
                else:lines.append(f'(global_label "{n}" (shape input) (at {px} {py} 0) (effects (font (size 0.7 0.7)) (justify {"right" if angle==0 else "left"})) (uuid {uid(ref+"/label/"+pin)}))')
        lines.append(')');(OUT/(group+'.kicad_sch')).write_text('\n'.join(lines)+'\n')
    root+=['(sheet_instances (path "/" (page "1")))',')'];(OUT/'cpu_global.kicad_sch').write_text('\n'.join(root)+'\n')
    with (OUT/'pinmap.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    return rows


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs,parts,sources,refs=merge();unused=mark_unused_outputs(parts,defs);distribution=distribute(parts,defs)
    distribution['unused_outputs_marked_nc']=unused
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n')
    (OUT/'design.json').write_text(json.dumps({'iteration':'NET-10','parts':parts,'sources':sources,'reference_map':refs},indent=2)+'\n')
    (VERIFY/'fanout.json').write_text(json.dumps(distribution,indent=2)+'\n')
    project=OUT/'cpu_global.kicad_pro'
    if not project.exists():project.write_text(json.dumps({'meta':{'filename':'cpu_global.kicad_pro','version':1}},indent=2)+'\n')
    rows=emit(defs,parts)
    cmd=[KICAD,'sch','export','netlist','--format','kicadxml','-o',str(VERIFY/'cpu_global.xml'),str(OUT/'cpu_global.kicad_sch')]
    result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    actual={}
    for net in ET.parse(VERIFY/'cpu_global.xml').getroot().findall('./nets/net'):
        n=net.get('name').removeprefix('/')
        for node in net.findall('node'):actual[node.get('ref'),node.get('pin')]=n
    bad=[]
    for row in rows:
        n=actual.get((row['reference'],row['pin']))
        if row['net']=='NC':
            if n and not n.startswith('unconnected-'):bad.append(row)
        elif n!=row['net']:bad.append({'expected':row,'found':n})
    report={'date':'2026-11-25','kicad':subprocess.check_output([KICAD,'version'],text=True).strip(),'command':cmd,'components':len(parts),'pins':len(rows),'no_connects':sum(r['net']=='NC' for r in rows),'max_signal_input_loads':distribution['max_input_loads'],'added_buffers':distribution['added_buffer_packages'],'failures':bad,'scope':'Joined CPU graph only; board/peripherals/physical release pending'}
    (VERIFY/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return int(bool(bad))


if __name__=='__main__':raise SystemExit(main())
