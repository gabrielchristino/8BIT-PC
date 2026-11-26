"""Audit the exact two-pin delta, clock loads, and actual backend Boolean source."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def functions(parts,defs):
    return {p['reference']:{defs[p['part']]['pins'][pin]['name']:net for pin,net in p['nets'].items()} for p in parts}


def main():
    names=['hardware/system_access/design.json','hardware/common_request/design.json','hardware/common_request/package-functions.json',
           'hardware/video_common_clock/design.json','hardware/video_common_clock/package-functions.json',
           'hardware/clocked_reset/design.json','hardware/clocked_reset/package-functions.json']
    old,new,defs,video,video_defs,reset,reset_defs=[json.loads((ROOT/n).read_text()) for n in names]
    before={p['reference']:p for p in old['parts']};after={p['reference']:p for p in new['parts']}
    errors=[];delta=[]
    if before.keys()!=after.keys():errors.append('Inventory changed')
    for ref,p in before.items():
        other=after[ref]
        if {k:v for k,v in p.items() if k!='nets'}!={k:v for k,v in other.items() if k!='nets'}:errors.append('Changed package '+ref)
        for pin,net in p['nets'].items():
            if net!=other['nets'][pin]:delta.append({'reference':ref,'pin':pin,'from':net,'to':other['nets'][pin]})
    expected=[{'reference':'U4','pin':'3','from':'BUF_3_3','to':'BUF_4_1'},
              {'reference':'U4','pin':'11','from':'BUF_3_4','to':'BUF_4_1'}]
    if delta!=expected:errors.append('Unexpected pin delta')
    ff=functions(new['parts'],defs)
    wanted={'BUF_3_3':[('U1','CLK'),('U2','CLK'),('U3','CLK')],
            'BUF_3_4':[('U5','CLK'),('U6','CLK'),('U7','CLK')],
            'BUF_4_1':[('U4','CLK0'),('U4','CLK1'),('U8','CLK')]}
    groups=[]
    for net,pins in wanted.items():
        actual=sorted((ref,fn) for ref,fs in ff.items() for fn,wire in fs.items() if fn.startswith('CLK') and wire==net)
        if actual!=sorted(pins):errors.append('Clock group '+net)
        groups.append({'net':net,'clock_pins':actual,'input_count':len(actual),
                       'conditional_ci_pf_each':10,'trace_budget_pf':10,'total_budget_pf':len(actual)*10+10})
    vf=functions(video['parts'],video_defs)
    rf=functions(reset['parts'],reset_defs)
    # Actual source is OR(P1,P2), not P0. Preserve this fact before planning
    # pulse improvements; steady-state backend already has50% duty.
    source_net=vf['U11']['D0'];driver=None
    for ref,fs in vf.items():
        if next(p for p in video['parts'] if p['reference']==ref)['part']=='SN74AHC32':
            for i in range(4):
                if fs[f'Y{i}']==source_net:driver={'reference':ref,'channel':i,'inputs':[fs[f'A{i}'],fs[f'B{i}']]}
    if not driver or set(driver['inputs'])!={'P1','P2'} or vf['U11']['CLR0_N']!='+5V':errors.append('Unexpected backend source')
    if (rf['U8']['A0'],rf['U8']['Y0'],rf['U8']['A1'],rf['U8']['Y1'])!=('BACKEND','BACKEND_ROOT','BACKEND_ROOT','ACCESS_CLK'):
        errors.append('Backend distribution changed')
    period=39.721946/(1+50e-6)
    record={'date':'2026-11-26','sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+[
                'tools/check_common_request_topology.py','references/ti/sn74hc74.pdf','references/ti/sn74ahc125.pdf','references/ti/sn74ahc74.pdf']],
            'ics':sum(p['part'] not in ('R','C') for p in new['parts']),'components':len(new['parts']),
            'changed_pins':delta,'clock_groups':groups,'backend_source':{'ff':'video/U11_0','d_net':source_net,'or_driver':driver,
                'asynchronous_clear_disabled':True,'steady_duty':0.5},
            'conditional_steady_pulse_budget':{'source_high_low_ns':2*period,'backend_ahc74_cq_spread_ns':9.5,
                'ahc125_buffer_stages_to_controller':3,'each_buffer_rise_fall_spread_ns':7.5,
                'steady_high_low_lower_ns':2*period-9.5-3*7.5,'hc74_required_clock_pulse_ns_at4v5_minus40_to85':20,
                'scope':'Selected edge bounds, zero source jitter/PCB skew and valid steady phase sequence. Reset transition pulse shape has NOT been bounded; do not apply steady duty formula to reset cuts.'},
            'first_stage_metastability_modeled':False,'extracted_pin_skew_qualified':False,
            'failures':errors,'production_released':False}
    (ROOT/'verification/net24/topology.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'changed_pins':delta,'ics':record['ics'],'clock_input_counts':[r['input_count'] for r in groups],
                      'backend_already_50_percent':True,'conditional_steady_pulse_lower_ns':2*period-9.5-3*7.5,'failures':errors}))
    return int(bool(errors))


if __name__=='__main__':raise SystemExit(main())
