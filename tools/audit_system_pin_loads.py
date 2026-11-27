"""Join candidate pin graphs using exact existing HDL boundary aliases.

Restricted structural reader, not a Verilog elaborator, PCB extractor or ERC.
Resistors and conditional contacts never become copper aliases.
"""
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net29'
LEAVES={
 'cpu':('cpu_global','isa1_cpu'),
 'decode':('memory_decode','memory_decode_netlist'),
 'access_controller':('common_request','common_request_netlist'),
 'frontend':('memory_bus','memory_bus_netlist'),
 'raster':('local_phase_video','local_phase_video_netlist'),
 'peripheral':('local_phase_keyboard','local_phase_keyboard_netlist'),
 'reset_domains':('local_phase_reset','local_phase_reset_netlist')}
XMLS={
 'cpu':'verification/net10/cpu_global.xml',
 'decode':'verification/net11/memory_decode.xml',
 'access_controller':'verification/net24/native/common_request.xml',
 'frontend':'verification/net13/memory_bus.xml',
 'raster':'verification/net26/native/video/local_phase_video.xml',
 'peripheral':'verification/net26/native/keyboard/local_phase_keyboard.xml',
 'reset_domains':'verification/net26/native/reset/local_phase_reset.xml'}

def clean(text):return re.sub(r'//[^\n]*|/\*.*?\*/','',text,flags=re.S)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def group(text,start):
    assert text[start]=='('
    depth=0
    for i in range(start,len(text)):
        if text[i]=='(':depth+=1
        if text[i]==')':
            depth-=1
            if not depth:return text[start+1:i],i+1
    raise ValueError('Unbalanced structural expression')

def header(text):
    m=re.search(r'\bmodule\s+(\w+)\s*',text);assert m
    pos=m.end()
    if text[pos]=='#':_,pos=group(text,text.index('(',pos))
    ports,_=group(text,text.index('(',pos));result=[];direction=None;width=1
    for fragment in ports.split(','):
        fragment=fragment.strip()
        m=re.match(r'(input|output|inout)\s+(?:wire\s+)?(?:\[(\d+):(\d+)\]\s*)?(\w+)$',fragment)
        if m:
            direction,hi,lo,name=m.groups();width=int(hi)-int(lo)+1 if hi else 1
            assert not lo or int(lo)==0
        else:
            assert direction and re.fullmatch(r'\w+',fragment),fragment
            name=fragment
        result.append({'name':name,'width':width,'direction':direction})
    return result

def instance(text,module,name):
    m=re.search(r'\b'+re.escape(module)+r'\s*',text);assert m,module
    pos=m.end()
    if text[pos]=='#':_,pos=group(text,text.index('(',pos))
    m=re.match(r'\s*(\w+)\s*',text[pos:]);assert m and m[1]==name,(module,name)
    pos+=m.end();arguments,_=group(text,pos)
    if arguments.strip().startswith('.'):
        pairs=re.findall(r'\.(\w+)\(([^()]*)\)',arguments)
        residue=re.sub(r'\.\w+\([^()]*\)','',arguments).replace(',','').strip()
        assert not residue,residue
        assert len(dict(pairs))==len(pairs),'Duplicate named port'
        return dict(pairs)
    assert '{' not in arguments and '(' not in arguments
    return [x.strip() for x in arguments.split(',')]

class Join:
    def __init__(self):self.parents={};self.widths={};self.links=[]
    def find(self,key):
        parent=self.parents.setdefault(key,key)
        if parent!=key:self.parents[key]=self.find(parent)
        return self.parents[key]
    def union(self,a,b,reason):
        self.parents[self.find(a)]=self.find(b);self.links.append({'a':a,'b':b,'reason':reason})
    def atom(self,scope,value):
        value=re.sub(r'\s+','',value)
        if value=="1'b1":return 'rail/+5V'
        if value=="1'b0":return 'rail/GND'
        if value.startswith('memory.'):
            scope='mem';value=value.removeprefix('memory.')
        assert re.fullmatch(r'\w+(?:\[\d+\])?',value),value
        return scope+'/'+value
    def expand(self,scope,value,width):
        value=re.sub(r'\s+','',value)
        if re.fullmatch(r'\w+',value):
            key=scope+'/'+value
            assert self.widths.setdefault(key,width)==width,('Inconsistent bus width',key,width,self.widths[key])
            return [self.atom(scope,value+(f'[{i}]' if width>1 else '')) for i in range(width)]
        assert width==1,('Unsupported bus expression',value,width)
        return [self.atom(scope,value)]
    def bind(self,ports,args,scope,parent):
        if isinstance(args,list):
            assert len(args)==len(ports)
            args={p['name']:value for p,value in zip(ports,args)}
        assert set(args)=={p['name'] for p in ports},'Port inventory mismatch'
        for p in ports:
            a=self.expand(scope,p['name'],p['width']);b=self.expand(parent,args[p['name']],p['width'])
            for left,right in zip(a,b):self.union(left,right,'port binding')

