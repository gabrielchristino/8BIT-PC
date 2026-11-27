"""NET35 exact window arithmetic and bounded discharge proxy, not vendor power model."""
import copy
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
import build_sync_window as build
import build_dac_leaf as native
from check_dac_leaf import move
from limited_process import run_limited

ROOT=build.ROOT
OUT=ROOT/'verification/net35'

def calculations():
    # Actual datasheet full-temperature ISET98..102uA and output offset +/-2mV.
    # Do not use initial +/-1percent as a full-temperature tolerance.
    rails=[i*r+offset+path for i,r,offset,path in itertools.product([F('.000098'),F('.000102')],
        [F(35100)*F('.999'),F(35100)*F('1.001')],[-F('.002'),F('.002')],[-F('.010'),F('.010')])]
    trips=[]
    for ref,top,bottom,leak in itertools.product([F('.405')*F('.98'),F('.405')*F('1.02')],
        [F(14000)*F('.999'),F(14000)*F('1.001')], [F(2000)*F('.999'),F(2000)*F('1.001')],
        [-F('.000000025'),F('.000000025')]):
        trips.append(ref*(1+top/bottom)+leak*top)
    assert min(rails)>=3 and max(rails)<=F('3.6')
    release_margin=min(rails)-max(trips)*F('1.03');assert release_margin>0
    results=[]
    for trip,cap,load,esr in itertools.product(trips,[F('.000047'),F('.000100')],[F('.005'),F('.010')],[F(0),F('.05')]):
        low=trip*F('.95')-load*F('.0000201')/cap-load*esr
        assert low>3
        results.append({'trip_v':float(trip),'cap_f':float(cap),'load_a':float(load),'esr_ohm':float(esr),'voltage_at_disable_bound_v':float(low)})
    old_min=F('3.207')
    # Necessary threshold interval: ignore all extra post-detection droop, already impossible.
    required_nom=F(3)/(F('.985')*F('.95'))
    allowed_nom=old_min/(F('1.015')*F('1.025'))
    assert required_nom>allowed_nom
    minimum_load=min(rails)/(2200*F('1.01'));assert minimum_load>F('.001')
    return {'scope':'Conditional feasibility with explicit current,capacitance,ESR,voltage-error and detection-delay assumptions. Not validated regulator dynamics or ramp/POR.',
        'rail_min_max_v':[float(min(rails)),float(max(rails))],'rset_ohm':35100,'rset_tolerance':.001,
        'set_current_guaranteed_full_temperature_a':[.000098,.000102],'output_offset_v':.002,'extra_path_and_ripple_budget_v':.010,
        'trip_min_max_v':[float(min(trips)),float(max(trips))],'release_max_v':float(max(trips)*F('1.03')),
        'release_margin_mv':float(release_margin*1000),'upper_3_6v_margin_mv':float((F('3.6')-max(rails))*1000),
        'minimum_bleed_current_ma':float(minimum_load*1000),'hypothesized_delay_us':20.1,'hypothesized_load_limit_ma':10,
        'hypothesized_effective_cap_min_uf':47,'hypothesized_esr_max_ohm':.05,
        'worst_voltage_at_disable_v':min(r['voltage_at_disable_bound_v'] for r in results),'conditional_discharge_corners':results,
        'old_window_required_nominal_trip_min_v':float(required_nom),'old_window_allowed_nominal_trip_max_v':float(allowed_nom),
        'changing_only_old_threshold_cannot_close_window':True,
        'limits':['VDD-dependent supervisor delay and output transition/load require qualification at3.51V.',
          '20.1us,10mA,47uF effective,ESR50milliohm and bounded monotonic fall are design requirements/hypotheses, not measured guarantees.',
          'No short circuit or abrupt external clamp is inside the discharge envelope.',
          'Capacitor ESL, Kelvin connections, stability, startup and regulator nonlinear behavior remain unqualified.']}

def functional():
    prior=(ROOT/'hardware/vga_sync_3v3/vga_sync_functional.sv').read_text()
    current=(ROOT/'hardware/vga_sync_window/sync_window_functional.sv').read_text()
    assert prior==current.replace('module net35_sync','module net34_sync')
    bench=(ROOT/'sim/net34/tb_sync_states.sv').read_text().replace('module tb_sync_states','module tb_window_states').replace('net34_sync','net35_sync')
    (OUT/'tb_window_states.sv').write_text(bench)
    rows=[]
    with tempfile.TemporaryDirectory(prefix='isa1-sync-window-') as work:
        for slow,negative in [(0,0),(1,0),(1,1)]:
            command=['iverilog','-g2012','-s','tb_window_states','-Ptb_window_states.SLOW='+str(slow),
                     '-Ptb_window_states.NEGATIVE='+str(negative),'-o','bench.vvp',
                     str(ROOT/'hardware/vga_sync_window/sync_window_functional.sv'),str(OUT/'tb_window_states.sv')]
            comp=run_limited(command,work,timeout=20,memory_mb=256,cpu_seconds=10);assert comp['exit']==0 and not comp['stderr']
            run=run_limited(['vvp','bench.vvp'],work,timeout=20,memory_mb=256,cpu_seconds=10)
            marker='sync drive while inhibited' if negative else 'RESULT sync_state_checks=14'
            assert marker in run['stdout'] and not run['stderr'] and not run['wall_timeout']
            assert (run['exit']!=0)==bool(negative)
            rows.append({'slow':slow,'negative':negative,'compile':comp,'execution':run,'expected_marker':marker,'passed':True})
    return rows

