"""NET34 conditional DC contracts, XML faults, and an explicitly ideal RC proxy."""
import copy
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import build_vga_sync as build
import build_dac_leaf as native
from check_dac_leaf import move
from limited_process import run_limited

ROOT=build.ROOT
OUT=ROOT/'verification/net34'

def arithmetic():
    vmin=F('3.3')*F('.99')-F('.010')-F('.050')
    vmax=F('3.3')*F('1.01')+F('.010')+F('.050')
    tripmin=F('3.07')*F('.985');release_max=F('3.07')*F('1.015')*F('1.025')
    assert 3<vmin<=vmax<F('3.6')
    assert vmin>release_max
    results=[]
    for series,load,loaded,high in itertools.product([F(75)*F('.99'),F(75)*F('1.01')],
            [F(2200),F(4700),F(10000),F(10**12)],[False,True],[False,True]):
        source=F('2.4') if high else F('.4')
        # Receiver sinks at most100uA when high; sources at most2mA when low.
        # No arbitrary pullup to5.5V into an actively high3.3V output is qualified.
        sink=(F('.0001') if high else -F('.002')) if loaded else F(0)
        v=(source/series-sink)/(1/series+1/load)
        current=abs((v-source)/series)
        assert current<F('.016')
        assert v>=2 if high else v<=F('.8')
        results.append({'series_ohm':float(series),'receiver_ohm':float(load),'receiver_sink_a':float(sink),
                        'high':high,'receiver_voltage_bound_v':float(v),'output_current_bound_a':float(current)})
    minimum_load=vmin/(10000*F('1.01'))
    floating_input_max=F('.000005')*47000*F('1.01')
    assert minimum_load>F('.0001') and floating_input_max<F('.8')
    rejects={
      'sync_75ohm_receiver_not_supported':F('2.4')*75/(75+75)<2,
      'initial_ldo_accuracy_alone_is_incomplete':vmin<F('3.267'),
      'supervisor_20us_at_5pct_overdrive_does_not_prove_3v_cutoff':tripmin*F('.95')<3}
    assert all(rejects.values())
    return {'scope':'Conditional steady-state arithmetic using identified datasheet conditions and receiver profile; not multivariate PVT/power-transient approval.',
        'ldo_candidate_window_v':[float(vmin),float(vmax)],'ldo_budget':'1 percent initial/DC plus10mV max line and50mV max load; different test conditions, combined envelope remains conditional',
        'supervisor_low_threshold_min_v':float(tripmin),'supervisor_release_max_v':float(release_max),
        'conditional_release_margin_mv':float((vmin-release_max)*1000),'at_5pct_overdrive_below_minimum_threshold_v':float(tripmin*F('.95')),
        'minimum_bleed_load_ma':float(minimum_load*1000),'local_input_leakage_pull_down_max_v':float(floating_input_max),
        'receiver_profile':'TTL thresholds2.0/0.8V; shunt resistance>=2.2k to ground. When HIGH receiver only sinks0..100uA; when LOW receiver may source0..2mA. No high-state backdrive. Not universal monitor compatibility.',
        'dc_corners':results,'rejected_shortcuts':rejects,'core_input_operating_margin_to_5_5v_mv':float((F('5.5')-F('5.48095'))*1000),
        'manual_review_restrictions':['Ioff at VCC0 does not specify the intermediate ramp or active-high backdrive.',
            'TPS731 reverse block requires EN low before input removal; not adopted.',
            'Regulator cannot be presumed to absorb receiver backfeed; high-state injection excluded.'],
        'negative_cutoff_result_is_not_approved_power_sequence':True}

