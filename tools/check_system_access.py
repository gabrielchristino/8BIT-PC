"""Prove the variant changes only three package types, not the state logic."""
import hashlib
import json
from pathlib import Path
import subprocess
from build_system_access import ROOT,OUT,VERIFY,KICAD


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    old=ROOT/'hardware/keyboard_access'
    before=json.loads((old/'design.json').read_text())['parts']
    after=json.loads((OUT/'design.json').read_text())['parts']
    changes=[];failures=[]
    if len(before)!=len(after):failures.append('Inventory changed')
    for a,b in zip(before,after):
        a=dict(a);b=dict(b)
        if a['part']!=b['part']:
            changes.append({'reference':a['reference'],'from':a['part'],'to':b['part']})
            b['part']=a['part']
        if a!=b:failures.append('Net/pin/passive/placement changed '+a['reference'])
    expected=[{'reference':f'U{i}','from':'SN74HC174','to':'SN74AHC174'} for i in range(1,4)]
    if changes!=expected:failures.append('Unexpected part substitution')
    source=(old/'keyboard_access_netlist.sv').read_text()
    projected=source.replace('module keyboard_access_netlist #(parameter TIMED=0)','module system_access_netlist #(parameter TIMED=0,EARLY=0)').replace('hc174_model #(.TIMED(TIMED))','net19_ahc174 #(.TIMED(TIMED),.EARLY(EARLY))')
    if projected!=(OUT/'system_access_netlist.sv').read_text():failures.append('Digital logic changed beyond package models')
    defs=json.loads((OUT/'package-functions.json').read_text())
    if defs['SN74HC174']['pins']!=defs['SN74AHC174']['pins']:failures.append('Package pin incompatibility')
    sources=['tools/check_system_access.py','hardware/keyboard_access/design.json','hardware/system_access/design.json',
             'hardware/keyboard_access/keyboard_access_netlist.sv','hardware/system_access/system_access_netlist.sv',
             'sim/net19a/package_models.sv','references/ti/sn74ahc174.pdf']
    report={'date':'2026-11-26','sources':[{'path':n,'sha256':digest(ROOT/n)} for n in sources],
            'changes':changes,'same_pin_logic_except_package_models':not failures,
            'selected_limits':{'supply_v':[4.5,5.5],'temperature_c':[-40,85],'cl_max_pf':50,
                'clock_q_max_ns':10.5,'clock_q_min_ns':1,'async_clear_max_ns':11,
                'data_setup_ns':4.5,'data_hold_ns':.5,'clear_recovery_ns':2.5,'clear_clock_pulse_min_ns':5,
                'input_capacitance_max_pf':10,'static_icc_max_a':40e-6,
                'dynamic_cpd':'Typical only; not a guaranteed board current bound'},
            'limits_scope':'TI SCLS425H tables 5.3/5.5/5.7/5.9; no all-independent min/max/skew/load or PCB signoff',
            'failures':failures,'production_released':False}
    (VERIFY/'equivalence-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'physical_substitutions':changes,'same_pin_logic':not failures,'failures':failures}));return int(bool(failures))


if __name__=='__main__':raise SystemExit(main())
