"""NET-15 conditional electrical envelope, not a measured membrane model.

Conservative resistance bound moves all 16 pull-ups/capacitors to the far end
of a maximum seven-contact path through the four-row undioded graph. Leakage
envelope raises the low state, then lowers the released high state. Driver
VOL is clamped at a proposed guaranteed upper bound, not a transistor I/V.
"""
import hashlib
import itertools
import json
from pathlib import Path
import platform
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net15'


def main():
    folder=OUT/'rc';folder.mkdir(parents=True,exist_ok=True)
    report={'date':'2026-11-25','iteration':'NET-15','python':platform.python_version(),
      'ngspice':subprocess.run(['ngspice','--version'],capture_output=True,text=True).stdout,
      'scope':'Conditional first-order resistance/RC envelope, no measured units or vendor pad/ESD/CDC/bounce/PCB approval',
      'assumptions':{'pullup_ohm':100000,'tolerance_fraction':0.05,'contact_max_ohm':150,'shared_row_wire_max_ohm':10,
        'max_contacts_in_simple_path':7,'max_rows_in_path':4,'effective_capacitance_per_column_max_f':1e-9,
        'column_leakage_envelope_a':2e-6,'driver_vol_clamp_v':0.44,'driver_sink_limit_a':0.008,
        'global_negative_threshold_min_v':1.35,'global_positive_threshold_max_v':3.85,
        'settling_limit_s':0.001,'native_guard_cycles':8192,'backend_hz':25175000/4,
        'native_guard_s':8192/(25175000/4),'parameters_measured':False},
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in ['tools/run_keypad_envelope.py','references/ti/sn74ahc14.pdf','references/ti/sn74ahc125.pdf']],
      'rows':[],'failures':[],'physical_approval':False}
    def save():(OUT/'electrical-envelope.json').write_text(json.dumps(report,indent=2)+'\n')
    # C=20nF and contact=250 ohm intentionally exceed qualification budgets.
    cases=list(itertools.product((4.5,5.5),(0.95,1.05),(10,100,150,250),(0.1,10),(100e-12,1e-9,20e-9)))
    for index,(supply,tolerance,contact,wire,cap) in enumerate(cases):
        pullup=100000*tolerance;path_r=7*contact+4*wire
        deck=f'''Conditional keypad path bound, corner {index}
VCC vcc 0 {supply}
VDRV drv 0 0.44
VSW control 0 PWL(0 1 19.999u 1 20u 0)
SINK common drv control 0 SW
.model SW SW(Ron=0.01 Roff=1e12 Vt=0.5 Vh=0)
RPATH common columns {path_r}
RPULL vcc columns {pullup/16}
CCOL columns 0 {cap*16}
* Low-state leakage sources current into the input; after release use the
* opposite worst-case sign. This is an envelope, not a vendor input model.
ILEAK vcc columns PWL(0 32u 19.999u 32u 20u -32u)
.tran 1u 10m
.measure tran low_column FIND V(columns) AT=19u
.measure tran sink_current FIND I(VDRV) AT=19u
.measure tran high_column FIND V(columns) AT=9.99m
.measure tran threshold_cross WHEN V(columns)=3.85 RISE=1 TD=20u
.end
'''
        source=folder/f'corner-{index:03d}.cir';log=folder/f'corner-{index:03d}.log';source.write_text(deck)
        command=['ngspice','-b',str(source)]
        proc=subprocess.run(command,capture_output=True,text=True,timeout=30);output=proc.stdout+proc.stderr;log.write_text(output)
        measures={k:float(v) for k,v in re.findall(r'^(low_column|sink_current|high_column|threshold_cross)\s*=\s*([-+\d.eE]+)',output,re.M)}
        row={'corner':index,'supply_v':supply,'pullup_ohm':pullup,'contact_ohm':contact,'shared_row_wire_ohm':wire,'effective_column_cap_f':cap,
          'path_ohm':path_r,'command':command,'exit':proc.returncode,'measures':measures,
          'within_qualification_budget':contact<=150 and wire<=10 and cap<=1e-9,
          'deck':source.relative_to(ROOT).as_posix(),'log':log.relative_to(ROOT).as_posix()}
        if proc.returncode or len(measures)!=4:
            report['failures'].append(f'Corner {index} simulation/measurement failed')
        else:
            settling=measures['threshold_cross']-20e-6
            row.update(settling_s=settling,low_passed=measures['low_column']<1.35,
              high_passed=measures['high_column']>3.85,current_passed=abs(measures['sink_current'])<=0.008,settling_passed=settling<=0.001)
            row['envelope_passed']=all(row[k] for k in ('low_passed','high_passed','current_passed','settling_passed'))
            # Require deliberate out-of-budget calibration to be rejected;
            # never count those corners as a physical approval.
            if row['envelope_passed']!=row['within_qualification_budget']:report['failures'].append(f'Corner {index} acceptance/calibration mismatch')
            # Independent DC calculation for the linear low-state model.
            equivalent=pullup/16;expected=(supply/equivalent+0.44/(path_r+0.01)+32e-6)/(1/equivalent+1/(path_r+0.01))
            row['dc_formula_v']=expected
            if abs(expected-measures['low_column'])>0.005:report['failures'].append(f'Corner {index} DC formula mismatch')
        report['rows'].append(row);save()
        if report['failures']:
            print(json.dumps({'failures':report['failures'],'last':row}),flush=True);return 1
    report['qualified_model_corners']=sum(r['within_qualification_budget'] for r in report['rows'])
    report['rejected_calibrations']=sum(not r['within_qualification_budget'] for r in report['rows'])
    save();print(json.dumps({'corners':len(cases),'qualified_model_corners':report['qualified_model_corners'],'rejected_calibrations':report['rejected_calibrations'],'failures':report['failures'],'physical_approval':False}));return 0


if __name__=='__main__':raise SystemExit(main())
