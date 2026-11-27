"""NET34 standalone, supervised 3.3V sync driver. Predecessors untouched."""
import csv
import hashlib
import inspect
import json
from pathlib import Path
import uuid
from collections import Counter
import build_dac_leaf as common
from limited_process import run_limited

ROOT=common.ROOT
OUT=ROOT/'hardware/vga_sync_3v3'
VERIFY=ROOT/'verification/net34/native'
NAME='vga_sync_3v3'
BASE='8aa26ed00ec94f87f3f21fa8cd93f4b1abf1e14b'

def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net34/'+s))
def save(path,value):common.save(path,value)

def configuration():
    def spec(names,types,url):
        return {'datasheet':url,'pins':{str(i):{'name':n,'type':types.get(n,'input')} for i,n in enumerate(names,1)}}
    defs={
        'TPS70933DBVR':spec(['IN','GND','EN','NC','OUT'],{'IN':'power_in','GND':'power_in','OUT':'power_out','NC':'no_connect'},'https://www.ti.com/lit/ds/symlink/tps709.pdf'),
        'TPS3808G33DBVR':spec(['RESET_N','GND','MR_N','CT','SENSE','VCC'],{'RESET_N':'open_collector','GND':'power_in','VCC':'power_in'},'https://www.ti.com/lit/ds/symlink/tps3808.pdf'),
        'SN74LVC1G132DBVR':spec(['A','B','GND','Y','VCC'],{'GND':'power_in','Y':'output','VCC':'power_in'},'https://www.ti.com/lit/ds/symlink/sn74lvc1g132.pdf'),
        'SN74LVC2G125DCTR':spec(['OE0_N','A0','Y1','GND','A1','Y0','OE1_N','VCC'],{'Y0':'tri_state','Y1':'tri_state','GND':'power_in','VCC':'power_in'},'https://www.ti.com/lit/ds/symlink/sn74lvc2g125.pdf')}
    for kind in ['R','C']:
        defs[kind]={'datasheet':'','pins':{'1':{'name':'1','type':'passive'},'2':{'name':'2','type':'passive'}}}
    parts=[]
    def add(ref,kind,value,nets,x,y,role):
        assert set(nets)==set(defs[kind]['pins'])
        parts.append({'reference':ref,'part':kind,'value':value,'nets':nets,'x':x,'y':y,'role':role})
    add('U1','TPS70933DBVR','TPS70933DBVR',{'1':'CORE_VDD','2':'GND','3':None,'4':None,'5':'SYNC_3V3'},60.96,60.96,'EN intentionally open per datasheet; do not tie EN to VIN')
    add('U2','TPS3808G33DBVR','TPS3808G33DBVR',{'1':'PG33_N','2':'GND','3':'SYNC_3V3','4':None,'5':'SYNC_3V3','6':'SYNC_3V3'},177.8,60.96,'CT intentionally open,12..28ms release; analog operation not modeled')
    add('U3','SN74LVC1G132DBVR','SN74LVC1G132DBVR',{'1':'VIDEO_READY','2':'PG33_N','3':'GND','4':'SYNC_OE_N','5':'SYNC_3V3'},60.96,139.7,'Schmitt NAND: enable only when source and local supervisor are ready')
    add('U4','SN74LVC2G125DCTR','SN74LVC2G125DCTR',{'1':'SYNC_OE_N','2':'DAC_HSYNC_N','3':'V_BUFFER','4':'GND','5':'DAC_VSYNC_N','6':'H_BUFFER','7':'SYNC_OE_N','8':'SYNC_3V3'},177.8,139.7,'5.5V tolerant inputs; Ioff specified at VCC0, not whole ramp')
    for i,(a,b,value,role,x,y) in enumerate([
        ('CORE_VDD','GND','4.7uF','CIN effective requirement>=2.2uF; component not qualified',30.48,96.52),
        ('SYNC_3V3','GND','22uF','COUT effective requirement>=2.2uF; transient target10uF unqualified',91.44,96.52),
        ('SYNC_3V3','GND','100nF','supervisor decoupling',208.28,96.52),
        ('SYNC_3V3','GND','100nF','NAND decoupling',91.44,175.26),
        ('SYNC_3V3','GND','100nF','dual buffer decoupling',208.28,175.26)],1):
        add('C'+str(i),'C',value,{'1':a,'2':b},x,y,role)
    resistors=[('SYNC_3V3','PG33_N','4.7k','supervisor pullup'),('SYNC_3V3','SYNC_OE_N','10k','OE default disabled pullup'),
        ('VIDEO_READY','GND','47k','define disconnected ready input'),('H_BUFFER','H_OUT','75','1 percent series, not shunt'),
        ('V_BUFFER','V_OUT','75','1 percent series, not shunt'),('SYNC_3V3','GND','10k','minimum rail load>=100uA when qualified'),
        ('DAC_HSYNC_N','GND','47k','define disconnected H input'),('DAC_VSYNC_N','GND','47k','define disconnected V input')]
    for i,(a,b,value,role) in enumerate(resistors,1):
        add('R'+str(i),'R',value,{'1':a,'2':b},30.48+60.96*((i-1)%4),218.44+25.4*((i-1)//4),role)
    return defs,parts

def symbol(kind,spec):
    if kind in ('R','C'):
        result,loc=common.symbol(kind,spec);return result.replace('NET32:','NET34:'),loc
    count=len(spec['pins']);left=(count+1)//2;loc={}
    for i in range(1,count+1):
        isleft=i<=left;row=i-1 if isleft else count-i
        loc[str(i)]=(-17.78 if isleft else 17.78,((left-1)/2-row)*2.54,0 if isleft else 180)
    text=f'(symbol "NET34:{kind}" (pin_names (offset 0.508)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 16 0) (effects (font (size 1 1)))) (property "Value" "{kind}" (at 0 13 0) (effects (font (size 1 1)))) (property "Datasheet" {json.dumps(spec["datasheet"])} (at 0 0 0) (effects (font (size 1 1)) hide)) (symbol "{kind}_0_1" (rectangle (start -12.7 8.89) (end 12.7 -8.89) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol "{kind}_1_1" '
    for pin,s in spec['pins'].items():
        x,y,angle=loc[pin]
        text+=f'(pin {s["type"]} line (at {x:.3f} {y:.3f} {angle}) (length 5.08) (name "{s["name"]}" (effects (font (size 1 1)))) (number "{pin}" (effects (font (size 1 1)))))'
    return text+'))',loc

def emit(defs,parts):
    # Reuse the tested complete-package emitter in a separate environment.
    env=dict(common.__dict__);env.update(OUT=OUT,VERIFY=VERIFY,NAME=NAME,BASE=BASE,uid=uid,symbol=symbol)
    source=inspect.getsource(common.emit).replace('NET32','NET34')
    source=source.replace('dac_packages.kicad_sym','sync_packages.kicad_sym')
    source=source.replace('ISA-1 DAC experiment - interface protection pending','ISA-1 supervised 3.3V sync - experimental')
    source=source.replace('DIAGNOSTIC RSET - UNCALIBRATED WHITE - NOT FOR PRODUCTION','VGA PROTECTION / POWER TRANSIENTS / PCB UNQUALIFIED')
    exec(source,env);env['emit'](defs,parts)
    (VERIFY/'adapted-emitter.py').write_text(source)
    save(OUT/'design.json',{'date':'2026-11-27','base_git_commit':BASE,'status':'standalone candidate, no connector/ESD or analog POR qualification','parts':parts})

def project(actual):
    # Pin numbers and native nets are checked before emitting the projection.
    assert actual[('U3','1')]=='VIDEO_READY' and actual[('U3','2')]=='PG33_N' and actual[('U3','4')]=='SYNC_OE_N'
    assert actual[('U4','6')]=='H_BUFFER' and actual[('U4','3')]=='V_BUFFER'
    text='''`timescale 1ns/1ps
// Qualified-state functional projection, NOT regulator/supervisor/transistor POR model.
// supply=0: fully off/Ioff; supply=1: qualified 3.0..3.6V; supply=2: ramp unspecified.
module net34_sync #(parameter SLOW=1)(input wire [1:0] supply,input wire supervisor_released,
 input wire ready_source,h_internal,v_internal,output tri h_buffer,v_buffer,output wire oe_n);
 localparam realtime GATE_T=SLOW?6.5:2,DATA_T=SLOW?5.3:1.4,ENABLE_T=SLOW?5.7:1.2,DISABLE_T=SLOW?5.6:1.4;
 localparam realtime ACTIVE_T=DATA_T>ENABLE_T?DATA_T:ENABLE_T;
 tri pg,ready,h,v,oe;
 assign (weak1,weak0) ready=1'b0;
 assign (weak1,weak0) h=1'b0;
 assign (weak1,weak0) v=1'b0;
 assign ready=ready_source;assign h=h_internal;assign v=v_internal;
 assign (weak1,weak0) pg=supply==0?1'b0:supply==1?1'b1:1'bx;
 assign pg=(supply==1 && !supervisor_released)?1'b0:1'bz;
 assign (weak1,weak0) oe=supply==0?1'b0:supply==1?1'b1:1'bx;
 assign #GATE_T oe=supply==0?1'bz:supply==1?~(pg & ready):1'bx;
 assign oe_n=oe;
 assign #(ACTIVE_T,ACTIVE_T,DISABLE_T) h_buffer=supply==0?1'bz:supply!=1?1'bx:oe?1'bz:h;
 assign #(ACTIVE_T,ACTIVE_T,DISABLE_T) v_buffer=supply==0?1'bz:supply!=1?1'bx:oe?1'bz:v;
 // One selected active delay covers data and enable; it is not an exact cell arc.
endmodule
'''
    (OUT/'vga_sync_functional.sv').write_text(text)

def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs,parts=configuration();emit(defs,parts);jobs={}
    for key,args in [('xml',['sch','export','netlist','--format','kicadxml','-o',str(VERIFY/(NAME+'.xml'))]),
                     ('erc',['sch','erc','--format','json','-o',str(VERIFY/'erc.json')]),
                     ('pdf',['sch','export','pdf','-o',str(VERIFY/'schematic.pdf')])]:
        jobs[key]=run_limited([common.KICAD,*args,str(OUT/(NAME+'.kicad_sch'))],ROOT,timeout=120,memory_mb=2048,cpu_seconds=90,output_mb=2)
        save(VERIFY/'commands.json',jobs);assert jobs[key]['exit']==0 and not jobs[key]['wall_timeout'],jobs[key]
    _,actual=common.validate(VERIFY/(NAME+'.xml'),defs,parts);project(actual)
    jobs['preview']=run_limited(['pdftoppm','-scale-to','1800','-singlefile','-png',str(VERIFY/'schematic.pdf'),str(VERIFY/'preview')],ROOT,timeout=30,memory_mb=512,cpu_seconds=20)
    save(VERIFY/'commands.json',jobs);assert jobs['preview']['exit']==0
    erc=json.loads((VERIFY/'erc.json').read_text());counts=dict(Counter(v['type'] for s in erc['sheets'] for v in s['violations']))
    sources=['tools/build_vga_sync.py','tools/build_dac_leaf.py','tools/limited_process.py','references/net34/sn74lvc1g132.pdf',
             'references/net34/tps709.pdf','references/net23/sn74lvc2g125.pdf','references/net20/tps3808.pdf']
    report={'date':'2026-11-27','base_git_commit':BASE,'components':len(parts),'ics':4,'pins':sum(len(p['nets']) for p in parts),
        'erc_unwaived':counts,'erc_approved':False,'power_ramp_or_transient_qualified':False,'production_released':False,
        'sources':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in sources],'failures':[]}
    save(VERIFY/'native-results.json',report);print(json.dumps(report),flush=True)

if __name__=='__main__':main()
