def convert(source=None,destination=None):
    source=source or VERIFY/'load_distributed_bus.xml';destination=destination or OUT/'load_distributed_bus_netlist.sv'
    defs=json.loads((OUT/'package-functions.json').read_text());expected={p['reference']:p for p in json.loads((OUT/'design.json').read_text())['parts']};root=ET.parse(source).getroot();nets=set();actual={}
    for net in root.findall('./nets/net'):
        n=net.get('name').removeprefix('/');nets.add(n)
        for p in net.findall('node'):
            key=p.get('ref'),p.get('pin')
            if key in actual:raise ValueError('Multiple nets '+str(key))
            actual[key]=n
    ins,outs=ports();drivers={n:[('external','strong')] for n in [*ins,'+5V','GND']};inputs=[];loads={};lines=[];seen=set();ram_writers=[];vram_writers=[]
    for c in root.findall('./components/comp'):
        ref=c.get('ref');kind=expected[ref]['part'];seen.add(ref);fs={}
        value='100nF' if kind=='C' else '3.3k' if kind=='R' else kind
        if c.findtext('value')!=value:raise ValueError('Value changed '+ref)
        for pin,s in defs[kind]['pins'].items():
            n=actual.get((ref,pin));typ=s['type'];name=s['name']
            if typ in ('input','power_in','bidirectional') and (not n or n.startswith('unconnected-')):raise ValueError('Floating input '+ref+'/'+pin)
            if name in ('VCC','GND') and n!={'VCC':'+5V','GND':'GND'}[name]:raise ValueError('Wrong power '+ref)
            if n:fs[name]=sig(n)
            if typ=='input':inputs.append((ref,pin,n));loads.setdefault(n,[]).append(ref+'/'+pin)
            if typ in ('output','bidirectional') and n:drivers.setdefault(n,[]).append((ref+'/'+pin,'tri' if typ=='bidirectional' or kind=='SN74AHC125' else 'strong'))
        def vec(prefix,w):return '{'+','.join(fs[f'{prefix}{i}'] for i in reversed(range(w)))+'}'
        if kind=='C':continue
        if kind=='R':
            if fs['1']!="1'b1" or not re.fullmatch(r'n_(RAM|VRAM|ROM)_IO_[0-7]',fs['2']):raise ValueError('Pull-up wiring '+ref)
            lines.append(f"pullup({fs['2']});");continue
        if kind in ('AS7C256A_28SOJ','AT28C256_28PDIP'):
            ro=kind.startswith('AT');seed=167 if ro else 49 if ref=='U1' else 93
            if ro and fs['WE_N']!="1'b1":raise ValueError('EEPROM WE is not permanently protected HIGH')
            lines.append(f"wire {ref}_drive; parallel_memory_32k #(.TIMED(TIMED),.READ_ONLY({int(ro)}),.SEED({seed}),.EARLY_ON(EARLY_ON)) {ref}({vec('A',15)},{fs['CE_N']},{fs['OE_N']},{fs['WE_N']},{vec('IO',8)},checks_valid,{ref}_drive);")
        elif kind=='SN74AHCT157':lines.append(f"assign #MUX_T {vec('Y',4)}={fs['G_N']} ? 4'b0 : {fs['SELECT']} ? {vec('B',4)} : {vec('A',4)};")
        elif kind=='SN74HCT244':
            for i in range(8):lines.append(f"assign #RECEIVER_T {fs[f'Y{i}']}={fs[f'OE{i//4}_N']} ? 1'bz : {fs[f'A{i}']};")
        elif kind in ('SN74AHC08','SN74AHC32'):
            op='&' if kind=='SN74AHC08' else '|'
            for i in range(4):
                if f'Y{i}' in fs:lines.append(f"assign #GATE_T {fs[f'Y{i}']}={fs[f'A{i}']} {op} {fs[f'B{i}']};")
        elif kind=='SN74AHC04':
            for i in range(6):
                if f'Y{i}' in fs:lines.append(f"assign #GATE_T {fs[f'Y{i}']}=~{fs[f'A{i}']};")
        elif kind=='SN74AHC125':
            for i in range(4):
                if f'Y{i}' not in fs:continue
                state=f'{ref}_drive{i}';lines.append(f"wire {state};assign #(BUF_ON,BUF_OFF) {state}=~{fs[f'OE{i}_N']};")
                lines.append(f"assign #(GATE_T,GATE_T,BUF_OFF) {fs[f'Y{i}']}={fs[f'OE{i}_N']} ? 1'bz : {fs[f'A{i}']};")
                n=fs[f'Y{i}']
                if n.startswith('n_RAM_IO_'):ram_writers.append(state)
                if n.startswith('n_VRAM_IO_'):vram_writers.append(state)
        else:raise ValueError('No model '+kind)
    if seen!=set(expected):raise ValueError('Inventory mismatch')
    for ref,pin,n in inputs:
        ds=drivers.get(n,[])
        if not ds:raise ValueError('Undriven '+ref+'/'+pin)
        if len(ds)>1 and not re.fullmatch(r'(RAM|VRAM|ROM)_IO_[0-7]',n):raise ValueError('Multiple drivers '+n)
    for n,ds in drivers.items():
        if len(ds)>1 and not re.fullmatch(r'(RAM|VRAM)_IO_[0-7]',n):raise ValueError('Multiple drivers '+n)
        if re.fullmatch(r'(RAM|VRAM)_IO_[0-7]',n) and (len(ds)!=2 or any(t!='tri' for _,t in ds)):raise ValueError('Invalid memory bus driver set '+n)
    for n in outs:
        if len(drivers.get(n,[]))!=1:raise ValueError('Undriven output '+n)
    if len(ram_writers)!=8 or len(vram_writers)!=8:raise ValueError('Missing write drivers')
    lines.append('wire ram_write_driving=|{'+','.join(ram_writers)+'};wire vram_write_driving=|{'+','.join(vram_writers)+'};')
    lines.append('always @(U1_drive or ram_write_driving)if(U1_drive===1 && ram_write_driving===1)$fatal(1,"SRAM output and write buffer overlap RAM");')
    lines.append('always @(U2_drive or vram_write_driving)if(U2_drive===1 && vram_write_driving===1)$fatal(1,"SRAM output and write buffer overlap VRAM");')
    names=[sig(n) for n in (nets|set(ins)) if n not in ('+5V','GND')]
    if len(names)!=len(set(names)):raise ValueError('Name collision')
    header=['`timescale 1ns/1ps','// GENERATED from actual KiCad XML. Models/fixtures are not physical validation.',
      'module load_distributed_bus_netlist #(parameter TIMED=0,EARLY_ON=0)(input wire reset_n,power_good,vram_owner,data_drive,oe_n,we_n,input wire [14:0] ram_address,vram_address,rom_address,video_address,input wire [7:0] write_data,io_data,input wire [3:0] cs_n,select,output wire [7:0] read_data,video_data);',
      'localparam GATE_T=TIMED?10:0,MUX_T=TIMED?12:0,RECEIVER_T=TIMED?42:0,BUF_ON=TIMED?(EARLY_ON?0:10):0,BUF_OFF=TIMED?10:0;',
      'wire checks_valid=reset_n && power_good;']
    header+=['wire '+n+';' for n in sorted(names)];header+=[f'assign {sig(n)}={v};' for n,v in ins.items()]
    lines+=[f'assign {v}={sig(n)};' for n,v in outs.items()];lines+=['endmodule'];destination.write_text('\n'.join(header+lines)+'\n')
    return {'date':'2026-11-25','components':len(seen),'ics':sum(p['part'] not in ('C','R') for p in expected.values()),'pins':sum(len(p['nets']) for p in expected.values()),'no_connects':sum(n is None for p in expected.values() for n in p['nets'].values()),'max_signal_input_loads':max(len(v) for n,v in loads.items() if n not in ('+5V','GND')),'failures':[],'scope':'Pin graph and digital fanout; electrical load/PCB/analog/PVT closure pending'}
