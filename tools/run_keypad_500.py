"""NET-17: conditional 500-ohm keypad envelope, with real resistor networks.

Separate resistor variant. Do not confuse direct-contact recognition with exact
Boolean ghost closure for arbitrarily large chords. Physical units unmeasured.
"""
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net17'
COLUMN_PULLUP=270000;ROW_PULLUP=120000


def reachable(keys,row):
    nodes={row}
    while True:
        nxt=nodes.copy()
        for r,c in keys:
            if r in nodes:nxt.add(4+c)
            if 4+c in nodes:nxt.add(r)
        if nxt==nodes:return {c for c in range(16) if 4+c in nodes}
        nodes=nxt


def solve(keys,row,supply,tol,leak,contact,isolation,series):
    # Independent 20-node DC solution; driver is a clamped VOL envelope with
    # 0.01ohm switch resistance, matching the SPICE deck, not a transistor I/V.
    a=[[0.0]*20 for _ in range(20)];b=[0.0]*20
    for n in range(20):
        resistance=(ROW_PULLUP if n<4 else COLUMN_PULLUP)*tol
        a[n][n]=1/resistance;b[n]=supply/resistance+leak*(3e-6 if n<4 else 1.25e-6)
    for r in range(4):
        for c in range(16):
            n=4+c;g=1/((contact if (r,c) in keys else isolation)+20)
            a[r][r]+=g;a[n][n]+=g;a[r][n]-=g;a[n][r]-=g
    driver_g=1/(series+.01);a[row][row]+=driver_g;b[row]+=.44*driver_g
    original=[x[:] for x in a];rhs=b[:]
    for k in range(20):
        pivot=max(range(k,20),key=lambda n:abs(a[n][k]));a[k],a[pivot]=a[pivot],a[k];b[k],b[pivot]=b[pivot],b[k]
        for n in range(k+1,20):
            ratio=a[n][k]/a[k][k]
            for j in range(k+1,20):a[n][j]-=ratio*a[k][j]
            b[n]-=ratio*b[k]
    x=[0.0]*20
    for k in range(19,-1,-1):x[k]=(b[k]-sum(a[k][j]*x[j] for j in range(k+1,20)))/a[k][k]
    residual=max(abs(sum(original[n][j]*x[j] for j in range(20))-rhs[n]) for n in range(20))
    return x,residual


