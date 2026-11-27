"""NET32 pin negatives, full-code latch check and conditional current-load study."""
import copy
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import build_dac_leaf as native
from limited_process import run_limited

ROOT=native.ROOT
OUT=ROOT/'verification/net32'

def save(path,value):native.save(path,value)

def move(root,ref,pin,target):
    nets=root.find('nets');found=None
    for net in nets:
        for node in list(net):
            if node.get('ref')==ref and node.get('pin')==pin:
                assert found is None;found=node;net.remove(node)
    assert found is not None
    target_net=next(n for n in nets if n.get('name').removeprefix('/')==target)
    target_net.append(found)

def graph_negatives(defs,parts):
    source=native.VERIFY/(native.NAME+'.xml');original=ET.parse(source).getroot();rows=[]
    folder=OUT/'pin-negatives';folder.mkdir(parents=True,exist_ok=True)
    for name in ['data_swapped','unused_output_floats','comp1_wrong_rail','local_shunt_missing','sleep_high','nc_connected']:
        root=copy.deepcopy(original)
        if name=='data_swapped':move(root,'U1','1','R_DB_0');move(root,'U1','10','R_DB_9')
        if name=='unused_output_floats':move(root,'U1','21','R_ANALOG')
        if name=='comp1_wrong_rail':move(root,'C4','2','GND')
        if name=='local_shunt_missing':
            components=root.find('components');components.remove(next(c for c in components if c.get('ref')=='R2'))
        if name=='sleep_high':move(root,'U1','15','DAC_VDD')
        if name=='nc_connected':
            net=next(n for n in root.find('nets') if n.get('name').removeprefix('/')=='GND')
            ET.SubElement(net,'node',{'ref':'U1','pin':'11'})
        path=folder/(name+'.xml');ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
        try:native.validate(path,defs,parts)
        except AssertionError as error:rows.append({'case':name,'rejected':True,'reason':str(error),'path':path.relative_to(ROOT).as_posix()})
        else:rows.append({'case':name,'rejected':False})
    assert all(row['rejected'] for row in rows),rows
    return rows

def dc_arithmetic():
    # Manufacturer current range is NOT a protective current limiter.
    # These are explicit bounded-source hypotheses, not absolute safety proof.
    w=F('0.7');monitor=F(75);compliance=F('1.25');factor=F(1023,1024)
    max_shunt=compliance*monitor/w-monitor
    min_shunt=w/(F('0.020')*factor-w/monitor)
    required_current_at_largest_shunt=w/monitor+w/max_shunt
    assert min_shunt>max_shunt
    gains=[F('.9'),F('1.1')];rsets=[F(2320)*F('.999'),F(2320)*F('1.001')]
    locals_=[F(75)*F('.99'),F(75)*F('1.01')];monitors=[F(75)*F('.95'),F(75)*F('1.05')]
    white_values=[];currents=[];open_values=[];count=0
    for gain,rset,local,remote in itertools.product(gains,rsets,locals_,monitors):
        current=32*F('1.2')*gain/rset;currents.append(current)
        assert F('.002')<=current<=F('.020')
        white=current*factor*local*remote/(local+remote);white_values.append(white)
        open_values.append(current*factor*local)
        for pixel in range(256):
            values=[(pixel>>5)&7,(pixel>>2)&7,pixel&3]
            for value,maximum in zip(values,[7,7,3]):
                code=(2*value*1023+maximum)//(2*maximum)
                v=current*F(code,1024)*local*remote/(local+remote)
                assert 0<=v<=compliance
                count+=1
    nominal=32*F('1.2')/2320*factor*F('37.5')
    # DC KCL envelope under an independent <=20mA hypothesis, regardless of linearity.
    independent_open_bound=F('.020')*max(locals_)
    assumed_abs_ceiling=F('5.22076')+F('.3')
    assert independent_open_bound<assumed_abs_ceiling
    assert abs(nominal/w-1)>F('.05') # deliberately uncalibrated diagnostic leaf
    return {'conditional_voltage_evaluations':count,'diagnostic_white_nominal_v':float(nominal),
        'diagnostic_loaded_white_range_v':[float(min(white_values)),float(max(white_values))],
        'diagnostic_fullscale_current_max_ma':float(max(currents)*1000),
        'diagnostic_open_linear_extrapolation_max_v':float(max(open_values)),
        'passive_shunt_max_ohm_for_open_compliance':float(max_shunt),
        'passive_shunt_min_ohm_for_20ma_and_loaded_white':float(min_shunt),
        'minimum_required_white_current_ma_with_open_compliance':float(required_current_at_largest_shunt*1000),
        'no_passive_single_shunt_solution':True,'independent_20ma_hypothesis_open_kcl_bound_v':float(independent_open_bound),
        'assumed_vdd_min_plus_0_3v':float(assumed_abs_ceiling),'diagnostic_white_is_not_final_target':True,
        'dc_kcl_is_not_esd_hotplug_power_sequence_or_safety_approval':True}

