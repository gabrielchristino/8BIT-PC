import json, pathlib
P=pathlib.Path(__file__).parent
nets=json.loads((P/'isa1_rev50_reset_pc_nets.json').read_text())['nets']
issues=[]
# Test the actual rev5.0 equations with hostile but possible external controls.
# HC163 /LOAD has priority over ENP/ENT, but synchronous /CLR takes precedence.
for initial in range(65536):
 for load_n in (0,1):
  for count in (0,1):
   q=[0,0,0]; pc=initial
   for edge in range(1,5):
    clr=q[1] # SUP_RESET_N=1 after reset release
    run=q[2]
    if not clr: pc=0
    elif not load_n: pc=0xBEEF # example selected EA/RET load value
    elif count: pc=(pc+1)&65535
    q=[1,q[0],q[1]]
    if edge<=3 and pc!=0:
     issues.append({'initial':initial,'load_n':load_n,'count':count,'edge':edge,'pc':pc,'cpu_run_before_edge':run})
     break
   if issues:break
  if issues:break
 if issues:break
# Net-level safety requirements, cannot be proven from present nets
missing=[n for n in ('SRAM_WE_N','EEPROM_WE_N','POWER_GOOD','OSC_VALID','PC_COUNT_SAFE','PC_LOAD_N_SAFE') if n not in nets]
# Revised contract: while !CPU_RUN force /LOAD=1, COUNT=0; then reset+release 3 edges.
checks=0
for initial in range(65536):
 for request_load in (0,1):
  for request_count in (0,1):
   q=[0,0,0];pc=initial
   for edge in range(1,5):
    run=q[2]; clr=q[1]
    load_n=(request_load if run else 1)
    count=(request_count if run else 0)
    if not clr:pc=0
    elif not load_n:pc=0xBEEF
    elif count:pc=(pc+1)&65535
    q=[1,q[0],q[1]]
    if edge<=3: assert pc==0
    checks+=1
assert issues, 'Expected to detect unsafe uncontrolled /LOAD'
result={'revision':'5.1','audit':'behavioral fault injection and net coverage','rev50_counterexample':issues[0], 'missing_safety_nets':missing,'revised_contract_checks':checks,'revised_contract_pass':True,'electrical_simulation':False,'kicad_erc':False}
(P/'isa1_rev51_results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
