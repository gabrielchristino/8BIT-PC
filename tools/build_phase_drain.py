"""NET25 experimental native drain pair; do not run ancestor builders."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import uuid
import xml.etree.ElementTree as ET
from build_memory_decode import sig
from build_cpu_global import KICAD
import build_video_common_clock as video
import build_clocked_reset as reset

ROOT=Path(__file__).resolve().parents[1]

def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)

def make(kind):
    isvideo=kind=='video'
    predecessor=video if isvideo else reset
    oldname='video_common_clock' if isvideo else 'clocked_reset'
    name='phase_drain_video' if isvideo else 'phase_drain_reset'
    out=ROOT/'hardware'/name
    verify=ROOT/'verification/net25/native'/kind
    out.mkdir(parents=True,exist_ok=True);verify.mkdir(parents=True,exist_ok=True)
    defs=json.loads((ROOT/'hardware'/oldname/'package-functions.json').read_text())
    parts=copy.deepcopy(json.loads((ROOT/'hardware'/oldname/'design.json').read_text())['parts'])
    def part(ref):return next(p for p in parts if p['reference']==ref)
    def connect(ref,function,net,expected):
        p=part(ref)
        pin=next(n for n,s in defs[p['part']]['pins'].items() if s['name']==function)
        assert p['nets'][pin]==expected,(ref,function,p['nets'][pin],expected)
        p['nets'][pin]=net
    def ports():
        ins,outs=video.ports()
        ins.update(PHASE_INIT_N='phase_init_n',BANK_SYNC1='bank_sync1')
        outs['BANK_ARM']='bank_arm'
        return ins,outs
    if isvideo:
        p=part('U8');assert p['part']=='SN74AHC74'
        fs={'A':'SAFE','B':'+5V','CLK':'BUF_2_2','CLR_N':'PHASE_INIT_N',
            'Q3':'PHASE_RUN','VCC':'+5V','GND':'GND'}
        p.update(part='SN74AHC164',nets={pin:fs.get(s['name']) for pin,s in defs['SN74AHC164']['pins'].items()})
        connect('U9','CLR_N','+5V','BUF_1_1')
        connect('U9','A','PHASE_SHIFT_IN','PHASE_SERIAL')
        for ch,a,b,y in [(2,'PHASE_SERIAL','PHASE_RUN','PHASE_SHIFT_IN'),(3,'SAFE','PHASE_RUN','LOCAL_RESET_N')]:
            for f,n,e in [(f'A{ch}',a,'GND'),(f'B{ch}',b,'GND'),(f'Y{ch}',y,None)]:connect('U24',f,n,e)
        for f,n,e in [('A1','READY','GND'),('B1','BANK_SYNC1','GND'),('Y1','BANK_ARM',None)]:connect('U27',f,n,e)
        emitter=video.original._emitter.replace('video_raster',name).replace('NET14B','NET25V').replace('NET-14B','NET-25V')
        converter=video.converter.replace('video_common_clock',name)
        converter=once(converter,'input wire master,reset_n,power_good,','input wire master,reset_n,power_good,phase_init_n,bank_sync1,')
        converter=once(converter,'hsync_n,vsync_n,ready,output wire','hsync_n,vsync_n,ready,bank_arm,output wire')
    else:
        connect('U3','D0','BANK_ARM','+5V')
        emitter=reset.emitter.replace(oldname,name).replace('NET23','NET25R').replace('NET-23','NET-25R')
        converter=reset.converter.replace(oldname,name)
        converter=once(converter,"'BACKEND':'backend_source'","'BACKEND':'backend_source','BANK_ARM':'bank_arm'")
        converter=once(converter,"'MASTER':'master_source'}","'MASTER':'master_source','DELAY_CLEAR_N':'phase_init_n','RESET_SYNC1':'bank_sync1'}")
        converter=once(converter,'input wire raw_safe_n,backend_source,osc_power_valid,','input wire raw_safe_n,backend_source,osc_power_valid,bank_arm,')
        converter=once(converter,'keyboard_clk,cpu_source,master_source);','keyboard_clk,cpu_source,master_source,phase_init_n,bank_sync1);')
    env=dict(predecessor.__dict__)
    env.update(ROOT=ROOT,OUT=out,VERIFY=verify,ports=ports,
        uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net25/'+kind+'/'+s)))
    if isvideo:
        old_symbol=video.old_symbol
        env['package_symbol']=lambda k,s:tuple(x.replace('NET02:','NET25V:') if isinstance(x,str) else x for x in old_symbol(k,s))
    else:
        env['package_symbol']=lambda k,s:tuple(x.replace('NET23:','NET25R:') if isinstance(x,str) else x for x in reset.package_symbol(k,s))
    exec(emitter,env)
    exec(converter,env)
    env['emit'](defs,parts)
    (out/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n')
    (out/'design.json').write_text(json.dumps({'iteration':'NET25 experimental', 'parts':parts},indent=2)+'\n')
    command=[KICAD,'sch','export','netlist','--format','kicadxml','-o',str(verify/(name+'.xml')),str(out/(name+'.kicad_sch'))]
    r=subprocess.run(command,capture_output=True,text=True,timeout=120)
    (verify/'export.json').write_text(json.dumps({'command':command,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n')
    assert r.returncode==0,r.stderr
    report=env['convert']()
    report.update(date='2026-11-26',command=command,kicad=subprocess.check_output([KICAD,'version'],text=True).strip(),
        production_released=False,scope='Experimental synchronous token drain, strict native pin graph. Regression/analog/PVT/MTBF/power/PCB not approved.',
        sources=[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in
            [Path(__file__),ROOT/'hardware'/oldname/'design.json',ROOT/'hardware'/oldname/'package-functions.json',ROOT/'tools'/('build_video_common_clock.py' if isvideo else 'build_clocked_reset.py')]])
    (verify/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'kind':kind,**report}),flush=True)
    assert not report['failures'] and report['max_signal_input_loads']<=4

if __name__=='__main__':
    make('video')
    make('reset')
