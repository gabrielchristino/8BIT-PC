"""NET33 native video/DAC variants; spare channels plus one AHC174 package."""
import copy
import hashlib
import inspect
import json
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET
from collections import defaultdict,Counter
import build_memory_bus as emitter
from build_stack_bank import symbol as old_symbol
import build_dac_leaf as dac
from limited_process import run_limited

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net33'
BASE='052928f344e1fad6f6d43f380345793f60b748ff'

def save(path,value):dac.save(path,value)
def sig(net):return "1'b0" if net=='GND' else "1'b1" if net=='+5V' else 'n_'+net

def video_configuration():
    folder=ROOT/'hardware/load_distributed_video'
    defs=copy.deepcopy(json.loads((folder/'package-functions.json').read_text()))
    parts=copy.deepcopy(json.loads((folder/'design.json').read_text())['parts']);changes=[]
    def pin(ref,fn,expected,net):
        p=next(p for p in parts if p['reference']==ref)
        number=next(n for n,s in defs[p['part']]['pins'].items() if s['name']==fn)
        assert p['nets'][number]==expected,(ref,fn,expected)
        changes.append({'reference':ref,'pin':number,'before':expected,'after':net});p['nets'][number]=net
    for channel,bit in [(2,0),(3,1)]:
        pin('U27',f'A{channel}','GND',f'PIXEL_{bit}')
        pin('U27',f'Y{channel}',None,f'BLUE{bit}_BUFFER')
    pin('U35','A3','GND','P1');pin('U35','Y3',None,'DAC_CLK')
    for channel,source,target in [(1,'HSYNC_N','H_ACTIVE'),(2,'VSYNC_N','V_ACTIVE'),
                                  (3,'H_ACTIVE_LATCH','DAC_HSYNC_N'),(4,'V_ACTIVE_LATCH','DAC_VSYNC_N')]:
        pin('U32',f'A{channel}','GND',source);pin('U32',f'Y{channel}',None,target)
    defs['SN74AHC174']=copy.deepcopy(json.loads((ROOT/'hardware/common_request/package-functions.json').read_text())['SN74AHC174'])
    fs={'CLK':'DAC_CLK','CLR_N':'BUF_1_2','D0':'H_ACTIVE','D1':'V_ACTIVE',
        'Q0':'H_ACTIVE_LATCH','Q1':'V_ACTIVE_LATCH','VCC':'+5V','GND':'GND',
        **{f'D{i}':'GND' for i in range(2,6)}}
    parts.append({'reference':'U38','part':'SN74AHC174','x':290.83,'y':495.3,
                  'nets':{n:fs.get(s['name']) for n,s in defs['SN74AHC174']['pins'].items()}})
    parts.append({'reference':'C38','part':'C','x':311.15,'y':464.82,'nets':{'1':'+5V','2':'GND'}})
    for part in parts:part['value']='100nF' if part['part']=='C' else part['part']
    assert len(changes)==14
    return defs,parts,changes

def dac_configuration():
    defs=copy.deepcopy(json.loads((ROOT/'hardware/vga_dac_experiment/package-functions.json').read_text()))
    parts=copy.deepcopy(json.loads((ROOT/'hardware/vga_dac_experiment/design.json').read_text())['parts'])
    for p in parts:
        for pin,net in list(p['nets'].items()):
            if net=='DAC_VDD':p['nets'][pin]='+5V'
            elif net=='DAC_CLOCK':p['nets'][pin]='DAC_CLK'
            elif net and '_DB_' in net:
                color,bit=net.split('_DB_');bit=int(bit)
                if color in 'RG':
                    source=[2,0,1,2,0,1,2,0,1,2][bit] # reverse of abcabcabca
                    p['nets'][pin]='PIXEL_'+str(source+(5 if color=='R' else 2))
                else:
                    source=bit%2
                    p['nets'][pin]=f'BLUE{source}_BUFFER' if bit<6 else f'PIXEL_{source}'
    return defs,parts

