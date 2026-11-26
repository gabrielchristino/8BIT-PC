"""Probe the new native common request clock with all existing monitors."""
import hashlib
import itertools
import json
from pathlib import Path
import tempfile
from run_rtl import run
from run_request_skew_probe import once

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net24'


def main():
    source=ROOT/'hardware/common_request/common_request_netlist.sv'
    text=once(source.read_text(),'TIMED=0,EARLY=0)',
              'TIMED=0,EARLY=0,parameter realtime STATE_CLOCK=8.5,PAYLOAD_CLOCK=8.5,REQUEST_CLOCK=8.5,FIRST_CQ=44)')
    for net,param in [('BUF_3_3','STATE_CLOCK'),('BUF_3_4','PAYLOAD_CLOCK'),('BUF_4_1','REQUEST_CLOCK')]:
        text=once(text,f'assign #GATE_T n_{net}=',f'assign #(TIMED?{param}:0) n_{net}=')
    text=once(text,'hc74_model #(.TIMED(TIMED)) U4_0',
              'net24_hc74_probe #(.TIMED(TIMED),.CQ_NS(FIRST_CQ)) U4_0')
    projection=ROOT/'sim/net24/common_request_probe.sv'
    projection.write_text('// GENERATED from native common request graph; monitors unchanged.\n'+text)
    ancestor=ROOT/'sim/net24/tb_request_skew.sv'
    bench=ancestor.read_text().replace('FIRST_CLOCK=8.5,SECOND_CLOCK=8.5,FIRST_CQ=44',
        'STATE_CLOCK=8.5,PAYLOAD_CLOCK=8.5,REQUEST_CLOCK=8.5,FIRST_CQ=44')
    bench=bench.replace('system_access_netlist','common_request_netlist')
    bench=once(bench,'.FIRST_CLOCK(FIRST_CLOCK),.SECOND_CLOCK(SECOND_CLOCK)',
               '.STATE_CLOCK(STATE_CLOCK),.PAYLOAD_CLOCK(PAYLOAD_CLOCK),.REQUEST_CLOCK(REQUEST_CLOCK)')
    bench=once(bench,'FIRST_CLOCK,SECOND_CLOCK,FIRST_CQ','STATE_CLOCK,REQUEST_CLOCK,FIRST_CQ')
    bench=once(bench,'first_clock_ns=%0.3f second_clock_ns=%0.3f',
               'state_clock_ns=%0.3f request_clock_ns=%0.3f')
    bench_path=ROOT/'sim/net24/tb_common_request.sv';bench_path.write_text(bench)
    names=['sim/hdl/hc_models.sv','sim/net02/package_models.sv','sim/net03/package_models.sv','sim/net04/package_models.sv',
           'sim/net19a/package_models.sv','sim/net24/request_probe_model.sv','sim/net24/common_request_probe.sv','sim/net24/tb_common_request.sv']
    report={'date':'2026-11-26','scope':'Native common-clock request candidate under independent state/payload/request buffer delays1/8.5ns and illustrative firstHC74 CQ0/1/6/44ns. CQ minimum unspecified by HC74; selected models are not silicon characterization or extracted PCB skew/MTBF/full STA.',
            'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+[
                'tools/run_common_request_probe.py','tools/run_request_skew_probe.py','sim/net24/tb_request_skew.sv',
                'hardware/common_request/common_request_netlist.sv','verification/net24/native/common_request.xml']],
            'runs':[],'negative':[],'failures':[],'production_released':False}
    with tempfile.TemporaryDirectory(prefix='isa1-common-request-') as tmp:
        work=Path(tmp)
        for index,(delays,cq) in enumerate(itertools.product(itertools.product((1,8.5),repeat=3),(0,1,6,44))):
            parameters=dict(zip(['STATE_CLOCK','PAYLOAD_CLOCK','REQUEST_CLOCK'],delays));parameters['FIRST_CQ']=cq
            command=['iverilog','-g2012','-Wall','-s','tb_request_skew',
                     *[f'-Ptb_request_skew.{key}={value}' for key,value in parameters.items()],
                     '-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names]]
            row={'index':index,'parameters':parameters,'compile':run(command,work)}
            if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=30)
            result=row.get('execution',{})
            row['passed']=row['compile']['exit']==0 and not row['compile']['stderr'] and result.get('exit')==0 and 'acknowledged_read=1 failures=0' in result.get('stdout','')
            report['runs'].append(row)
            if not row['passed']:report['failures'].append(index)
            (OUT/'common-request-probe.json').write_text(json.dumps(report,indent=2)+'\n')
            if not row['passed']:
                print(json.dumps(row),flush=True);return 1
        bad=once(projection.read_text(),' U4_0(n_BUF_4_1,',' U4_0(n_BUF_3_3,')
        fault=work/'first_clock_reverted.sv';fault.write_text(bad)
        inputs=[str(fault) if n=='sim/net24/common_request_probe.sv' else str(ROOT/n) for n in names]
        command=['iverilog','-g2012','-Wall','-s','tb_request_skew',
                 '-Ptb_request_skew.STATE_CLOCK=1','-Ptb_request_skew.PAYLOAD_CLOCK=8.5',
                 '-Ptb_request_skew.REQUEST_CLOCK=8.5','-Ptb_request_skew.FIRST_CQ=6',
                 '-o',str(work/'test.vvp'),*inputs]
        row={'mutation':'Restore first request clock to state branch, leave second on common/MDR branch',
             'mutated_projection_sha256':hashlib.sha256(fault.read_bytes()).hexdigest(),'compile':run(command,work)}
        if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=30)
        result=row.get('execution',{})
        row['expected_rejection']='DFF data setup violation'
        row['passed']=row['compile']['exit']==0 and not row['compile']['stderr'] and result.get('exit') not in (None,0) and row['expected_rejection'] in result.get('stdout','')
        report['negative'].append(row)
        if not row['passed']:report['failures'].append('reverted clock negative')
        (OUT/'common-request-probe.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({'completed':len(report['runs']),'negative_detected':row['passed'],'failures':report['failures']}))
    return int(bool(report['failures']))


if __name__=='__main__':raise SystemExit(main())
