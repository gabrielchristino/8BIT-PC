from microcode import ROM,EncodedMachine
import json
n=0
for op in range(256):
 if op in ROM:continue
 m=EncodedMachine(1,1,0);m.rom[0]=op;m.step()
 assert m.halt and m.pc==1 and m.writes==0
 m.reset();m.rom[0]=255;m.step();assert m.halt
 n+=1
print(n);open('invalid_results.json','w').write(json.dumps({'invalid_opcodes':n,'failures':0}))
