import json, pathlib
p=pathlib.Path(__file__).parent
base=json.loads((p/'isa1_rev45_nets.json').read_text())
nets={k:list(v) for k,v in base['nets'].items()}
def add(net,ref,pin):
 s=f'{ref}.{pin}'
 for name,ls in nets.items():
  if s in ls: raise ValueError(f'{s} already on {name}')
 nets.setdefault(net,[]).append(s)
# Two SN74HC74D: FF1/FF2 in U_RST1, FF3 in U_RST2.
# 74HC74 top view: /1CLR=1,1D=2,1CLK=3,/1PRE=4,1Q=5,/1Q=6,GND=7,
# /2Q=8,2Q=9,/2PRE=10,2CLK=11,2D=12,/2CLR=13,VCC=14
for u in ['U_RST1','U_RST2']:
 add('VCC_5V',u,14);add('GND',u,7)
for u,prefix in [('U_RST1',1),('U_RST1',2),('U_RST2',1)]:
 pins=(1,2,3,4,5,6) if prefix==1 else (13,12,11,10,9,8)
 clr,d,clk,pre,q,nq=pins
 add('SUP_RESET_N',u,clr);add('VCC_5V',u,pre);add('SYS_CLK',u,clk)
 add({('U_RST1',1):'VCC_5V',('U_RST1',2):'RST_Q1',('U_RST2',1):'RST_Q2'}[(u,prefix)],u,d)
 add({('U_RST1',1):'RST_Q1',('U_RST1',2):'RST_Q2',('U_RST2',1):'RST_Q3'}[(u,prefix)],u,q)
 add('NC',u,nq)
# unused FF2 of U_RST2: async clear/preset tied inactive, D tied 0, CLK tied 0; Q outputs NC
for pin,net in {13:'VCC_5V',12:'GND',11:'GND',10:'VCC_5V',9:'NC',8:'NC'}.items():add(net,'U_RST2',pin)
# SN74HC08: AND gates PC_CLR_N = SUP_RESET_N & RST_Q2; CPU_RUN = SUP_RESET_N & RST_Q3
# HC08: 1A=1,1B=2,1Y=3,2A=4,2B=5,2Y=6,GND=7,3Y=8,3A=9,3B=10,4Y=11,4A=12,4B=13,VCC=14
for pin,net in {14:'VCC_5V',7:'GND',1:'SUP_RESET_N',2:'RST_Q2',3:'PC_CLR_N',4:'SUP_RESET_N',5:'RST_Q3',6:'CPU_RUN',9:'GND',10:'GND',8:'NC',12:'GND',13:'GND',11:'NC'}.items():add(net,'U_AND',pin)
# Note existing PC_CLK from rev45 is distinct SYS_CLK; explicit join required
nets['SYS_CLK']+=nets.pop('PC_CLK')
# check unique pins; NC is an intentionally unconnected pin listing, not a wired net
allpins=[x for n,ls in nets.items() for x in ls]
assert len(allpins)==len(set(allpins))
assert len([x for x in allpins if x.startswith('U_RST')])==28
assert len([x for x in allpins if x.startswith('U_AND.')])==14
assert 'PC_CLR_N' in nets and 'CPU_RUN' in nets
# Verify sequential synchronous reset behavior for arbitrary PC initial values
checks=0
for initial in range(65536):
 q=[0,0,0];pc=initial
 for edge in range(1,5):
  old=q[:]; clr=old[1];run=old[2]
  if not clr:pc=0
  elif run:pc=(pc+1)&65535
  q=[1,old[0],old[1]]
  if edge<=3:assert pc==0
  else:assert pc==1
  checks+=1
out={'revision':'5.0','status':'partial pin-level netlist, NOT complete schematic','nets':nets,'components':{'SN74HC163D':4,'SN74HC157D':4,'SN74HC74D':2,'SN74HC08D':1},'unresolved':['Supervisor TPS3808G50DBVR pins and CT/Rpullup','Oscillator model and supply','glitch-free write protection','reset release metastability','clock gating/control of PC_LOAD_N and PC_COUNT','ERC and timed gate-level simulation']}
(p/'isa1_rev50_reset_pc_nets.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
(p/'isa1_rev50_results.json').write_text(json.dumps({'pin_assignments':len(allpins),'unique_pin_assignments':len(set(allpins)),'sequential_assertions':checks,'status':'PASS in abstract model'},indent=2))
print('PASS',len(allpins),'pins',checks,'sequential checks')
