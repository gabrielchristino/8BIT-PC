"""Bounded functional proposal checks, independent of frozen NET30 sources."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from limited_process import run_limited

ROOT=Path(__file__).resolve().parents[1]

def main():
    names=['sim/net31/dac_packet_contract.sv','sim/net31/tb_dac_packet.sv',
           'tools/run_dac_packet_contract.py','tools/limited_process.py']
    expected={0:'RESULT functional_proposal_only=1 rgb_codes=256 samples=105000 visible=76800 hsync=12600 vsync=400 failures=0',
              1:'DAC setup violation',2:'DAC hold violation',3:'DAC high pulse violation',4:'packet sync mismatch'}
    rows=[]
    with tempfile.TemporaryDirectory(prefix='isa1-dac-contract-') as temp:
        for negative,marker in expected.items():
            compiled=run_limited(['iverilog','-g2012','-s','tb_dac_packet',
                '-Ptb_dac_packet.NEGATIVE='+str(negative),'-o','bench.vvp']+
                [str(ROOT/name) for name in names[:2]],temp,timeout=20,memory_mb=256,cpu_seconds=10)
            assert compiled['exit']==0 and not compiled['stderr'],compiled
            execution=run_limited(['vvp','bench.vvp'],temp,timeout=30,memory_mb=256,cpu_seconds=20)
            passed=not execution['wall_timeout'] and not execution['stderr'] and marker in execution['stdout']
            passed=passed and ((execution['exit']==0) if not negative else (execution['exit']!=0 and 'FATAL:' in execution['stdout']))
            rows.append({'negative':negative,'expected_marker':marker,'compile':compiled,'execution':execution,'passed':passed})
    report={'date':'2026-11-27','scope':'Functional proposal with selected 1ns output delay and input timing guards. Synthetic packet/raster stimuli, not NET30 native integration, CPU execution or analog simulation.',
        'command':['python3','tools/run_dac_packet_contract.py'],
        'iverilog_version':subprocess.run(['iverilog','-V'],capture_output=True,text=True).stdout,
        'sources':[{'path':name,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()} for name in names],
        'runs':rows,'failures':[row['negative'] for row in rows if not row['passed']],
        'production_released':False}
    out=ROOT/'verification/net31';out.mkdir(parents=True,exist_ok=True)
    (out/'packet-results.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    print(json.dumps({'scenarios':len(rows),'expected_negative_rejections':4,'failures':report['failures']}))
    assert not report['failures']

if __name__=='__main__':main()
