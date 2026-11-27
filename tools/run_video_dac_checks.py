"""Four native raster/DAC selected-delay scenarios and two calibrated negatives."""
import hashlib
import json
from pathlib import Path
import tempfile
from limited_process import run_limited

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net33'

def main():
    prior=json.loads((ROOT/'verification/net30/memory-pin-results.json').read_text())
    names=[p for p in prior['runs'][0]['compile']['command'] if p.endswith('.sv')]
    names=[str(ROOT/p) for p in ['sim/hdl/hc_models.sv','sim/net02/package_models.sv','sim/net14c/package_models_async.sv',
        'sim/net19a/package_models.sv','sim/net22/phase_packages.sv','sim/net25/warm_packages.sv',
        'sim/net31/dac_packet_contract.sv','hardware/dac_packet_video/dac_packet_video_async.sv',
        'hardware/vga_dac_rgb332/dac_rgb332_digital.sv','sim/net33/tb_video_dac.sv']]
    cases=[(p,e,0) for p in [0,1] for e in [0,1]]+[(1,1,1),(1,1,2)]
    report={'date':'2026-11-27','scope':'Native raster and DAC pin projection only, synthetic video memory data and qualified external master/reset. Two full frame/reset epochs per positive case. Selected digital delays/binary boundaries, no CPU, analog, PVT/MTBF/POR or production approval.',
        'sources':[{'path':str(Path(p).relative_to(ROOT)),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in names+[str(Path(__file__).resolve()),str(ROOT/'tools/limited_process.py')]],
        'runs':[],'failures':[],'production_released':False}
    with tempfile.TemporaryDirectory(prefix='isa1-video-dac-') as work:
        for policy,early,negative in cases:
            compiled=run_limited(['iverilog','-g2012','-s','tb_video_dac','-Ptb_video_dac.EARLY='+str(early),
                '-Ptb_video_dac.POLICY='+str(policy),'-Ptb_video_dac.NEGATIVE='+str(negative),'-o','bench.vvp']+names,
                work,timeout=30,memory_mb=512,cpu_seconds=20)
            row={'policy':policy,'early':early,'negative':negative,'compile':compiled}
            if compiled['exit']==0:
                result=run_limited(['vvp','bench.vvp'],work,timeout=120,memory_mb=512,cpu_seconds=90,output_mb=2)
                marker={0:'RESULT native_raster_dac=1 reset_epochs=2 samples=210000 visible=153600 hsync=25200 vsync=800 colors=256 cpu=0 analog=0',
                        1:'sync changed before DAC capture',2:'native RGB332 DAC mapping mismatch'}[negative]
                passed=not result['wall_timeout'] and not result['stderr'] and marker in result['stdout']
                passed=passed and ((result['exit']==0) if negative==0 else (result['exit']!=0 and 'FATAL:' in result['stdout']))
                row.update(execution=result,expected_marker=marker,passed=passed)
            else:row['passed']=False
            report['runs'].append(row)
            if not row['passed']:report['failures'].append([policy,early,negative])
            (OUT/'raster-dac-results.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
            print(json.dumps({'policy':policy,'early':early,'negative':negative,'passed':row['passed'],
                              'stdout':row.get('execution',compiled).get('stdout'),
                              'stderr':row.get('execution',compiled).get('stderr')}),flush=True)
            if not row['passed']:return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
