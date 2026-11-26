import json, pathlib, copy
P=pathlib.Path(__file__).parent
src=json.loads((P/'isa1_rev50_reset_pc_nets.json').read_text())
n=copy.deepcopy(src['nets'])
def rm(net,pin):
 n[net].remove(pin)
 if not n[net]:del n[net]
def add(net,*pins):n.setdefault(net,[]).extend(pins)
# Move PC /LOAD to safe OR gate, PC count enables to spare AND gate
for i in range(4):rm('PC_LOAD_N',f'U_PC{i}.9')
for pin in ['U_PC0.7','U_PC0.10','U_PC1.7','U_PC2.7','U_PC3.7']:rm('PC_COUNT',pin)
# Spare AND gate 3: 9,10 -> 8; remove its grounded inputs and NC output
for pin in ['U_AND.9','U_AND.10']:rm('GND',pin)
rm('NC','U_AND.8')
add('PC_COUNT_REQ','U_AND.9')
add('CPU_RUN','U_AND.10','U_INV.1')
add('PC_COUNT_SAFE','U_AND.8','U_PC0.7','U_PC0.10','U_PC1.7','U_PC2.7','U_PC3.7')
# HC04 inverter gate 1: pin 1 in, 2 out; 3-4,5-6,9-8,11-10,13-12 unused
add('NOT_CPU_RUN','U_INV.2','U_OR.2')
add('PC_LOAD_N_REQ','U_OR.1')
add('PC_LOAD_N_SAFE','U_OR.3',*(f'U_PC{i}.9' for i in range(4)))
add('VCC_5V','U_INV.14','U_OR.14')
add('GND','U_INV.7','U_OR.7','U_INV.3','U_INV.5','U_INV.9','U_INV.11','U_INV.13','U_OR.4','U_OR.5','U_OR.9','U_OR.10','U_OR.12','U_OR.13')
add('NC','U_INV.4','U_INV.6','U_INV.8','U_INV.10','U_INV.12','U_OR.6','U_OR.8','U_OR.11')
# 74HC32 unused gate inputs are tied low; outputs unconnected.
# Existing HC08 gate4 inputs 12,13 grounded, output 11 NC.
allpins={}
for net,pins in n.items():
 for p in pins:
  assert p not in allpins,(p,net,allpins.get(p))
  allpins[p]=net
for prefix,size in [('U_PC0',16),('U_PC1',16),('U_PC2',16),('U_PC3',16),('U_MUX0',16),('U_MUX1',16),('U_MUX2',16),('U_MUX3',16),('U_RST1',14),('U_RST2',14),('U_AND',14),('U_INV',14),('U_OR',14)]:
 missing=[f'{prefix}.{i}' for i in range(1,size+1) if f'{prefix}.{i}' not in allpins]
 assert not missing,(prefix,missing)
# Check exact expected pin mapping and no NC used as a real bus.
assert n['PC_COUNT_SAFE']==['U_AND.8','U_PC0.7','U_PC0.10','U_PC1.7','U_PC2.7','U_PC3.7']
assert set(n['PC_LOAD_N_SAFE'])=={'U_OR.3',*(f'U_PC{i}.9' for i in range(4))}
assert set(n['NOT_CPU_RUN'])=={'U_INV.2','U_OR.2'}
# Exhaustively test all initial PC states, four request combos, and four rising edges.
checks=0
for initial in range(65536):
 for load_req in (0,1):
  for count_req in (0,1):
   pc=initial;q=[0,0,0]
   for edge in range(1,5):
    run=q[2];clr=q[1]
    load_safe=load_req or not run
    count_safe=count_req and run
    if not clr:pc=0
    elif not load_safe:pc=0xBEEF
    elif count_safe:pc=(pc+1)&65535
    if edge<=3:assert pc==0,(initial,load_req,count_req,edge,pc)
    q=[1,q[0],q[1]]
    checks+=1
# Additional exhaustive truth table for safety equations
truth=[]
for run in (0,1):
 for load in (0,1):
  for count in (0,1):
   safe_load=int(bool(load or not run));safe_count=int(bool(count and run))
   assert run or (safe_load==1 and safe_count==0)
   truth.append({'CPU_RUN':run,'PC_LOAD_N_REQ':load,'PC_COUNT_REQ':count,'PC_LOAD_N_SAFE':safe_load,'PC_COUNT_SAFE':safe_count})
output={'revision':'5.2','status':'partial intent netlist, not EDA schematic','parts_added':{'U_INV':'SN74HC04D','U_OR':'SN74HC32D'},'nets':n,'pin_count':len(allpins),'logical_checks':checks,'truth_table':truth,'verified_electrical':False,'erc':False}
(P/'isa1_rev52_corrected_nets.json').write_text(json.dumps(output,indent=2))
(P/'isa1_rev52_results.json').write_text(json.dumps({k:output[k] for k in ['revision','pin_count','logical_checks','truth_table','verified_electrical','erc']},indent=2))
print('PASS:',len(allpins),'pins;',checks,'checks;',len(n),'net labels')
