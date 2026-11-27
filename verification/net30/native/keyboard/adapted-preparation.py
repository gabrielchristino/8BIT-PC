def make(kind):
    oldname={'video':'phase_drain_video','reset':'phase_drain_reset','keyboard':'keyboard_500'}[kind]
    name='load_distributed_'+kind
    out=ROOT/'hardware'/name;verify=ROOT/'verification/net30/native'/kind
    out.mkdir(parents=True,exist_ok=True);verify.mkdir(parents=True,exist_ok=True)
    defs=copy.deepcopy(json.loads((ROOT/'hardware'/oldname/'package-functions.json').read_text()))
    parts=copy.deepcopy(json.loads((ROOT/'hardware'/oldname/'design.json').read_text())['parts'])
    def part(ref):return next(p for p in parts if p['reference']==ref)
    def connect(ref,fn,net,expected):
        p=part(ref);pin=next(pin for pin,s in defs[p['part']]['pins'].items() if s['name']==fn)
        assert p['nets'][pin]==expected,(kind,ref,fn,p['nets'][pin],expected)
        p['nets'][pin]=net
    def ports():
        ins,outs=video.ports();ins.update(PHASE_INIT_N='phase_init_n',BANK_SYNC1='bank_sync1');outs['BANK_ARM']='bank_arm'
        return ins,outs
    if kind=='video':
        # The old local AND becomes a physical noninverting phase1 buffer.
        for fn,n,e in [('A3','P1','SAFE'),('B3','+5V','PHASE_RUN'),('Y3','LOCAL_RESET_CLK','LOCAL_RESET_N')]:connect('U24',fn,n,e)
        fs={'CLK0':'LOCAL_RESET_CLK','CLR0_N':'SAFE','PRE0_N':'+5V','D0':'+5V','Q0':'LOCAL_RESET_STAGE1',
            'CLK1':'LOCAL_RESET_CLK','CLR1_N':'SAFE','PRE1_N':'+5V','D1':'LOCAL_RESET_STAGE1','Q1':'LOCAL_RESET_N','VCC':'+5V','GND':'GND'}
        parts.append({'reference':'U37','part':'SN74AHC74','x':158.75,'y':495.3,
            'nets':{pin:fs.get(s['name']) for pin,s in defs['SN74AHC74']['pins'].items()}})
        parts.append({'reference':'C37','part':'C','x':179.07,'y':464.82,'nets':{'1':'+5V','2':'GND'}})
        previous=video;namespace='NET30V'
        emitter=video.original._emitter.replace('video_raster',name).replace('NET14B',namespace).replace('NET-14B','NET-26V')
        converter=video.converter.replace('video_common_clock',name)
        converter=once(converter,'input wire master,reset_n,power_good,','input wire master,reset_n,power_good,phase_init_n,bank_sync1,')
        converter=once(converter,'hsync_n,vsync_n,ready,output wire','hsync_n,vsync_n,ready,bank_arm,output wire')
        package_symbol=lambda k,s:tuple(x.replace('NET02:',namespace+':') if isinstance(x,str) else x for x in video.old_symbol(k,s))
    elif kind=='reset':
        # Access clock is now the actual BACKEND wire, not another buffer.
        # Retain the package for keyboard/bank branches and tie off this channel.
        for fn,n,e in [('A1','GND','BACKEND_ROOT'),('OE1_N','+5V','GND'),('Y1',None,'ACCESS_CLK')]:connect('U8',fn,n,e)
        previous=reset;namespace='NET26R'
        emitter=reset.emitter.replace('clocked_reset',name).replace('NET23',namespace).replace('NET-23','NET-26R')
        converter=reset.converter.replace('clocked_reset',name)
        converter=once(converter,"'BACKEND':'backend_source'","'BACKEND':'backend_source','BANK_ARM':'bank_arm'")
        converter=once(converter,"'MASTER':'master_source'}","'MASTER':'master_source','DELAY_CLEAR_N':'phase_init_n','RESET_SYNC1':'bank_sync1'}")
        converter=once(converter,"'ACCESS_CLK':'access_clk'","'BACKEND':'access_clk'")
        converter=once(converter,'input wire raw_safe_n,backend_source,osc_power_valid,','input wire raw_safe_n,backend_source,osc_power_valid,bank_arm,')
        converter=once(converter,'keyboard_clk,cpu_source,master_source);','keyboard_clk,cpu_source,master_source,phase_init_n,bank_sync1);')
        package_symbol=lambda k,s:tuple(x.replace('NET23:',namespace+':') if isinstance(x,str) else x for x in reset.package_symbol(k,s))
    else:
        defs['SN74AHC174']=copy.deepcopy(json.loads((ROOT/'hardware/common_request/package-functions.json').read_text())['SN74AHC174'])
        assert {p:s['name'] for p,s in defs['SN74HC174']['pins'].items()}=={p:s['name'] for p,s in defs['SN74AHC174']['pins'].items()}
        p=part('U1');assert p['part']=='SN74HC174';p['part']='SN74AHC174'
        previous=keyboard;namespace='NET30K'
        emitter=keyboard.previous._emitter.replace('mmio_keyboard',name).replace('NET15',namespace).replace('NET-15','NET-26K')
        converter=keyboard.converter.replace(keyboard.marker,keyboard.addition+keyboard.marker.lstrip())
        converter=converter.replace('keyboard_500',name)
        old="        elif kind=='SN74HC174':"
        addition='''        elif kind=='SN74AHC174':lines.append(f"net19_ahc174 #(.TIMED(TIMED)) {ref}({fs['CLK']},{fs['CLR_N']},{vec('D',6)},{vec('Q',6)});")
        elif kind=='SN74HC174':'''
        converter=once(converter,old,addition)
        package_symbol=lambda k,s:tuple(x.replace('NET17:',namespace+':') if isinstance(x,str) else x for x in keyboard.package_symbol(k,s))
    published=json.loads((ROOT/'hardware'/('local_phase_'+kind)/'design.json').read_text())['parts']
    assert parts==published,'Prepared ancestor does not equal published NET26'
    modify(kind,defs,parts)
    old_ports=keyboard.ports if kind=='keyboard' else ports
    def system_ports():
        ins,outs=old_ports()
        if kind=='keyboard':
            assert outs.pop('BOOT')=='boot'
            outs['BOOT_EXTERNAL']='boot'
        else:
            assert outs.pop('H_2')=='h[2]'
            outs['H2_EXTERNAL']='h[2]'
        return ins,outs
    env=dict(previous.__dict__)
    env.update(ROOT=ROOT,OUT=out,VERIFY=verify,ports=system_ports,package_symbol=package_symbol,
        uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'isa1/net30/'+kind+'/'+s)))
    exec(emitter,env);exec(converter,env)
    return env,defs,parts,name