def negatives(defs,parts):
    original=ET.parse(build.VERIFY/(build.NAME+'.xml')).getroot();rows=[]
    cases=[('buffer_channels_swapped','U4','6','V_BUFFER'),('buffer_wrong_rail','U4','8','CORE_VDD'),
           ('supervisor_wrong_sense','U2','5','CORE_VDD'),('gate_ready_bypassed','U3','1','SYNC_3V3'),
           ('oe_grounded','U4','1','GND'),('ldo_enable_tied_to_input','U1','3','CORE_VDD'),
           ('series_shortened','R4','2','H_BUFFER'),('ready_pull_wrong_rail','R3','2','SYNC_3V3')]
    for name,ref,pin,net in cases:
        root=copy.deepcopy(original)
        if name=='ldo_enable_tied_to_input':
            # Its native NC net may still have a node; move handles that too.
            move(root,ref,pin,net)
        else:move(root,ref,pin,net)
        path=OUT/'pin-negatives'/(name+'.xml');path.parent.mkdir(parents=True,exist_ok=True)
        ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
        try:native.validate(path,defs,parts)
        except AssertionError as error:rows.append({'case':name,'rejected':True,'reason':str(error),'file':path.relative_to(ROOT).as_posix()})
        else:rows.append({'case':name,'rejected':False})
    assert all(r['rejected'] for r in rows)
    return rows

def rc_proxy(actual,parts):
    assert actual[('R4','1')]=='H_BUFFER' and actual[('R4','2')]=='H_OUT'
    value=next(p['value'] for p in parts if p['reference']=='R4');series=float(value)
    rows=[]
    for capacitance in [50,250,1000]:
        folder=OUT/'rc-proxy'/str(capacitance);folder.mkdir(parents=True,exist_ok=True)
        circuit=['Ideal3.3V+selected37.5ohm source; native series R; not vendor/cable/ESD model',
            'Vsource src 0 PULSE(0 3.3 20n 1n 1n 3.8u 31.78u)','Rsource src buffer 37.5',
            f'Rnative buffer connector {series}','Rreceiver connector 0 2200',f'Cload connector 0 {capacitance}p',
            '.control','set wr_singlescale','set wr_vecnames','tran 1n 8u','wrdata values.dat v(connector)','quit','.endc','.end']
        (folder/'proxy.cir').write_text('\n'.join(circuit)+'\n')
        result=run_limited(['ngspice','-b','proxy.cir'],folder,timeout=20,memory_mb=256,cpu_seconds=10,output_mb=2)
        build.save(folder/'execution.json',result);assert result['exit']==0 and not result['wall_timeout'],result
        data=[list(map(float,line.split())) for line in (folder/'values.dat').read_text().splitlines()[1:]]
        hi=min(v for t,v in data if 1e-6<t<3e-6);lo=max(v for t,v in data if 6e-6<t<7e-6)
        assert hi>=2 and lo<=.8
        rows.append({'load_pf':capacitance,'samples':len(data),'minimum_1_to_3us_v':hi,'maximum_6_to_7us_v':lo,
                     'scope':'Illustrative RC load; source Ron, supply and edge are selected hypotheses, not guaranteed chip/cable behavior.'})
    return rows

def main():
    defs,parts=build.configuration();_,actual=native.validate(build.VERIFY/(build.NAME+'.xml'),defs,parts)
    math=arithmetic();faults=negatives(defs,parts);rc=rc_proxy(actual,parts)
    names=['tools/check_sync_electrical.py','tools/build_vga_sync.py','tools/build_dac_leaf.py','tools/check_dac_leaf.py',
           'tools/limited_process.py','hardware/vga_sync_3v3/design.json','hardware/vga_sync_3v3/package-functions.json',
           'verification/net34/native/vga_sync_3v3.xml','references/net34/tps709.pdf','references/net34/sn74lvc1g132.pdf',
           'references/net23/sn74lvc2g125.pdf','references/net20/tps3808.pdf']
    report={'date':'2026-11-27','arithmetic':math,'pin_negatives':faults,'rc_proxy':rc,'failures':[],
        'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names],
        'ramp_transient_esd_qualified':False,'production_released':False}
    build.save(OUT/'electrical-results.json',report)
    print(json.dumps({'dc_corners':len(math['dc_corners']),'pin_negatives':len(faults),'rc_proxy_cases':len(rc),
                      'conditional_ldo_window_v':math['ldo_candidate_window_v'],'release_margin_mv':math['conditional_release_margin_mv'],
                      'power_sequence_qualified':False,'failures':[]}))

if __name__=='__main__':main()
