"""NET35 alternative supply/supervisor window; no predecessor regenerated."""
import copy
import hashlib
import inspect
import json
from pathlib import Path
import uuid
from collections import Counter
import build_vga_sync as prior
import build_dac_leaf as native
from limited_process import run_limited

ROOT=prior.ROOT
OUT=ROOT/'hardware/vga_sync_window'
VERIFY=ROOT/'verification/net35/native'
NAME='vga_sync_window'
BASE='e2d466193a4f2e83e251ebb9c7ea985405907e9d'

def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net35/'+s))
def save(path,value):native.save(path,value)

def configuration():
    defs=copy.deepcopy(json.loads((ROOT/'hardware/vga_sync_3v3/package-functions.json').read_text()))
    parts=copy.deepcopy(json.loads((ROOT/'hardware/vga_sync_3v3/design.json').read_text())['parts'])
    del defs['TPS70933DBVR']
    spec=defs.pop('TPS3808G33DBVR');defs['TPS3808G01DBVR']=spec
    names=['IN1','IN2','EN_UV','PG','ILIM','PGFB','SET','GND','OUTS','OUT','EP_GND']
    types={'IN1':'power_in','IN2':'power_in','PG':'open_collector','GND':'power_in','EP_GND':'power_in','OUT':'power_out'}
    defs['LT3042IMSE_PBF']={'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/lt3042.pdf',
        'source':'RevC MSE10 plus exposed GND pad11; web transcription, local PDF download timed out',
        'pins':{str(i):{'name':n,'type':types.get(n,'passive' if n in ['ILIM','SET'] else 'input')} for i,n in enumerate(names,1)}}
    for p in parts:
        p['nets']={pin:('SYNC_RAIL' if net=='SYNC_3V3' else 'PG_LOCAL_N' if net=='PG33_N' else net) for pin,net in p['nets'].items()}
        if p['reference']=='U1':
            p.update(part='LT3042IMSE_PBF',value='LT3042IMSE#PBF',role='3.51V nominal; Kelvin OUTS and exposed pad require actual layout validation',
                nets={'1':'CORE_VDD','2':'CORE_VDD','3':'CORE_VDD','4':None,'5':'GND','6':'CORE_VDD',
                      '7':'LDO_SET','8':'GND','9':'SYNC_RAIL','10':'SYNC_RAIL','11':'GND'})
        if p['reference']=='U2':p.update(part='TPS3808G01DBVR',value='TPS3808G01DBVR');p['nets']['5']='SYNC_SENSE'
        if p['reference']=='C2':p.update(value='100uF',role='Bulk effective>=47uF and ESR<=50milliohm are acceptance requirements, not measured')
        if p['reference']=='R6':p.update(value='2.2k',role='minimum steady load>1mA for LT3042 full-range specifications')
    def add(ref,kind,value,a,b,x,y,role):parts.append({'reference':ref,'part':kind,'value':value,'nets':{'1':a,'2':b},'x':x,'y':y,'role':role})
    add('C6','C','10uF','SYNC_RAIL','GND',299.72,96.52,'Ceramic effective>=4.7uF,ESR<50milliohm,ESL<2nH; Kelvin OUTS')
    add('C7','C','0.47uF','LDO_SET','GND',299.72,139.7,'SET bypass, startup/transients not yet qualified')
    add('R9','R','14k','SYNC_RAIL','SYNC_SENSE',269.24,190.5,'0.1 percent across selected conditions, divider upper')
    add('R10','R','2k','SYNC_SENSE','GND',330.2,190.5,'0.1 percent across selected conditions, divider lower')
    add('R11','R','35.1k','LDO_SET','GND',299.72,218.44,'0.1 percent across selected conditions, output setting')
    assert len(parts)==22
    return defs,parts

def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs,parts=configuration();env=dict(prior.__dict__)
    env.update(OUT=OUT,VERIFY=VERIFY,NAME=NAME,BASE=BASE,uid=uid)
    symbol=inspect.getsource(prior.symbol).replace('NET34','NET35')
    emit=inspect.getsource(prior.emit).replace('NET34','NET35').replace('3.3V sync','3.51V sync window')
    exec(symbol,env);exec(emit,env);env['emit'](defs,parts)
    save(OUT/'design.json',{'date':'2026-11-27','base_git_commit':BASE,'status':'Alternative window candidate, not physical power qualification','parts':parts})
    (VERIFY/'adapted-symbol.py').write_text(symbol);(VERIFY/'adapted-emitter.py').write_text(emit)
    jobs={}
    for key,args in [('xml',['sch','export','netlist','--format','kicadxml','-o',str(VERIFY/(NAME+'.xml'))]),
                     ('erc',['sch','erc','--format','json','-o',str(VERIFY/'erc.json')]),
                     ('pdf',['sch','export','pdf','-o',str(VERIFY/'schematic.pdf')])]:
        jobs[key]=run_limited([native.KICAD,*args,str(OUT/(NAME+'.kicad_sch'))],ROOT,timeout=120,memory_mb=2048,cpu_seconds=90,output_mb=2)
        save(VERIFY/'commands.json',jobs);assert jobs[key]['exit']==0 and not jobs[key]['wall_timeout'],jobs[key]
    native.validate(VERIFY/(NAME+'.xml'),defs,parts)
    jobs['preview']=run_limited(['pdftoppm','-scale-to','1800','-singlefile','-png',str(VERIFY/'schematic.pdf'),str(VERIFY/'preview')],ROOT,timeout=30,memory_mb=512,cpu_seconds=20)
    save(VERIFY/'commands.json',jobs);assert jobs['preview']['exit']==0
    model=(ROOT/'hardware/vga_sync_3v3/vga_sync_functional.sv').read_text()
    (OUT/'sync_window_functional.sv').write_text(model.replace('module net34_sync','module net35_sync'))
    erc=json.loads((VERIFY/'erc.json').read_text());counts=dict(Counter(v['type'] for s in erc['sheets'] for v in s['violations']))
    names=['tools/build_sync_window.py','tools/build_vga_sync.py','tools/build_dac_leaf.py','hardware/vga_sync_3v3/design.json',
        'hardware/vga_sync_3v3/package-functions.json','hardware/vga_sync_3v3/vga_sync_functional.sv','references/net20/tps3808.pdf']
    report={'date':'2026-11-27','base_git_commit':BASE,'components':len(parts),'ics':4,'pins':sum(len(p['nets']) for p in parts),
        'qualified_state_model_equal_after_module_rename':True,'erc_unwaived':counts,'erc_approved':False,
        'lt3042_original_local_pdf':False,'power_ramp_or_transients_qualified':False,'production_released':False,
        'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names],'failures':[]}
    save(VERIFY/'native-results.json',report);print(json.dumps(report),flush=True)

if __name__=='__main__':main()
