"""NET-16A pre-design RC reset-order envelope, not a native circuit approval."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net16'


def main():
    folder=OUT/'rc';folder.mkdir(parents=True,exist_ok=True)
    report={'date':'2026-11-25','scope':'Pre-design first-order RC timing contract, no native schematic, supervisor/BOM/PCB/PVT approval',
      'ngspice':subprocess.run(['ngspice','--version'],capture_output=True,text=True).stdout,
      'assumptions':{'resistor_ohm':10000,'resistor_tolerance':0.01,'capacitor_f':1e-9,'capacitor_tolerance':0.05,'capacitor_technology_required':'C0G or equivalent bounded effective capacitance; no part selected',
      'leakage_abs_a':1e-6,'raw_low_max_v':0.3,'raw_high_min_v':4.5,'raw_low_min_s':30e-6,'schmitt_global_hysteresis_min_v':0.4,
      'we_disable_selected_max_s':40e-9,'extra_order_guard_s':100e-9,'backend_period_s':4/25175000,
      'external_release_resolution':'Metastability and actual synchronizer choice remain open; no bounded analog resolution assumed'},
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in ('tools/run_reset_order_envelope.py','references/ti/sn74ahc14.pdf','references/power-candidates/tlv803e.pdf')],
      'rows':[],'negative':[],'failures':[],'production_released':False}
    def save():(OUT/'reset-order-envelope.json').write_text(json.dumps(report,indent=2)+'\n')
    cases=[]
    for rtol,ctol,leak,low,supply in itertools.product((.99,1.01),(.95,1.05),(-1e-6,1e-6),(0,.3),(4.5,5.5)):
        # The 3.75 -> 3.35 pair with 0.4V hysteresis is a conservative global
        # bound, not a claim those extrema occur together in an actual device.
        for initial,threshold in [(3.75,3.35),(supply,1.35)]:cases.append(('fall',10000*rtol,1e-9*ctol,leak,low,initial,threshold,True))
        for threshold in (1.75,3.85):cases.append(('rise',10000*rtol,1e-9*ctol,leak,supply,low,threshold,True))
    # Deliberately remove almost all capacitance: inhibit can then lose the race.
    cases.append(('fall',9900,1e-12,-1e-6,0,3.75,3.35,False))
    for i,(mode,res,cap,leak,source,initial,threshold,qualified) in enumerate(cases):
        deck=f'''Reset-order first-order envelope {i}
VRAW source 0 {source}
RDELAY source delayed {res}
CDELAY delayed 0 {cap} IC={initial}
ILEAK 0 delayed {leak}
.tran 0.01u 100u UIC
.measure tran crossing WHEN V(delayed)={threshold} {'FALL' if mode=='fall' else 'RISE'}=1
.end
'''
        path=folder/f'order-{i:03d}.cir';log=path.with_suffix('.log');path.write_text(deck)
        cmd=['ngspice','-b',str(path)];p=subprocess.run(cmd,capture_output=True,text=True,timeout=20);output=p.stdout+p.stderr;log.write_text(output)
        found=re.search(r'^crossing\s*=\s*([-+\d.eE]+)',output,re.M)
        row={'index':i,'mode':mode,'r_ohm':res,'c_f':cap,'leak_a':leak,'source_v':source,'initial_v':initial,'threshold_v':threshold,'within_budget':qualified,'command':cmd,'exit':p.returncode,'deck':path.relative_to(ROOT).as_posix(),'log':log.relative_to(ROOT).as_posix()}
        if p.returncode or not found:report['failures'].append('Simulation '+str(i))
        else:
            measured=float(found.group(1));final=source+leak*res;analytic=-res*cap*math.log((threshold-final)/(initial-final))
            row.update(crossing_s=measured,analytic_s=analytic)
            if abs(measured-analytic)>max(5e-9,analytic*.003):report['failures'].append('Analytic cross-check '+str(i))
            if mode=='fall':row['order_passed']=measured>140e-9
            else:row['release_delay_passed']=measured<30e-6
            if qualified and ((mode=='fall' and (not row['order_passed'] or measured+35e-9>=30e-6)) or (mode=='rise' and not row['release_delay_passed'])):report['failures'].append('Contract '+str(i))
            if not qualified:
                report['negative'].append({'case':'Almost no RC delay','passed':not row['order_passed'],'observed_s':measured})
        report['rows'].append(row);save()
        if report['failures']:print(json.dumps({'failures':report['failures'],'last':row}));return 1
    qualified=[r for r in report['rows'] if r['within_budget']]
    report['summary']={'qualified_scenarios':len(qualified),'min_assert_delay_s':min(r['crossing_s'] for r in qualified if r['mode']=='fall'),
      'max_assert_delay_s':max(r['crossing_s'] for r in qualified if r['mode']=='fall'),'max_charge_delay_s':max(r['crossing_s'] for r in qualified if r['mode']=='rise')}
    # Optimistically apply the stated 50us maximum propagation at a near-trip
    # point, although the PDF actually specifies a much larger step/overdrive.
    # Failure even under this optimistic assumption rejects the simple design;
    # passing a row cannot qualify that assumption.
    report['supervisor_hold_up_screen']=[{'load_a':load,'nominal_cap_f':cap,'effective_cap_f':cap*.8,'optimistic_trip_min_v':4.63*.98,
      'optimistic_delay_s':50.04e-6,'optimistic_rail_at_inhibit_v':4.63*.98-load*50.04e-6/(cap*.8),
      'model_above_4v5':4.63*.98-load*50.04e-6/(cap*.8)>=4.5,'qualified':False}
      for load,cap in itertools.product((.25,.5,1,1.5),(220e-6,470e-6,1000e-6,2200e-6))]
    report['negative'].append({'case':'Unstretched raw reset shorter than RC assertion','raw_pulse_s':.1e-6,'passed':.1e-6<report['summary']['min_assert_delay_s'],'reason':'Such a pulse cannot guarantee bank reset; input pulse stretcher is required, not silently filtered as a completed reset'})
    if not all(x['passed'] for x in report['negative']):report['failures'].append('Negative calibration')
    save();print(json.dumps({'summary':report['summary'],'negative':report['negative'],'failures':report['failures'],'production_released':False}));return int(bool(report['failures']))


if __name__=='__main__':raise SystemExit(main())
