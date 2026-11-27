"""NET34 isolated qualified states and two native raster+driver frame tests."""
import hashlib
import json
from pathlib import Path
import tempfile
from limited_process import run_limited

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net34'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    fixture=(ROOT/'sim/net33/tb_video_dac.sv').read_text()
    fixture=fixture.replace('module tb_video_dac;','module tb_sync_raster;\n parameter SLOW=1;')
    fixture=fixture.replace('wire observed_hs=NEGATIVE==1?hs:dhs;',
        "wire external_h,external_v,oe_unused;\n net34_sync #(.SLOW(SLOW)) output_stage(2'd1,1'b1,ready,dhs,dvs,external_h,external_v,oe_unused);\n wire observed_hs=NEGATIVE==1?hs:external_h;")
    fixture=fixture.replace('wire observed_vs=NEGATIVE==1?vs:dvs;','wire observed_vs=NEGATIVE==1?vs:external_v;')
    fixture=fixture.replace('RESULT native_raster_dac=1','RESULT native_raster_dac_sync_driver=1')
    (OUT/'tb_sync_raster.sv').write_text(fixture)
    core=['sim/hdl/hc_models.sv','sim/net02/package_models.sv','sim/net14c/package_models_async.sv',
          'sim/net19a/package_models.sv','sim/net22/phase_packages.sv','sim/net25/warm_packages.sv',
          'sim/net31/dac_packet_contract.sv','hardware/dac_packet_video/dac_packet_video_async.sv',
          'hardware/vga_dac_rgb332/dac_rgb332_digital.sv']
    stage='hardware/vga_sync_3v3/vga_sync_functional.sv'
    report={'date':'2026-11-27','scope':'Native sync pins/function with qualified rail0/valid states and unspecified ramp; supervisor release and regulator rail are forcepoints. Frame tests use NET33 native raster/DAC projection and synthetic data. No regulator/supervisor analog simulation or ESD/PCB approval.',
        'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in core+[
            stage,'sim/net33/tb_video_dac.sv','sim/net34/tb_sync_states.sv','verification/net34/tb_sync_raster.sv',
            'tools/run_sync_checks.py','tools/limited_process.py']],
        'runs':[],'failures':[],'production_released':False}
    cases=[('states',0,0),('states',1,0),('states',1,1),('frames',0,0),('frames',1,0)]
    with tempfile.TemporaryDirectory(prefix='isa1-sync-stage-') as work:
        for kind,slow,negative in cases:
            top='tb_sync_states' if kind=='states' else 'tb_sync_raster'
            names=[stage,'sim/net34/tb_sync_states.sv'] if kind=='states' else core+[stage,'verification/net34/tb_sync_raster.sv']
            command=['iverilog','-g2012','-s',top,'-P'+top+'.SLOW='+str(slow),'-P'+top+'.NEGATIVE='+str(negative),'-o','bench.vvp']+[str(ROOT/n) for n in names]
            compiled=run_limited(command,work,timeout=30,memory_mb=512,cpu_seconds=20)
            row={'kind':kind,'slow':slow,'negative':negative,'compile':compiled,'passed':False}
            if compiled['exit']==0:
                result=run_limited(['vvp','bench.vvp'],work,timeout=120,memory_mb=512,cpu_seconds=90,output_mb=2)
                marker='sync drive while inhibited' if negative else 'RESULT sync_state_checks=' if kind=='states' else 'RESULT native_raster_dac_sync_driver=1 reset_epochs=2 samples=210000 visible=153600 hsync=25200 vsync=800 colors=256 cpu=0 analog=0'
                passed=not result['wall_timeout'] and not result['stderr'] and marker in result['stdout']
                passed=passed and ((result['exit']!=0 and 'FATAL:' in result['stdout']) if negative else result['exit']==0 and 'failures=0' in result['stdout'])
                row.update(execution=result,expected_marker=marker,passed=passed)
            report['runs'].append(row)
            if not row['passed']:report['failures'].append([kind,slow,negative])
            (OUT/'sync-results.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
            print(json.dumps({'kind':kind,'slow':slow,'negative':negative,'passed':row['passed'],
                'output':row.get('execution',compiled).get('stdout'),'stderr':row.get('execution',compiled).get('stderr')}),flush=True)
            if not row['passed']:return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