def emit_video(defs,parts):
    name='dac_packet_video';folder=ROOT/'hardware'/name;verify=OUT/'video'
    folder.mkdir(parents=True,exist_ok=True);verify.mkdir(parents=True,exist_ok=True)
    env=dict(emitter.__dict__)
    env.update(OUT=folder,VERIFY=verify,uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net33/video/'+s)),
        package_symbol=lambda k,s:tuple(v.replace('NET02:','NET33:') if isinstance(v,str) else v for v in old_symbol(k,s)))
    source=inspect.getsource(emitter.emit).replace('memory_bus',name).replace('NET13','NET33')
    source=source.replace('ISA-1 SRAM / EEPROM data front-end','ISA-1 VGA packet adapter - experimental')
    source=source.replace('2026-11-25','2026-11-27').replace('NET-13','NET-33')
    source=source.replace('(paper "A1")','(paper "A0")')
    (verify/'adapted-emitter.py').write_text(source)
    exec(source,env);env['emit'](defs,parts)
    save(folder/'design.json',{'date':'2026-11-27','base_git_commit':BASE,'status':'unpromoted native video variant','parts':parts})
    save(folder/'package-functions.json',defs)
    return name,folder,verify

def emit_dac(defs,parts):
    name='vga_dac_rgb332';folder=ROOT/'hardware'/name;verify=OUT/'dac'
    folder.mkdir(parents=True,exist_ok=True);verify.mkdir(parents=True,exist_ok=True)
    env=dict(dac.__dict__)
    env.update(OUT=folder,VERIFY=verify,NAME=name,BASE=BASE,uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net33/dac/'+s)))
    source=inspect.getsource(dac.emit).replace('NET32','NET33').replace('NET32:', 'NET33:')
    # Symbol generator has its own namespace; keep it consistent with the emitter.
    symbol_source=inspect.getsource(dac.symbol).replace('NET32:','NET33:')
    exec(symbol_source,env);exec(source,env);env['emit'](defs,parts)
    save(folder/'design.json',{'date':'2026-11-27','base_git_commit':BASE,'status':'RGB332 pin mapping; diagnostic analog values, not final VGA','parts':parts})
    (verify/'adapted-emitter.py').write_text(source)
    (verify/'adapted-symbol.py').write_text(symbol_source)
    return name,folder,verify

def export(name,folder,verify,defs,parts):
    jobs={}
    for key,args in [('xml',['sch','export','netlist','--format','kicadxml','-o',str(verify/(name+'.xml'))]),
                     ('erc',['sch','erc','--format','json','-o',str(verify/'erc.json')])]:
        jobs[key]=run_limited([dac.KICAD,*args,str(folder/(name+'.kicad_sch'))],ROOT,timeout=120,memory_mb=2048,cpu_seconds=90,output_mb=4)
        save(verify/'commands.json',jobs)
        assert jobs[key]['exit']==0 and not jobs[key]['wall_timeout'],jobs[key]
    _,actual=dac.validate(verify/(name+'.xml'),defs,parts)
    erc=json.loads((verify/'erc.json').read_text())
    return actual,dict(Counter(v['type'] for s in erc['sheets'] for v in s['violations']))

def model_from_xml(video_actual,vd,vp,dac_actual,dd,dp):
    text=(ROOT/'sim/net30/load_video_async.sv').read_text()
    text=text.replace('module load_distributed_video_netlist','module dac_packet_video_netlist',1)
    old='output wire [7:0] pixel);'
    assert text.count(old)==1
    text=text.replace(old,'output wire [7:0] pixel,output wire dac_clk,blue0,blue1,dac_hsync_n,dac_vsync_n);')
    lines=[];new_nets=set()
    oldparts={p['reference']:p for p in json.loads((ROOT/'hardware/load_distributed_video/design.json').read_text())['parts']}
    for ref,channels in [('U27',[2,3]),('U32',[1,2,3,4]),('U35',[3])]:
        part=next(p for p in vp if p['reference']==ref);spec=vd[part['part']]
        fs={s['name']:video_actual.get((ref,pin)) for pin,s in spec['pins'].items()}
        for channel in channels:
            target=fs[f'Y{channel}'];a=fs[f'A{channel}'];new_nets.update([target,a])
            if ref=='U27':expression=sig(a)+" | "+sig(fs[f'B{channel}'])
            elif ref=='U32':expression='~'+sig(a)
            else:expression=sig(fs[f'OE{channel}_N'])+" ? 1'bz : "+sig(a)
            lines.append(f'assign #GATE_T {sig(target)}={expression};')
    part=next(p for p in vp if p['reference']=='U38')
    fs={s['name']:video_actual.get(('U38',pin)) for pin,s in vd[part['part']]['pins'].items()}
    data='{'+','.join(sig(fs[f'D{i}']) for i in reversed(range(6)))+'}'
    outputs='{'+','.join(sig(fs[f'Q{i}']) if fs.get(f'Q{i}') and not fs[f'Q{i}'].startswith('unconnected-') else 'U38_unused_Q'+str(i) for i in reversed(range(6)))+'}'
    lines.append(f'net19_ahc174 #(.TIMED(TIMED),.EARLY(EARLY_CAPTURE)) U38({sig(fs["CLK"])},{sig(fs["CLR_N"])},{data},{outputs});')
    new_nets.update(['H_ACTIVE_LATCH','V_ACTIVE_LATCH'])
    for net in sorted(new_nets):
        if 'wire '+sig(net)+';' not in text:lines.insert(0,'wire '+sig(net)+';')
    lines[:0]=['wire U38_unused_Q'+str(i)+';' for i in range(2,6)]
    for port,net in [('dac_clk','DAC_CLK'),('blue0','BLUE0_BUFFER'),('blue1','BLUE1_BUFFER'),('dac_hsync_n','DAC_HSYNC_N'),('dac_vsync_n','DAC_VSYNC_N')]:lines.append('assign '+port+'='+sig(net)+';')
    assert text.count('endmodule')==1
    text=text.replace('endmodule','\n'.join(lines)+'\nendmodule')
    (ROOT/'hardware/dac_packet_video/dac_packet_video_async.sv').write_text(text)
    lines=['`timescale 1ns/1ps','// XML pin-derived latch projection; analog omitted.',
        'module net33_dac(input wire clk,input wire [7:0] pixel,input wire blue0,blue1,output wire [9:0] red,green,blue);']
    for index,color in enumerate('RGB'):
        ref='U'+str(index+1);args=[]
        for bit in range(9,-1,-1):
            net=dac_actual[(ref,str(10-bit))]
            if net.startswith('PIXEL_'):args.append('pixel['+net.split('_')[1]+']')
            else:
                assert net in ('BLUE0_BUFFER','BLUE1_BUFFER');args.append('blue'+net[4])
        lines.append('net31_dac_latch '+ref+'(clk,{'+','.join(args)+'},'+['red','green','blue'][index]+');')
    lines+=['endmodule'];(ROOT/'hardware/vga_dac_rgb332/dac_rgb332_digital.sv').write_text('\n'.join(lines)+'\n')

def loads(sets):
    inputs=defaultdict(list)
    for label,defs,parts in sets:
        for part in parts:
            for pin,net in part['nets'].items():
                if defs[part['part']]['pins'][pin]['type']=='input' and net not in ('GND','+5V'):
                    inputs[net].append(label+'/'+part['reference']+'/'+pin)
    assert max(map(len,inputs.values()))<=4,[(n,p) for n,p in inputs.items() if len(p)>4]
    return {'scope':'Only video plus DAC leaf, input-pin counting; no other system leaves or extracted capacitance',
        'maximum_inputs':max(map(len,inputs.values())), 'hypothesis':'10pF per input plus10pF traces; AD9760 only has typical Cin, so not a guaranteed bound',
        'inputs':dict(inputs)}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    vd,vp,changes=video_configuration();dd,dp=dac_configuration()
    vn,vf,vv=emit_video(vd,vp);dn,df,dv=emit_dac(dd,dp)
    va,ve=export(vn,vf,vv,vd,vp);da,de=export(dn,df,dv,dd,dp)
    model_from_xml(va,vd,vp,da,dd,dp)
    load=loads([('video',vd,vp),('dac',dd,dp)]);save(OUT/'pin-loads.json',load)
    sources=['tools/build_dac_video_adapter.py','tools/build_dac_leaf.py','tools/build_memory_bus.py','tools/build_stack_bank.py',
        'sim/net30/load_video_async.sv','hardware/load_distributed_video/design.json','hardware/load_distributed_video/package-functions.json',
        'hardware/vga_dac_experiment/design.json','hardware/vga_dac_experiment/package-functions.json',
        'hardware/common_request/package-functions.json','sim/net19a/package_models.sv']
    report={'date':'2026-11-27','base_git_commit':BASE,'video_ics':38,'dac_ics':3,'combined_components':len(vp)+len(dp),
        'video_pin_changes_in_spare_channels':changes,'new_video_packages':1,'native_video_and_dac_pin_maps_checked':True,
        'scope':'Separate native video+DAC experiment, not promoted into complete NET30; selected existing timing models, analog not qualified',
        'erc_unwaived':{'video':ve,'dac':de},'erc_approved':False,'production_released':False,
        'sources':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in sources],'failures':[]}
    save(OUT/'native-results.json',report)
    print(json.dumps({'video_ics':38,'dac_ics':3,'spare_pin_changes':len(changes),'max_inputs_in_two_leaf_join':load['maximum_inputs'],'erc_unwaived':report['erc_unwaived']}),flush=True)

if __name__=='__main__':main()
