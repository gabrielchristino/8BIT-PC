"""Apply the published structural reader to the separate NET30 candidates."""
import hashlib
import inspect
import json
from pathlib import Path
import audit_system_pin_loads as original

ROOT=Path(__file__).resolve().parents[1]

def main():
    env=dict(original.__dict__);env['LEAVES']=dict(original.LEAVES);env['XMLS']=dict(original.XMLS)
    deltas={}
    for key,kind,parent in [('raster','video','local_phase_video'),('peripheral','keyboard','local_phase_keyboard'),('frontend','bus','memory_bus')]:
        name='load_distributed_'+kind;env['LEAVES'][key]=(name,name+'_netlist')
        env['XMLS'][key]='verification/net30/native/'+kind+'/'+name+'.xml'
        old={p['reference']:p for p in json.loads((ROOT/'hardware'/parent/'design.json').read_text())['parts']}
        new={p['reference']:p for p in json.loads((ROOT/'hardware'/name/'design.json').read_text())['parts']}
        assert set(old)==set(new)
        changed=[]
        for ref,p in old.items():
            q=new[ref];assert {k:v for k,v in p.items() if k!='nets'}=={k:v for k,v in q.items() if k!='nets'}
            assert set(p['nets'])==set(q['nets'])
            changed.extend({'reference':ref,'pin':n,'before':net,'after':q['nets'][n]} for n,net in p['nets'].items() if net!=q['nets'][n])
        assert len(changed)=={'video':3,'keyboard':8,'bus':4}[kind]
        deltas[kind]=changed
    source=inspect.getsource(original.build).replace("memory_path=ROOT/'sim/net26/isa1_memory_local_phase.sv'","memory_path=ROOT/'sim/net30/isa1_memory_loads.sv'")
    exec(source,env);report=env['build']()
    assert report['connected_pins']==7814 and report['maximum_input_count']==4 and not report['nets_above_four_inputs']
    report.update(date='2026-11-26',scope='NET30 native spare-channel candidate structural audit only; input-only load screening, not electrical/timing/PCB/ERC acceptance.',native_pin_deltas=deltas)
    report['sources'] +=[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in [
        'tools/audit_distributed_loads.py','tools/build_distributed_loads.py','verification/net29/system-pin-loads.json']]
    out=ROOT/'verification/net30/system-pin-loads.json';out.write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    print(json.dumps({'connected_pins':report['connected_pins'],'max_inputs':4,'ics_added':0,'pin_changes':sum(map(len,deltas.values())),'production_released':False}))

if __name__=='__main__':main()