def spice_output_loads(actual,parts):
    part_by_ref={p['reference']:p for p in parts};rows=[]
    folder=OUT/'spice-load-proxy';folder.mkdir(parents=True,exist_ok=True)
    for name,remote in [('loaded',75.0),('open_1teraohm',1e12),('short_1milliohm',.001)]:
        work=folder/name;work.mkdir(parents=True,exist_ok=True)
        lines=['NET32 ideal current-source KCL proxy only, not AD9760 model','Vcode code 0 0']
        reference=[]
        for index,color in enumerate('RGB'):
            ref='R'+str(index*2+2);p=part_by_ref[ref]
            assert actual[(ref,'1')]==color+'_ANALOG' and actual[(ref,'2')]=='GND'
            local=float(p['value']);ifs=38.4/2320
            lines += [f'B{color} 0 {color}_ANALOG I={ifs:.17g}*v(code)/1024',
                      f'{ref} {color}_ANALOG 0 {local:.17g}',f'RM{color} {color}_ANALOG 0 {remote:.17g}']
            reference.append(ifs/1024*local*remote/(local+remote))
        lines+=['.control','set wr_singlescale','set wr_vecnames','dc Vcode 0 1023 1',
                'wrdata values.dat v(R_ANALOG) v(G_ANALOG) v(B_ANALOG)','quit','.endc','.end']
        (work/'load.cir').write_text('\n'.join(lines)+'\n')
        result=run_limited(['ngspice','-b','load.cir'],work,timeout=20,memory_mb=256,cpu_seconds=10,output_mb=2)
        save(work/'execution.json',result)
        assert result['exit']==0 and not result['wall_timeout'],result
        data=(work/'values.dat').read_text().splitlines();assert len(data)==1025
        max_error=0
        for code,line in enumerate(data[1:]):
            vector=list(map(float,line.split()));assert len(vector)==4 and abs(vector[0]-code)<1e-8
            for channel,slope in enumerate(reference):
                error=abs(vector[channel+1]-slope*code);max_error=max(max_error,error)
                assert error<1e-7,(name,code,channel,error)
        rows.append({'case':name,'samples':1024,'channels':3,'maximum_kcl_comparison_error_v':max_error,
                     'source':(work/'load.cir').relative_to(ROOT).as_posix(),'execution':(work/'execution.json').relative_to(ROOT).as_posix(),
                     'note':'Open-case predictions above compliance are out of model validity for DAC transfer; no real voltage/safety claim.'})
    return rows

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    defs,parts=native.configuration()
    _,actual=native.validate(native.VERIFY/(native.NAME+'.xml'),defs,parts)
    negatives=graph_negatives(defs,parts)
    names=['hardware/vga_dac_experiment/vga_dac_experiment_digital.sv','sim/net31/dac_packet_contract.sv','sim/net32/tb_dac_leaf.sv']
    with tempfile.TemporaryDirectory(prefix='isa1-dac-leaf-') as work:
        compiled=run_limited(['iverilog','-g2012','-s','tb_dac_leaf','-o','bench.vvp']+[str(ROOT/name) for name in names],work,timeout=20,memory_mb=256,cpu_seconds=10)
        assert compiled['exit']==0 and not compiled['stderr'],compiled
        result=run_limited(['vvp','bench.vvp'],work,timeout=20,memory_mb=256,cpu_seconds=10)
        assert result['exit']==0 and 'RESULT native_dac_only=1 samples=1024 distinct_codes_each_channel=1024 analog_model=0 failures=0' in result['stdout'] and not result['stderr'],result
    arithmetic=dc_arithmetic();spice=spice_output_loads(actual,parts)
    names+=['tools/build_dac_leaf.py','tools/check_dac_leaf.py','tools/limited_process.py',
            'hardware/vga_dac_experiment/design.json','hardware/vga_dac_experiment/package-functions.json',
            'verification/net32/native/vga_dac_experiment.xml','engineering/net31/dac_contract.json']
    report={'date':'2026-11-27','base_git_commit':native.BASE,'scope':'Standalone native pin projection; conditional DC arithmetic and ideal current-source load proxy. Not complete DAC electrical model, NET30 integration or physical qualification.',
        'pin_negatives':negatives,'digital':{'compile':compiled,'execution':result},'dc_arithmetic':arithmetic,'spice_kcl_proxy':spice,
        'versions':{name:subprocess.run(cmd,capture_output=True,text=True).stdout for name,cmd in [('iverilog',['iverilog','-V']),('ngspice',['ngspice','--version']),('kicad',[native.KICAD,'version'])]},
        'sources':[{'path':name,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()} for name in names],
        'failures':[],'production_released':False}
    save(OUT/'leaf-results.json',report)
    print(json.dumps({'pin_negatives':len(negatives),'digital_codes_each_channel':1024,'spice_cases':len(spice),'dc':arithmetic,'failures':[]}))

if __name__=='__main__':main()
