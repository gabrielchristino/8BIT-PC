import json, pathlib, collections
P=pathlib.Path(__file__).parent
source=json.loads((P/'isa1_rev33_microcode.json').read_text())
expanded=[]; errors=[]
for ins in source['instructions']:
    seq=[]
    for step in ins['steps']:
        kind,expr=step.split(': ',1)
        if kind=='FETCH':
            seq.append(dict(phase='ADDRESS_CAPTURE',addr_source='PC',mar_load=True,mem_oe=False,mem_we=False,read_capture=False,write_data_drive=False,operation=expr))
        elif kind=='READ':
            seq += [dict(phase='READ_ACCESS',addr_source='MAR',mar_load=False,mem_oe=True,mem_we=False,read_capture=False,write_data_drive=False,operation=expr),dict(phase='READ_CAPTURE',addr_source='MAR',mar_load=False,mem_oe=True,mem_we=False,read_capture=True,write_data_drive=False,operation=expr),dict(phase='READ_RELEASE',addr_source='MAR',mar_load=False,mem_oe=False,mem_we=False,read_capture=False,write_data_drive=False,operation='release memory output')]
        elif kind=='WRITE':
            seq += [dict(phase='WRITE_SETUP',addr_source='MAR',mar_load=False,mem_oe=False,mem_we=False,read_capture=False,write_data_drive=True,operation=expr),dict(phase='WRITE_PULSE',addr_source='MAR',mar_load=False,mem_oe=False,mem_we=True,read_capture=False,write_data_drive=True,operation=expr),dict(phase='WRITE_HOLD',addr_source='MAR',mar_load=False,mem_oe=False,mem_we=False,read_capture=False,write_data_drive=True,operation=expr),dict(phase='WRITE_RELEASE',addr_source='MAR',mar_load=False,mem_oe=False,mem_we=False,read_capture=False,write_data_drive=False,operation='release write driver')]
        elif kind=='INTERNAL':
            seq.append(dict(phase='INTERNAL',addr_source='NONE',mar_load=False,mem_oe=False,mem_we=False,read_capture=False,write_data_drive=False,operation=expr))
        else: errors.append((ins['opcode'],step))
    for i,s in enumerate(seq):
        if s['mem_oe'] and (s['mem_we'] or s['write_data_drive']): errors.append((ins['opcode'],i,'memory bus contention'))
        if s['mem_we'] and not s['write_data_drive']: errors.append((ins['opcode'],i,'write without driver'))
        if s['read_capture'] and not s['mem_oe']: errors.append((ins['opcode'],i,'capture without OE'))
        if s['phase']=='WRITE_PULSE' and (i==0 or seq[i-1]['phase']!='WRITE_SETUP'): errors.append((ins['opcode'],i,'missing setup'))
        if s['phase']=='WRITE_HOLD' and (i==0 or seq[i-1]['phase']!='WRITE_PULSE'): errors.append((ins['opcode'],i,'missing hold'))
    expanded.append(dict(opcode=ins['opcode'],mnemonic=ins['mnemonic'],states=seq))
counts=collections.Counter(s['phase'] for x in expanded for s in x['states'])
result={'instruction_count':len(expanded),'total_states':sum(map(lambda x:len(x['states']),expanded)),'max_states':max(len(x['states']) for x in expanded),'phase_counts':dict(counts),'static_invariant_errors':errors,'limitations':['READ and WRITE phases are conceptual and not yet clocked waveforms','PC/SP concurrent updates and source mux feasibility not verified','ROM width, ROM depth, actual chip pinout and timing not verified','no independent functional equivalence check']}
(P/'isa1_rev35_states.json').write_text(json.dumps(expanded,indent=2,ensure_ascii=False)+'\n')
(P/'isa1_rev35_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
assert len(expanded)==19 and not errors
print(json.dumps(result,indent=2))
