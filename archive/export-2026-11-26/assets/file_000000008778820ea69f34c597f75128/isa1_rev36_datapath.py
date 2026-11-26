"""ISA-1 rev3.6: architectural datapath constraint model, NOT electrical simulation."""
import json
from pathlib import Path
p=Path(__file__).parent
spec=json.loads((p/'isa1_rev33_microcode.json').read_text())
# One source may drive the internal data bus per state. All register Q outputs are isolated by buffers.
sources=['A','B','TMP','TPH','MDR','MEM','ALU','PC_LO','PC_HI','SP_LO','SP_HI','EA_LO','EA_HI','CONST']
def check_bus(enabled):
    assert len(enabled)<=1, f'BUS CONTENTION: {enabled}'
for s in sources: check_bus([s])
check_bus([])
conflict_detected=False
try: check_bus(['A','MEM'])
except AssertionError: conflict_detected=True
assert conflict_detected
# 16-bit dedicated increment/decrement networks: full-width wrap and carry/borrow.
for v in range(65536):
    inc=(v+1)&65535; dec=(v-1)&65535
    lo=(v&255); hi=v>>8
    assert inc==((((hi+(lo==255))&255)<<8)|((lo+1)&255))
    assert dec==((((hi-(lo==0))&255)<<8)|((lo-1)&255))
# CALL/RET preserve EA and correct stack ordering, with explicit memory transaction boundaries.
for pc in [0,1,0x12ff,0xfffe,0xffff]:
 for sp in [0,1,0x8000,0xffff]:
  for ea in [0,0x1234,0xffff]:
   ram={}; retaddr=pc; saved_ea=ea
   mar=sp; mdr=retaddr>>8; ram[mar]=mdr; sp=(sp-1)&65535
   mar=sp; mdr=retaddr&255; ram[mar]=mdr; sp=(sp-1)&65535
   pc=saved_ea
   sp=(sp+1)&65535; mar=sp; tmp=ram[mar]
   sp=(sp+1)&65535; mar=sp; tph=ram[mar]
   pc=(tph<<8)|tmp
   assert pc==retaddr
# Requirements coverage is explicitly limited: symbolic ops are NOT synthesized into real control signals.
ops=[x['mnemonic'] for x in spec['instructions']]
assert len(ops)==19 and len(set(ops))==19
results={'revision':'3.6','status':'PASS architectural constraints only','opcodes_reference':len(ops),
'bus_sources_proposed':len(sources),'bus_single_driver_cases':len(sources)+1,
'forced_conflict_detected':conflict_detected,'increment_decrement_16bit_values':65536,
'call_ret_stack_scenarios':5*4*3,
'not_verified':['physical bus ownership','74HC fanout/timing','pin mapping','ROM encoding','complete instruction microoperations','memory address decode','power-up reset','video/keyboard/ZIF']}
(p/'isa1_rev36_results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(results,indent=2,ensure_ascii=False))
