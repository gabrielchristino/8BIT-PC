import json, pathlib, collections
root=pathlib.Path(__file__).parent
j=json.loads((root/'isa1_rev33_microcode.json').read_text())
steps=[(i['mnemonic'],s) for i in j['instructions'] for s in i['steps']]
needs={
 'PC_16':2,'SP_16':2,'MAR_16':2,'EA_16':2,'RETADDR_16':2,
 'A_8':1,'B_8':1,'IR_8':1,'TMP_8':1,'TPH_8':1,'MDR_8':1,
}
assert len(j['instructions'])==19
assert sum(len(i['steps']) for i in j['instructions'])==101
assert any('CALL' in i['mnemonic'] for i in j['instructions'])
assert any('RET' == i['mnemonic'] for i in j['instructions'])
assert any('EA' in s for _,s in steps)
result={'reference':'rev33 symbolic microoperations','instructions':len(j['instructions']),'symbolic_steps':len(steps),'provisional_register_bytes':sum(needs.values()),'register_allocation':needs,'notes':['Register allocation is a conservative candidate, not a proven minimum.','No electrical timing, pin-level netlist or PCB verification performed.']}
(root/'isa1_rev34_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,indent=2,ensure_ascii=False))
