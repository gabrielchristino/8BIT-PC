import json
from pathlib import Path
p=Path(__file__).parent
old=json.loads((p/'isa1_rev33_microcode.json').read_text())
rows=[]
for ins in old['instructions']:
    steps=[]
    for s in ins['steps']:
        if ins['mnemonic'] in ('CALL','RET','PUSH_A','POP_A'):
            continue
        if s.startswith(('READ:','WRITE:')):
            steps.extend([{'phase':'ISSUE','operation':s},{'phase':'WAIT','operation':s},{'phase':'COMMIT','operation':s}])
        else: steps.append({'phase':'INTERNAL','operation':s})
    if steps: rows.append({'opcode':ins['opcode'],'mnemonic':ins['mnemonic'],'steps':steps})
# Explicit stack convention: SP points to occupied top, initial 8000.
checks=0
for sp0 in (0x8000,0x7000,0x100):
 for ret in range(65536):
    sp=sp0; mem={}
    for byte in (ret>>8,ret&255):
        addr=sp-1; mem[addr]=byte; sp=addr
    lo=mem[sp]; sp+=1; hi=mem[sp]; sp+=1
    assert (hi<<8|lo)==ret and sp==sp0
    checks+=1
for r in rows:
 for i,s in enumerate(r['steps']):
    if s['phase']=='WAIT':
        assert r['steps'][i-1]['phase']=='ISSUE' and r['steps'][i+1]['phase']=='COMMIT'
result={'stack_roundtrips':checks,'expanded_instructions':len(rows),'deferred_stack_instructions':['CALL','RET','PUSH_A','POP_A'],'missing_opcodes':old['audit']['excluded_unimplemented_opcodes'],'limitations':'Structural expansion only; no execution of expanded microcode, no electrical simulation.'}
(p/'isa1_rev76_microcode.json').write_text(json.dumps({'instructions':rows,'audit':result},indent=2))
print(result)

