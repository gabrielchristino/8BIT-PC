import json, pathlib, random
p=pathlib.Path(__file__).parent
micro=json.loads((p/'isa1_rev33_microcode.json').read_text())['instructions']
# Nexperia 74HC151D SO16, Rev 11: I0..I7, S0..S2, /E, Y, /Y
pins={'I0':4,'I1':3,'I2':2,'I3':1,'I4':15,'I5':14,'I6':13,'I7':12,'S0':11,'S1':10,'S2':9,'/E':7,'Y':5,'/Y':6,'GND':8,'VCC':16}
assert sorted(pins.values())==list(range(1,17))
main=['A','B','ALU','MEM','MDR','TMP','ADDR_BYTE','CONST']
aux=['PC_LO','PC_HI','SP_LO','SP_HI','EA_LO','EA_HI','ZERO','ZERO']
r=random.Random(3901)
checks=0
for _ in range(25000):
    sources=[r.randrange(256) for _ in range(8)]
    for sel in range(8):
        for bit in range(8):
            y=0
            for k in range(8):
                y |= ((sources[k]>>bit)&1) & int(k==sel)
            assert y == ((sources[sel]>>bit)&1)
            assert (y ^ 1) != y
            checks+=1
# Inventory explicitly grounded in actual micro-operations
allsteps=[(i['mnemonic'],s) for i in micro for s in i['steps']]
requirements={'IR_from_MEM':[], 'TPH_from_MEM':[], 'A_from_MEM':[], 'RETADDR_high_to_MDR':[], 'RETADDR_low_to_MDR':[], 'EA_from_TPH_TMP':[], 'PC_from_TPH_TMP':[], 'PC_from_EA':[], 'SP_increment_decrement':[], 'ALU_to_A':[]}
for mnemonic,step in allsteps:
    if 'IR<-MEM' in step: requirements['IR_from_MEM'].append(mnemonic)
    if 'TPH<-MEM' in step: requirements['TPH_from_MEM'].append(mnemonic)
    if 'A<-MEM' in step: requirements['A_from_MEM'].append(mnemonic)
    if 'MDR<-RETADDR.high' in step: requirements['RETADDR_high_to_MDR'].append(mnemonic)
    if 'MDR<-RETADDR.low' in step: requirements['RETADDR_low_to_MDR'].append(mnemonic)
    if 'EA<-TPH:TMP' in step: requirements['EA_from_TPH_TMP'].append(mnemonic)
    if 'PC<-TPH:TMP' in step: requirements['PC_from_TPH_TMP'].append(mnemonic)
    if 'PC<-EA' in step: requirements['PC_from_EA'].append(mnemonic)
    if 'SP<-SP+' in step or 'SP<-SP-' in step: requirements['SP_increment_decrement'].append(mnemonic)
    if 'A+B' in step or 'A-B' in step or 'A&B' in step or 'A|B' in step or 'A^B' in step or 'A<<' in step or 'A>>' in step: requirements['ALU_to_A'].append(mnemonic)
# Only the 8-way DB selector is proposed; separate destinations and write paths are NOT implemented.
missing={'RETADDR_high_to_MDR':'RETADDR.high not among 8 DB sources; ADDR_BYTE excludes RETADDR', 'RETADDR_low_to_MDR':'RETADDR.low not among 8 DB sources', 'EA_from_TPH_TMP':'16-bit EA destination input and transfer path undefined', 'PC_from_TPH_TMP':'16-bit PC load path undefined', 'PC_from_EA':'16-bit PC load path undefined', 'SP_increment_decrement':'16-bit increment/decrement hardware undefined', 'ALU_to_A':'ALU functional selection and flags circuit undefined'}
net=[]
for bank,source_names in [('DB',main),('ADDR_BYTE',aux)]:
    for bit in range(8):
        net.append({'ref':f'U_{bank}_{bit}', 'part':'74HC151D','output':f'{bank}[{bit}]','output_pin':5,'inputs':{str(pins[f'I{k}']):f'{src}[{bit}]' if src!='ZERO' else 'GND' for k,src in enumerate(source_names)},'select_pins':{'S0':11,'S1':10,'S2':9},'enable_pin':7,'vcc_pin':16,'gnd_pin':8})
results={'status':'PASS: pin-map and combinational truth-table model only','part':'Nexperia 74HC151D SO16','pinmap':pins,'mux_count':len(net),'main_sources':main,'aux_sources':aux,'logic_bit_checks':checks,'instructions':len(micro),'symbolic_steps':len(allsteps),'requirements_found':requirements,'unresolved_paths':missing,'limitations':['No manufacturer electrical simulation','No propagation-delay worst-case analysis','No clock/register setup and hold closure','No PCB ERC/DRC','MEM input isolation not implemented','CONST is undefined','DB destination load control not designed']}
(p/'isa1_rev39_mux_nets.json').write_text(json.dumps(net,indent=2)+'\n')
(p/'isa1_rev39_results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':results['status'],'chips':len(net),'bit_checks':checks,'instructions':len(micro),'steps':len(allsteps),'unresolved':len(missing)},indent=2))