def build(adapter=None):
    join=Join();pins=[];sources=[];parts=Counter();skipped=[]
    memory_path=ROOT/'sim/net26/isa1_memory_local_phase.sv'
    bench_path=ROOT/'verification/net26/program/system-tb_rtl_program-ideal.sv'
    memory=clean(adapter if adapter is not None else memory_path.read_text())
    bench=clean(bench_path.read_text())
    join.bind(header(memory),instance(bench,'isa1_clocked_memory','memory'),'mem','bench')
    for key,(name,module) in LEAVES.items():
        folder=ROOT/'hardware'/name
        design=folder/'design.json';functions=folder/'package-functions.json';model=folder/(name+'_netlist.sv')
        raw=json.loads(design.read_text());defs=json.loads(functions.read_text());text=clean(model.read_text())
        xml_path=ROOT/XMLS[key];actual={}
        for net in ET.parse(xml_path).getroot().findall('./nets/net'):
            netname=net.get('name').removeprefix('/')
            for node in net.findall('node'):
                node_key=(node.get('ref'),node.get('pin'))
                assert node_key not in actual,node_key
                actual[node_key]=netname
        expected={(p['reference'],pin):net for p in raw['parts'] for pin,net in p['nets'].items()}
        assert set(actual)==set(expected),(name,'XML pin inventory')
        for pin,net in expected.items():
            assert actual[pin]==net if net is not None else actual[pin].startswith('unconnected-'),(name,pin,net,actual[pin])
        scope='cpu' if key=='cpu' else 'mem/'+key
        args=instance(bench,module,'dut') if key=='cpu' else instance(memory,module,key)
        join.bind(header(text),args,scope,'bench' if key=='cpu' else 'mem')
        for alias in re.findall(r'\bassign\s+([^;]+);',text):
            if alias.lstrip().startswith('#'):continue  # real gate/delay model, not a wire
            left,right=map(str.strip,alias.split('='))
            join.union(join.atom(scope,left),join.atom(scope,right),'leaf port alias')
        for left,right in re.findall(r'\btran\(([^,]+),([^()]+)\);',text):
            left=left.strip();right=right.strip()
            if left.startswith('n_') and right.startswith('n_'):
                skipped.append({'scope':scope,'left':left,'right':right,'reason':'Functional resistor shortcut is not a physical wire.'})
            else:join.union(join.atom(scope,left),join.atom(scope,right),'bidirectional port alias')
        for p in raw['parts']:
            parts[p['part']]+=1
            for number,net in p['nets'].items():
                if net is None:continue
                key_net='rail/'+net if net in ('+5V','GND') else scope+'/n_'+re.sub(r'[^A-Za-z0-9_]','_',net)
                pin=defs[p['part']]['pins'][number]
                pins.append({'scope':scope,'module':name,'reference':p['reference'],'family':p['part'],
                    'pin':number,'function':pin['name'],'type':pin['type'],'local_net':net,'key':key_net})
        sources.extend([design,functions,model,xml_path])
    # Exact wire concatenation in the published adapter. Do not union any
    # behavioral forcepoint, contact, gate, test observer or clock stimulus.
    assert 'wire [14:0] video_address={v[8:2],h};' in memory,'Unrecognized video address wiring'
    for i in range(15):
        target='h['+str(i)+']' if i<8 else 'v['+str(i-6)+']'
        join.union('mem/video_address['+str(i)+']','mem/'+target,'video address wire concatenation')
    assert len(skipped)==4 and parts['C']==464
    for shortcut in skipped:
        assert join.find(join.atom(shortcut['scope'],shortcut['left']))!=join.find(join.atom(shortcut['scope'],shortcut['right']))
    assert join.find('rail/+5V')!=join.find('rail/GND')
    grouped=defaultdict(list)
    for pin in pins:grouped[join.find(pin['key'])].append(pin)
    aliases=defaultdict(list)
    for key in list(join.parents):aliases[join.find(key)].append(key)
    nets=[]
    for root,members in grouped.items():
        if root in (join.find('rail/+5V'),join.find('rail/GND')):continue
        inputs=[p for p in members if p['type']=='input']
        bidir=[p for p in members if p['type']=='bidirectional']
        outputs=[p for p in members if p['type'] in ('output','open_collector','bidirectional')]
        nets.append({'id':root,'aliases':sorted(aliases[root]),'input_count':len(inputs),
            'bidirectional_count':len(bidir),'driver_candidates':len(outputs),'pins':members,
            'conditional_input_only_pf':10*len(inputs)+10,
            'load_capacitance_extracted_pf':None,'electrically_qualified':False})
    nets.sort(key=lambda row:(-row['input_count'],row['id']))
    def load(scope,net):
        root=join.find(scope+'/n_'+net)
        return next(r['input_count'] for r in nets if r['id']==root)
    assert load('mem/raster','BACKEND')==4
    assert load('mem/raster','P1')==3
    assert load('mem/raster','LOCAL_RESET_N')==4
    assert load('mem/peripheral','BUF_1_0')==4
    assert sum(parts.values())==982  #460IC+2osc+464C+52R+4connectors
    sources.extend([memory_path,bench_path,Path(__file__)])
    return {'date':'2026-11-26','scope':'Structural HDL-boundary union of existing KiCad candidate pin graphs; not a new unified schematic, full Verilog elaboration, ERC, capacitance extraction, electrical/STA or production pass.',
        'parts':dict(parts),'connected_pins':len(pins),'signal_nets':nets,
        'nets_above_four_inputs':[r['id'] for r in nets if r['input_count']>4],
        'maximum_input_count':max(r['input_count'] for r in nets),'alias_links':join.links,
        'resistor_shortcuts_not_joined':skipped,
        'limitations':['Input-only10pF/pin+10pFtrace is a screening assumption at5V, not family/all-VDD data or extracted capacitance.',
            'Bidirectional/output/connector capacitance and resistive leakage are additional; multidriver nets require enable analysis.',
            'The test adapter contains RAW and oscillator power forcepoints. No analog source circuitry is invented by this join.',
            'Testbench observers add no physical loads; behavioral switch contacts remain conditional, not copper aliases.'],
        'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':digest(p)} for p in sources],
        'production_released':False}

def main():
    report=build();OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'system-pin-loads.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    print(json.dumps({'pins':report['connected_pins'],'max_inputs':report['maximum_input_count'],
        'above_four':report['nets_above_four_inputs']}))

if __name__=='__main__':main()