def run_case(spec):
    i,pattern,keys,start,end,supply,tol,leak,contact,isolation,cap,series,negative=spec
    folder=OUT/'rc';path=folder/f'matrix-{i:03d}.cir';log=path.with_suffix('.log')
    lines=[f'NET17 conditional keypad {pattern} corner {i}',f'VCC vcc 0 {supply}','VDRV drv 0 0.44']
    for r in range(4):
        initial=int(r==start);final=int(r==end)
        lines += [f'VSEL{r} ctl{r} 0 PWL(0 {initial} 19.999u {initial} 20u {final})',f'SROW{r} drive{r} drv ctl{r} 0 ROW',f'RS{r} drive{r} n{r} {series}']
    lines+=['.model ROW SW(Ron=0.01 Roff=1e15 Vt=0.5 Vh=0)']
    for n in range(20):
        lines += [f'RP{n} vcc n{n} {(ROW_PULLUP if n<4 else COLUMN_PULLUP)*tol}',f'CP{n} n{n} 0 {cap}',f'IL{n} 0 n{n} {leak*(3e-6 if n<4 else 1.25e-6)}']
    for r in range(4):
        for c in range(16):lines.append(f'RK{r}_{c} n{r} n{4+c} {(contact if (r,c) in keys else isolation)+20}')
    lines+=['.tran 0.5u 4m']
    # Observe 2ms after changing rows and the actual 16384-cycle guard.
    for c in range(16):
        lines += [f'.measure tran c{c}_settled FIND V(n{c+4}) AT=2.02m',f'.measure tran c{c}_guard FIND V(n{c+4}) AT={20e-6+16384/(25175000/4)}']
    lines += ['.measure tran sink FIND I(VDRV) AT=3.99m','.end']
    path.write_text('\n'.join(lines)+'\n');command=['ngspice','-b',str(path)]
    p=subprocess.run(command,capture_output=True,text=True,timeout=30);output=p.stdout+p.stderr;log.write_text(output)
    measured={k:float(v) for k,v in re.findall(r'^(c\d+_(?:settled|guard)|sink)\s*=\s*([-+\d.eE]+)',output,re.M)}
    final,residual=solve(keys,end,supply,tol,leak,contact,isolation,series);closure=reachable(keys,end)
    direct={c for r,c in keys if r==end};unconnected=set(range(16))-closure
    violations=[]
    if p.returncode or len(measured)!=33:violations.append('SPICE execution/measurements')
    else:
        for when in ('settled','guard'):
            for c in direct:
                if measured[f'c{c}_{when}']>=1.35:violations.append(f'Actual key not guaranteed low c{c}/{when}')
            for c in unconnected:
                if measured[f'c{c}_{when}']<=3.85:violations.append(f'Unconnected column not guaranteed high c{c}/{when}')
        # A global infinity-norm supersolution is valid only for this lumped
        # model, where every capacitive node also has its own VCC pull-up.
        error_bound=6*math.exp(-.002/(COLUMN_PULLUP*1.05*cap))
        if max(abs(measured[f'c{c}_settled']-final[c+4]) for c in range(16))>error_bound+.00002:violations.append('Transient/independent DC envelope mismatch')
        if abs(measured['sink'])>.008:violations.append('Driver current budget')
    if residual>1e-9:violations.append('DC solution residual')
    expected_negative={'contact resistance outside budget':'Actual key not guaranteed low',
      'isolation outside budget':'Unconnected column not guaranteed high',
      'capacitance outside budget':'Unconnected column not guaranteed high'}
    passed=(p.returncode==0 and len(measured)==33 and residual<=1e-9 and any(v.startswith(expected_negative[negative]) for v in violations)) if negative else not violations
    return {'index':i,'pattern':pattern,'keys':sorted(keys),'from_row':start,'to_row':end,'supply_v':supply,'pullup_tolerance_factor':tol,'row_series_ohm':series,'leakage_sign':leak,'contact_ohm':contact,'isolation_assumed_ohm':isolation,'capacitance_per_common_net_f':cap,
      'negative':negative,'command':command,'exit':p.returncode,'deck':path.relative_to(ROOT).as_posix(),'log':log.relative_to(ROOT).as_posix(),'measures':measured,'dc_columns_v':final[4:],'dc_residual_a':residual,
      'direct_columns':sorted(direct),'unconnected_columns':sorted(unconnected),'ghost_columns_not_qualified':sorted(closure-direct),'violations':violations,
      'passed':passed}


