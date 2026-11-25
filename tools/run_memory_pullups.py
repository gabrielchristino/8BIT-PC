"""First-order pull-up RC/leakage sweeps; not a PCB or vendor I/O model."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import subprocess
from build_memory_bus import ROOT,VERIFY


def main():
    out=VERIFY/'rc';out.mkdir(parents=True,exist_ok=True)
    rows=[];errors=[]
    for index,(v,r,c,leak) in enumerate(itertools.product([4.5,5.5],[3135,3465],[30e-12,50e-12,100e-12],[4.5e-6,11e-6])):
        final=v-r*leak
        deck=f'''ISA1 NET13 pull-up model: R tolerance, lumped C and worst sink leakage
VCC supply 0 {v}
RPU supply data {r}
CLOAD data 0 {c}
ILEAK data 0 {leak}
VCTRL ctrl 0 PULSE(1 0 10n .1n .1n 5u 10u)
SLOW data 0 ctrl 0 SW
.model SW SW(Ron=.1 Roff=1e15 Vt=.5 Vh=0)
.tran .5n 5u
.meas tran vh FIND v(data) AT=4.9u
.meas tran rise1090 TRIG v(data) VAL={final*.1} RISE=1 TARG v(data) VAL={final*.9} RISE=1
.end
'''
        source=out/f'corner-{index:02d}.cir';source.write_text(deck)
        cmd=['ngspice','-b',str(source)];p=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        (out/f'corner-{index:02d}.log').write_text(p.stdout+p.stderr)
        high=re.search(r'^vh\s*=\s*([\deE+.-]+)',p.stdout,re.M);rise=re.search(r'^rise1090\s*=\s*([\deE+.-]+)',p.stdout,re.M)
        if p.returncode or not high or not rise:errors.append(index);continue
        high=float(high[1]);rise=float(rise[1]);formula=math.log(9)*r*c
        if abs(high-final)>.005 or abs(rise-formula)>formula*.005:errors.append(index)
        rows.append({'corner':index,'command':cmd,'exit':p.returncode,'supply_v':v,'resistance_ohm':r,'lumped_cap_pf':c*1e12,'sink_leakage_ua':leak*1e6,
          'measured_high_v':high,'calculated_high_v':final,'measured_rise_10_90_ns':rise*1e9,'calculated_rise_10_90_ns':formula*1e9,
          'meets_conservative_500ns_rise':rise<=500e-9,'within_rc_budget':c<=50e-12})
    if len(rows)!=24 or not all(r['meets_conservative_500ns_rise']==r['within_rc_budget'] for r in rows):errors.append('RC budget/calibration coverage')
    pdfs=[ROOT/p for p in ['references/ti/sn74hct244.pdf','references/ti/sn74ahc125.pdf','references/ti/sn74ahct157.pdf','references/alliance/as7c256a.pdf','references/microchip/at28c256-industrial.pdf']]
    report={'date':'2026-11-25','ngspice':subprocess.run(['ngspice','--version'],capture_output=True,text=True).stdout.splitlines(),
      'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [Path(__file__),*pdfs]],
      'scope':'Lumped first-order RC + DC leakage only. 50pF is an RC test budget, not approval of SRAM load conditions; read access is specified at 30pF and Hi-Z timing at 5pF. Actual PCB/device output capacitance and full-temperature loading remain unclosed.',
      'rise_limit_used_ns':500,'pullup_nominal_ohm':3300,'tolerance_fraction':.05,
      'dc_checks':{'ttl_receiver_vih_v':2,'ttl_receiver_vil_v':.8,'memory_voh_min_v':2.4,'eeprom_vol_max_v':.45,'sram_vol_max_v':.4,
        'high_logic_margin_v':.4,'eeprom_low_logic_margin_v':.35,'eeprom_pullup_sink_ma_at_5v5':(5.5-.45)/3135*1000,'eeprom_guaranteed_sink_ma':2.1},
      'rows':rows,'failures':errors,'full_electrical_approval':False,'production_released':False}
    (VERIFY/'rc-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'corners':len(rows),'in_budget_passed':sum(r['within_rc_budget'] and r['meets_conservative_500ns_rise'] for r in rows),'out_of_budget_rejected':sum(not r['within_rc_budget'] and not r['meets_conservative_500ns_rise'] for r in rows),'failures':errors,'full_electrical_approval':False}));return int(bool(errors))


if __name__=='__main__':raise SystemExit(main())