def pin_faults(defs,parts):
    original=ET.parse(build.VERIFY/(build.NAME+'.xml')).getroot();rows=[]
    for case,ref,pin,net in [('pad_not_grounded','U1','11','CORE_VDD'),('out_sense_wrong','U1','9','CORE_VDD'),
         ('set_wrong_rail','R11','2','SYNC_RAIL'),('unused_pgfb_grounded','U1','6','GND'),
         ('supervisor_divider_bypassed','U2','5','SYNC_RAIL'),('divider_lower_wrong','R10','2','CORE_VDD'),
         ('bleed_wrong_rail','R6','2','SYNC_RAIL'),('buffer_oe_grounded','U4','1','GND')]:
        root=copy.deepcopy(original);move(root,ref,pin,net)
        p=OUT/'pin-negatives'/(case+'.xml');p.parent.mkdir(parents=True,exist_ok=True)
        ET.ElementTree(root).write(p,encoding='utf-8',xml_declaration=True)
        try:native.validate(p,defs,parts)
        except AssertionError as error:rows.append({'case':case,'rejected':True,'reason':str(error),'file':p.relative_to(ROOT).as_posix()})
        else:rows.append({'case':case,'rejected':False})
    assert all(r['rejected'] for r in rows)
    return rows

def spice(math):
    start=math['trip_min_max_v'][0]*.95;rows=[]
    cases=[(47,5,.001,False),(47,10,.05,False),(100,5,.05,False),(100,10,.05,False),
           (4.7,10,.05,True),(47,50,.05,True)]
    for index,(cap,ma,esr,negative) in enumerate(cases):
        folder=OUT/'discharge-proxy'/str(index);folder.mkdir(parents=True,exist_ok=True)
        lines=['Selected passive discharge envelope, NOT LT3042/TPS3808 model',
            f'Cbulk store 0 {cap}u IC={start:.17g}',f'RESR store rail {esr}',f'Iload rail 0 {ma/1000}',
            '.control','set wr_singlescale','set wr_vecnames','tran 10n 22u uic',
            'wrdata values.dat v(rail)','quit','.endc','.end']
        (folder/'discharge.cir').write_text('\n'.join(lines)+'\n')
        run=run_limited(['ngspice','-b','discharge.cir'],folder,timeout=20,memory_mb=256,cpu_seconds=10,output_mb=2)
        build.save(folder/'execution.json',run);assert run['exit']==0 and not run['wall_timeout']
        data=[list(map(float,line.split())) for line in (folder/'values.dat').read_text().splitlines()[1:]]
        t,v=min(data,key=lambda row:abs(row[0]-20.1e-6))
        expected=start-ma/1000*(t/(cap*1e-6)+esr)
        assert abs(v-expected)<1e-5,(index,v,expected)
        assert (v<3)==negative
        rows.append({'case':index,'effective_uf':cap,'load_ma':ma,'esr_ohm':esr,'negative':negative,
                     'sample_time_s':t,'voltage_v':v,'classified_as_expected':True,
                     'scope':'Current-source discharge from chosen5pct-overdrive point; ideal timer20.1us. Does not simulate actual supervisor or regulator.'})
    return rows

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    defs,parts=build.configuration();native.validate(build.VERIFY/(build.NAME+'.xml'),defs,parts)
    nominal={p['reference']:p['value'] for p in parts}
    for ref,value in {'R9':'14k','R10':'2k','R11':'35.1k','R6':'2.2k','C2':'100uF','C6':'10uF'}.items():
        assert nominal[ref]==value,('Numeric contract no longer matches native values',ref)
    math=calculations();states=functional();pins=pin_faults(defs,parts);discharge=spice(math)
    names=['tools/check_sync_window.py','tools/build_sync_window.py','tools/limited_process.py','tools/check_dac_leaf.py',
        'hardware/vga_sync_window/design.json','hardware/vga_sync_window/package-functions.json','hardware/vga_sync_window/sync_window_functional.sv',
        'hardware/vga_sync_3v3/vga_sync_functional.sv','sim/net34/tb_sync_states.sv','verification/net35/tb_window_states.sv',
        'verification/net35/native/vga_sync_window.xml','references/net20/tps3808.pdf']
    report={'date':'2026-11-27','base_git_commit':build.BASE,'arithmetic':math,'qualified_state_runs':states,
        'pin_negatives':pins,'discharge_proxy':discharge,'functional_model_equivalent_to_net34':True,
        'new_full_frames_executed':False,'physical_power_qualified':False,'production_released':False,'failures':[],
        'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names]}
    build.save(OUT/'window-results.json',report)
    print(json.dumps({'conditional_discharge_corners':len(math['conditional_discharge_corners']),
        'release_margin_mv':math['release_margin_mv'],'minimum_disable_bound_v':math['worst_voltage_at_disable_v'],
        'state_scenarios':len(states),'pin_negatives':len(pins),'spice_cases':len(discharge),'power_qualified':False,'failures':[]}))

if __name__=='__main__':main()
