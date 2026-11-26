"""Probe existing native request synchronizer under selected branch/CQ delays."""
import hashlib
import itertools
import json
from pathlib import Path
import re
import tempfile
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net24'


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def main():
    source=ROOT/'hardware/system_access/system_access_netlist.sv'
    text=once(source.read_text(),'TIMED=0,EARLY=0)','TIMED=0,EARLY=0,parameter realtime FIRST_CLOCK=8.5,SECOND_CLOCK=8.5,FIRST_CQ=44)')
    for net,param in [('BUF_3_3','FIRST_CLOCK'),('BUF_3_4','SECOND_CLOCK')]:
        text=once(text,f'assign #GATE_T n_{net}=',f'assign #(TIMED?{param}:0) n_{net}=')
    text=once(text,'hc74_model #(.TIMED(TIMED)) U4_0',
              'net24_hc74_probe #(.TIMED(TIMED),.CQ_NS(FIRST_CQ)) U4_0')
    projection=ROOT/'sim/net24/system_access_skew_probe.sv'
    projection.write_text('// GENERATED selected delay probe; all downstream monitors preserved.\n'+text)
    ancestor=ROOT/'sim/net03/package_models.sv'
    model=re.search(r'module hc74_model .*?endmodule',ancestor.read_text(),re.S).group(0)
    model=once(model,'module hc74_model #(parameter integer TIMED=0)',
               'module net24_hc74_probe #(parameter integer TIMED=0,parameter realtime CQ_NS=44)')
    model=once(model,'TIMED?44:0','TIMED?CQ_NS:0')
    model_path=ROOT/'sim/net24/request_probe_model.sv'
    model_path.write_text('`timescale 1ns/1ps\n// CQ6ns is an admitted illustrative value below the44ns maximum; datasheet gives no minimum. Not measured silicon.\n'+model+'\n')
    names=['sim/hdl/hc_models.sv','sim/net02/package_models.sv','sim/net03/package_models.sv','sim/net04/package_models.sv',
           'sim/net19a/package_models.sv','sim/net24/request_probe_model.sv','sim/net24/system_access_skew_probe.sv','sim/net24/tb_request_skew.sv']
    report={'date':'2026-11-26','base_git_commit':'c54226afed52e04c787b91c65dc29cfacf8f661e',
            'scope':'Existing native controller clock-group/CQ probe, not native circuit change. AHC1251..8.5ns; HC74 has44ns maximum at4.5V/-40..85C/CL50pF and no minimum, so CQ6 is an illustrative admitted model, not guaranteed silicon behavior. First REQ input is deliberately stable; original second-stage setup monitor remains enabled.',
            'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+[
                'tools/run_request_skew_probe.py','hardware/system_access/design.json',
                'hardware/system_access/system_access_netlist.sv','references/ti/sn74hc74.pdf','references/ti/sn74ahc125.pdf']],
            'runs':[],'investigations':[],'failures':[],'production_released':False}
    with tempfile.TemporaryDirectory(prefix='isa1-request-skew-') as tmp:
        work=Path(tmp)
        for cq,(first,second) in itertools.product((44,6),[(8.5,8.5),(1,8.5),(8.5,1)]):
            expected=cq==6 and first==1 and second==8.5
            command=['iverilog','-g2012','-Wall','-s','tb_request_skew',
                     f'-Ptb_request_skew.FIRST_CLOCK={first}',f'-Ptb_request_skew.SECOND_CLOCK={second}',f'-Ptb_request_skew.FIRST_CQ={cq}',
                     '-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names]]
            row={'first_clock_ns':first,'second_clock_ns':second,'first_cq_ns':cq,'compile':run(command,work)}
            if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=30)
            result=row.get('execution',{})
            row['expected_rejection']='DFF data setup violation' if expected else None
            row['passed']=row['compile']['exit']==0 and not row['compile']['stderr'] and (
                result.get('exit') not in (None,0) and 'DFF data setup violation' in result.get('stdout','') if expected else
                result.get('exit')==0 and 'acknowledged_read=1 failures=0' in result.get('stdout',''))
            report['investigations' if expected else 'runs'].append(row)
            if not row['passed']:report['failures'].append([cq,first,second])
            (OUT/'request-skew-probe.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(row),flush=True)
            if not row['passed']:return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
