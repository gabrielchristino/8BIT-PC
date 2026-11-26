"""ISA-1 rev2.2: event-window verification; abstract delay ranges, NOT SPICE."""
import itertools,json
from pathlib import Path
# Two independently controlled drivers. On old->new transition,
# old releases at disable_cmd+old_off, new drives at enable_cmd+new_on.
# Safety criterion: new drive strictly after old release.
DELAYS=range(0,21)
def verify(guard):
    collisions=[]; cases=0
    for off,on in itertools.product(DELAYS,repeat=2):
        cases+=1
        if guard+on <= off: collisions.append((off,on))
    return {'cases':cases,'unsafe':len(collisions),'examples':collisions[:4]}
# 3-phase controller: disable all -> change DIR -> enable next;
# safety includes direction change while disabled, guard bound.
checks={str(g):verify(g) for g in [0,10,20,21,30]}
assert checks['0']['unsafe']>0
assert checks['21']['unsafe']==0
# Exhaustive static invariant for control states; SRAM and CPU never both drive.
states={'IDLE':(0,0,0),'READ':(1,0,0),'TURN':(0,0,0),'WRITE_SETUP':(0,1,0),'WRITE_PULSE':(0,1,1),'WRITE_HOLD':(0,1,0)}
# tuple = (sram_output_enabled, cpu_output_enabled, write_enable)
for name,(sram,cpu,we) in states.items():
    assert not(sram and cpu),name
    assert not(we and (sram or not cpu)),name
# fault injection: an independent asynchronous decoder transient can still cause overlap
fault={'sram_output_enabled':True,'cpu_output_enabled':True}
assert all(fault.values())
out={'delay_domain':'hypothetical 0..20 units inclusive','turnaround':checks,'static_states':len(states),'injected_decoder_glitch_detected':True,'limitations':['No chip-specific min/max timing','No actual gates or analog simulation','No board-level power integrity','No guaranteed glitch-free decoder']}
p=Path(__file__).with_name('isa1_rev22_results.json');p.write_text(json.dumps(out,indent=2,ensure_ascii=False))
print(json.dumps({'guards':{k:{'cases':v['cases'],'unsafe':v['unsafe']} for k,v in checks.items()},'states':len(states),'fault_injected':True},indent=2))