def main():
    (OUT/'rc').mkdir(parents=True,exist_ok=True)
    parts=json.loads((ROOT/'hardware/keyboard_500/design.json').read_text())['parts']
    values={p['reference']:p.get('value') for p in parts if p['part']=='R'}
    expected={**{f'R{i}':'270k' for i in range(1,17)},**{f'R{i}':'120k' for i in range(17,21)},**{f'R{i}':'820' for i in range(21,25)}}
    if values!=expected:raise ValueError('Analog values do not match native resistor inventory')
    paths=['tools/run_keypad_500.py','hardware/keyboard_500/design.json','references/ti/sn74ahc14.pdf','references/ti/sn74ahc125.pdf','verification/net17/source-status.json']
    report={'date':'2026-11-26','python':platform.python_version(),'ngspice':subprocess.run(['ngspice','--version'],capture_output=True,text=True).stdout,
      'scope':'Conditional 500-ohm direct contacts, stable complete frames and conservative <=2-key admission; exact arbitrary ghost voltages/physical units not approved',
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in paths],
      'assumptions':{'contact_max_ohm':500,'column_pullup_ohm':COLUMN_PULLUP,'row_pullup_ohm':ROW_PULLUP,'pullup_tolerance':.05,'row_series_ohm':820,'row_series_tolerance':.01,'settling_budget_s':.002,'native_guard_cycles':16384,'native_guard_s':16384/(25175000/4),'series_wire_ohm_per_key_path':20,'isolation_min_ohm_in_operating_range':100e6,'isolation_measured':False,
      'row_intrinsic_leak_abs_a':3e-6,'column_intrinsic_leak_abs_a':1.25e-6,'row_total_leak_budget_a':4e-6,'column_total_leak_budget_a':1.5e-6,'capacitance_per_common_net_max_f':1e-9,
      'initial_node_error_bound_v':6.0,'driver_pin_local_load_budget_f':50e-12,
      'topology':'20 lumped common row/column nodes, capacitors to ground and own pull-up at every node; 10ohm per contact leg folded into key edge; no distributed PCB/pad model'},
      'runs':[],'negative':[],'failures':[],'production_released':False}
    current_bound=5.5*(16/(COLUMN_PULLUP*.95)+4/(ROW_PULLUP*.95))+40e-6;direct_bound=.44+(820*1.01+520)*current_bound
    high_bound=4.5-max(ROW_PULLUP*1.05*4e-6,COLUMN_PULLUP*1.05*1.5e-6)
    error=6*math.exp(-.002/(COLUMN_PULLUP*1.05*1e-9))
    report['analytic_bounds']={'direct_low_dc_upper_v':direct_bound,'unconnected_high_dc_lower_v':high_bound,'sink_current_dc_upper_a':current_bound,'sink_current_transient_upper_a':6/(820*.99),'max_lumped_tau_s':COLUMN_PULLUP*1.05e-9,'error_after_settling_budget_upper_v':error,
      'low_margin_after_settling_budget_v':1.35-direct_bound-error,'high_margin_after_settling_budget_v':high_bound-error-3.85,
      'row_open_contact_leak_max_a':16*5.5/100e6,'column_open_contact_leak_max_a':4*5.5/100e6,
      'proof_scope':'Passive-network maximum principle and monotone positive conductance equations within the stated lumped model; no assumption that all ghost columns reach low'}
    if direct_bound+error>=1.35 or high_bound-error<=3.85 or current_bound>.008:report['failures'].append('Analytic admission envelope')
    patterns=[('empty',set()),('single-old',{(0,0)}),('single-new',{(1,0)}),('pair-row',{(0,0),(0,15)}),('pair-column',{(0,0),(1,0)}),('pair-diagonal',{(0,0),(1,15)}),
      ('L-local',{(0,0),(1,0),(1,1)}),('L-cross-module',{(0,0),(1,0),(1,15)}),('rectangle',{(0,0),(1,0),(0,15),(1,15)}),
      ('chain-seven',{(0,0),(1,0),(1,1),(2,1),(2,2),(3,2),(3,15)}),('all-64',set(itertools.product(range(4),range(16)))),
      ('bottleneck',{(0,0)}|{(1,c) for c in range(16)}|{(2,15),(3,15)})]
    specs=[]
    for (name,keys),start,contact,supply,tol,leak,series in itertools.product(patterns,(0,1),(10,500),(4.5,5.5),(.95,1.05),(-1,1),(820*.99,820*1.01)):
        specs.append((len(specs),name,keys,start,1-start,supply,tol,leak,contact,100e6,1e-9,series,None))
    specs += [(len(specs),'excess-contact',patterns[-1][1],1,0,5.5,.95,1,5000,100e6,1e-9,820*1.01,'contact resistance outside budget')]
    specs += [(len(specs),'excess-open-leak',set(),0,1,4.5,1.05,-1,500,100000,1e-9,820*1.01,'isolation outside budget')]
    specs += [(len(specs),'excess-capacitance',{(0,0)},0,1,4.5,1.05,-1,500,100e6,20e-9,820*1.01,'capacitance outside budget')]
    def save():(OUT/'electrical-results.json').write_text(json.dumps(report,indent=2)+'\n')
    with ThreadPoolExecutor(max_workers=3) as pool:
        for row in pool.map(run_case,specs):
            report['negative' if row['negative'] else 'runs'].append(row)
            if not row['passed']:report['failures'].append(row['index'])
            if row['index']%64==0:save();print(json.dumps({'completed':row['index']+1,'total':len(specs),'failures':report['failures']}),flush=True)
    report['normal_scenarios']=len(report['runs']);report['negative_scenarios']=len(report['negative']);save()
    print(json.dumps({'normal_scenarios':report['normal_scenarios'],'negative_scenarios':report['negative_scenarios'],'analytic_bounds':report['analytic_bounds'],'failures':report['failures'],'production_released':False}));return int(bool(report['failures']))


if __name__=='__main__':raise SystemExit(main())
