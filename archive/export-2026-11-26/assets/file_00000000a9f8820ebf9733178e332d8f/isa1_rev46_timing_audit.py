import json
from pathlib import Path
p=Path(__file__).parent
net=json.loads((p/'isa1_rev45_nets.json').read_text())['nets']
assert net['PC_CLK']==[f'U_PC{i}.2' for i in range(4)]
assert net['PC_COUNT']==['U_PC0.7','U_PC0.10','U_PC1.7','U_PC2.7','U_PC3.7']
for i in range(3): assert net[f'PC_RCO{i}']==[f'U_PC{i}.15',f'U_PC{i+1}.10']
for i in range(4): assert f'U_PC{i}.9' in net['PC_LOAD_N']
# Structural model: RCO_i = ENT_i & (nibble_i == 15); all ENP=PC_COUNT.
count_checks=0
for v in range(65536):
 for en in (0,1):
  n=[(v>>(4*i))&15 for i in range(4)]
  ents=[en]
  for i in range(3): ents.append(ents[-1] & int(n[i]==15))
  updated=sum(((n[i]+int(bool(en and ents[i])))&15)<<(4*i) for i in range(4))
  assert updated==(v+en)&65535
  count_checks+=1
# illustrative, NOT datasheet-based, budget arithmetic in ns
scenarios=[
 {'name':'EXAMPLE_A_not_datasheet','clock_period_ns':1000,'clk_to_q_ns':40,'rco_stage_ns':35,'setup_ent_ns':25,'skew_ns':15,'margin_ns':50},
 {'name':'EXAMPLE_B_not_datasheet','clock_period_ns':200,'clk_to_q_ns':40,'rco_stage_ns':35,'setup_ent_ns':25,'skew_ns':15,'margin_ns':50},
]
for s in scenarios:
 s['cascade_path_ns']=s['clk_to_q_ns']+3*s['rco_stage_ns']+s['setup_ent_ns']+s['skew_ns']+s['margin_ns']
 s['example_pass']=s['clock_period_ns']>=s['cascade_path_ns']
result={'revision':'4.6','status':'structural pass; physical timing NOT verified','count_checks':count_checks,'clock_common':True,'rco_is_not_clock':True,'illustrative_only_scenarios':scenarios,'required_datasheet_parameters':['74HC163 clock-to-Q max','74HC163 ENT-to-RCO max (or appropriate propagation)','74HC163 ENT setup/hold','74HC163 /LOAD setup/hold','74HC163 /CLR setup/hold','74HC157 select-to-Y max','74HC157 input-to-Y max','74HC163 D setup/hold','actual clock skew, fanout, PCB capacitance, temperature and VCC'], 'blocking_issues':['EA and RET sources not yet electrically specified','reset supervisor and guaranteed startup clock not designed','timing not verified against manufacturer worst-case limits','control signals must be registered or hazard-free before sampling']}
(p/'isa1_rev46_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('PASS',count_checks,'counter cases; electrical timing remains unverified')
