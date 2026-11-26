import json,collections,pathlib
p=pathlib.Path(__file__).parent
j=json.loads((p/'isa1_rev52_corrected_nets.json').read_text()); nets=j['nets']
# Explicit pin direction tables from 74HC family top-view pinouts.
HC163={1:'I',2:'I',3:'I',4:'I',5:'I',6:'I',7:'I',8:'P-',9:'I',10:'I',11:'O',12:'O',13:'O',14:'O',15:'O',16:'P+'}
HC157={1:'I',2:'I',3:'I',4:'O',5:'I',6:'I',7:'O',8:'P-',9:'O',10:'I',11:'I',12:'O',13:'I',14:'I',15:'I',16:'P+'}
HC74={1:'I',2:'I',3:'I',4:'I',5:'O',6:'O',7:'P-',8:'O',9:'O',10:'I',11:'I',12:'I',13:'I',14:'P+'}
HC08={1:'I',2:'I',3:'O',4:'I',5:'I',6:'O',7:'P-',8:'O',9:'I',10:'I',11:'O',12:'I',13:'I',14:'P+'}
HC04={1:'I',2:'O',3:'I',4:'O',5:'I',6:'O',7:'P-',8:'O',9:'I',10:'O',11:'I',12:'O',13:'I',14:'O'}
HC32=HC08
parts={**{f'U_PC{i}':HC163 for i in range(4)},**{f'U_MUX{i}':HC157 for i in range(4)},'U_RST1':HC74,'U_RST2':HC74,'U_AND':HC08,'U_INV':HC04,'U_OR':HC32}
issues=[]; pin_net={}; stats=collections.Counter(); floating=[]
for net, pins in nets.items():
 for s in pins:
  ref,num=s.split('.');num=int(num)
  if ref not in parts or num not in parts[ref]:issues.append(f'unknown {s}');continue
  if s in pin_net:issues.append(f'duplicate {s} {pin_net[s]} {net}')
  pin_net[s]=net
for ref,mapping in parts.items():
 for pin,kind in mapping.items():
  s=f'{ref}.{pin}'
  if s not in pin_net:issues.append(f'unassigned {s}')
  elif kind=='P+' and pin_net[s] not in ('VCC','VCC_5V'):issues.append(f'power mismatch {s} {pin_net[s]}')
  elif kind=='P-' and pin_net[s]!='GND':issues.append(f'ground mismatch {s} {pin_net[s]}')
for net,pins in nets.items():
 if net=='NC':continue
 drivers=[s for s in pins if parts[s.split('.')[0]][int(s.split('.')[1])]=='O']
 sinks=[s for s in pins if parts[s.split('.')[0]][int(s.split('.')[1])]=='I']
 if len(drivers)>1:issues.append(f'output collision {net}: {drivers}')
 if not drivers and net not in ('GND','VCC'):
  floating.append({'net':net,'inputs':len(sinks),'note':'external input or floating; not resolved in this partial netlist'})
 stats['nets']+=1
 if drivers:stats['driven_nets']+=1
 if len(drivers)==1 and not sinks:stats['output_only_nets']+=1
# reset chain and LOAD precedence checks
assert {'U_PC0.9','U_PC1.9','U_PC2.9','U_PC3.9'} <= set(nets['PC_LOAD_N_SAFE'])
assert {'U_PC0.7','U_PC1.7','U_PC2.7','U_PC3.7'} <= set(nets['PC_COUNT_SAFE'])
result={'revision':'5.3','status':'static audit of partial netlist, not electrical validation','components':len(parts),'assigned_pins':len(pin_net),'nets_excluding_NC':stats['nets'],'driven_nets':stats['driven_nets'],'output_only_nets':stats['output_only_nets'],'external_or_unresolved_nets':floating,'errors':issues,'erc_executed':False,'timing_verified':False,'power_integrity_verified':False}
(p/'isa1_rev53_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'components':result['components'],'assigned_pins':result['assigned_pins'],'errors':issues,'unresolved_nets':len(floating),'output_only_nets':stats['output_only_nets']},indent=2))
