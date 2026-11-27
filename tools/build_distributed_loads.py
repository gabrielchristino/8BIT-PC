"""NET30 separate native variants; reuse four spare AHC125 channels."""
import copy
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import uuid
import build_local_phase_reset as previous
import build_memory_bus as memory
from build_cpu_global import KICAD
from run_request_skew_probe import once

ROOT=Path(__file__).resolve().parents[1]
BASE='b5a19c7ee72a9b8543060e77f9c26824daf271ca'

def modify(kind,defs,parts):
    def pin(ref,fn,new,old):
        part=next(p for p in parts if p['reference']==ref)
        number=next(n for n,s in defs[part['part']]['pins'].items() if s['name']==fn)
        assert part['nets'][number]==old,(kind,ref,fn,part['nets'][number],old)
        part['nets'][number]=new
    if kind=='keyboard':
        for ref,fn in [('U15','B0'),('U16','B0'),('U17','B0'),('U33','B1')]:pin(ref,fn,'WDATA0_LOCAL','WDATA_0')
        for fn,new,old in [('A1','WDATA_0','GND'),('Y1','WDATA0_LOCAL',None),('A2','BOOT','GND'),('Y2','BOOT_EXTERNAL',None)]:pin('U40',fn,new,old)
    elif kind=='video':
        for fn,new,old in [('A2','H_2','GND'),('Y2','H2_EXTERNAL',None)]:pin('U35',fn,new,old)
        pin('U30','A3','H2_EXTERNAL','H_2')
    elif kind=='bus':
        for fn,new,old in [('A2','SELECT_3','GND'),('Y2','SELECT3_LOCAL',None)]:pin('U28',fn,new,old)
        for fn in ['B1','B2']:pin('U25',fn,'SELECT3_LOCAL','SELECT_3')
    else:raise ValueError(kind)

def prepare_logic(kind):
    # Clone the already reviewed NET26 preparation function. Stop BEFORE its
    # emitter/converter/report calls; no predecessor outputs are regenerated.
    source=inspect.getsource(previous.make)
    source=source[:source.index("    env['emit'](defs,parts)")]+"    return env,defs,parts,name\n"
    source=once(source,"name='local_phase_'+kind","name='load_distributed_'+kind")
    source=source.replace('verification/net26/native','verification/net30/native').replace('isa1/net26/','isa1/net30/')
    source=source.replace("namespace='NET26V'","namespace='NET30V'").replace("namespace='NET26K'","namespace='NET30K'")
    marker='    env=dict(previous.__dict__)'
    extra='''    published=json.loads((ROOT/'hardware'/('local_phase_'+kind)/'design.json').read_text())['parts']
    assert parts==published,'Prepared ancestor does not equal published NET26'
    modify(kind,defs,parts)
    old_ports=keyboard.ports if kind=='keyboard' else ports
    def system_ports():
        ins,outs=old_ports()
        if kind=='keyboard':
            assert outs.pop('BOOT')=='boot'
            outs['BOOT_EXTERNAL']='boot'
        else:
            assert outs.pop('H_2')=='h[2]'
            outs['H2_EXTERNAL']='h[2]'
        return ins,outs
'''
    source=once(source,marker,extra+marker)
    source=once(source,"VERIFY=verify,ports=keyboard.ports if kind=='keyboard' else ports",'VERIFY=verify,ports=system_ports')
    env=dict(previous.__dict__);env['modify']=modify
    target=ROOT/'verification/net30/native'/kind;target.mkdir(parents=True,exist_ok=True)
    (target/'adapted-preparation.py').write_text(source)
    exec(source,env)
    return env['make'](kind)

def prepare_bus():
    name='load_distributed_bus';folder=ROOT/'hardware'/name;verify=ROOT/'verification/net30/native/bus'
    folder.mkdir(parents=True,exist_ok=True);verify.mkdir(parents=True,exist_ok=True)
    parent=ROOT/'hardware/memory_bus'
    defs=copy.deepcopy(json.loads((parent/'package-functions.json').read_text()))
    parts=copy.deepcopy(json.loads((parent/'design.json').read_text())['parts']);modify('bus',defs,parts)
    env=dict(memory.__dict__);env.update(OUT=folder,VERIFY=verify,uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net30/bus/'+s)))
    for function in [memory.package_symbol,memory.emit,memory.convert]:
        source=inspect.getsource(function).replace('memory_bus',name).replace('NET13','NET30B').replace('NET-13','NET-30B')
        (verify/(function.__name__+'-adapted.py')).write_text(source)
        exec(source,env)
    return env,defs,parts,name

def main():
    for kind in ['video','keyboard','bus']:
        env,defs,parts,name=prepare_bus() if kind=='bus' else prepare_logic(kind)
        folder=ROOT/'hardware'/name;verify=ROOT/'verification/net30/native'/kind
        env['emit'](defs,parts)
        (folder/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n')
        (folder/'design.json').write_text(json.dumps({'iteration':'NET30 unaccepted load-distribution candidate','base_git_commit':BASE,'parts':parts},indent=2)+'\n')
        cmd=[KICAD,'sch','export','netlist','--format','kicadxml','-o',str(verify/(name+'.xml')),str(folder/(name+'.kicad_sch'))]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        (verify/'export.json').write_text(json.dumps({'command':cmd,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr},indent=2)+'\n')
        assert result.returncode==0,result.stderr
        report=env['convert']()
        report.update(date='2026-11-26',base_git_commit=BASE,production_released=False,
            scope='Native spare-channel load-distribution candidate; functional/timing/analog/PCB qualification pending.',
            sources=[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in [
                'tools/build_distributed_loads.py','tools/build_local_phase_reset.py','tools/build_memory_bus.py',
                'hardware/'+({'bus':'memory_bus'}.get(kind,'local_phase_'+kind))+'/design.json']])
        (verify/'schematic-check.json').write_text(json.dumps(report,indent=2)+'\n')
        assert not report['failures'] and report['max_signal_input_loads']<=4
        print(json.dumps({'kind':kind,'components':report['components'],'pins':report['pins'],'candidate_only':True}),flush=True)

if __name__=='__main__':main()
