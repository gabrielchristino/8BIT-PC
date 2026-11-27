"""NET36: independent conditional charge budget, not a regulator model.

Preserves NET35 sources/results; tests stress cases and derives requirements.
"""
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'verification/net36'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def voltage(start, current, delay, cap, esr):
    return start - current*(delay/cap + esr)


def main():
    from limited_process import run_limited
    OUT.mkdir(parents=True, exist_ok=True)
    refs = ROOT/'references/net36'
    refs.mkdir(parents=True, exist_ok=True)
    url = 'https://www.analog.com/media/en/technical-documentation/data-sheets/lt3042.pdf'
    capture = dict(url=url, revision='C', transformation='Original response bytes, then pdftotext -layout', original_local_bytes=False)
    pdf = refs/'lt3042.pdf'
    try:
        if not pdf.exists():
            with urllib.request.urlopen(url, timeout=20) as response:
                data = response.read(8*1024*1024)
            assert data.startswith(b'%PDF-'), 'Response is not PDF'
            pdf.write_bytes(data)
        capture.update(original_local_bytes=True, path=pdf.relative_to(ROOT).as_posix(), sha256=sha(pdf), bytes=pdf.stat().st_size)
        extracted = refs/'lt3042.pdf.txt'
        run = run_limited(['pdftotext', '-layout', str(pdf), str(extracted)], ROOT, timeout=20, memory_mb=256, cpu_seconds=10)
        capture['extraction'] = run
        assert run['exit'] == 0 and 'Rev. C' in extracted.read_text()
        capture.update(extracted_sha256=sha(extracted))
    except Exception as error:
        capture['failure'] = repr(error)
    (refs/'capture.json').write_text(json.dumps(capture, indent=2)+'\n')
    # Re-derive all divider corners from native design values, independently
    # of importing/executing the frozen NET35 checker.
    design = json.loads((ROOT/'hardware/vga_sync_window/design.json').read_text())
    values = {p['reference']: p['value'] for p in design['parts']}
    assert all(values[k] == v for k, v in dict(R9='14k', R10='2k', R11='35.1k', R6='2.2k', C2='100uF', C6='10uF').items())
    trips = [ref*(1+top/bottom)+leak*top for ref, top, bottom, leak in itertools.product(
        [F('.405')*F('.98'), F('.405')*F('1.02')], [F(14000)*F('.999'), F(14000)*F('1.001')],
        [F(2000)*F('.999'), F(2000)*F('1.001')], [-F('.000000025'), F('.000000025')])]
    start = min(trips)*F('.95')
    delay, esr, oldcap = F('.0000201'), F('.05'), F('.000047')
    old = json.loads((ROOT/'verification/net35/window-results.json').read_text())['arithmetic']
    baseline = voltage(start, F('.010'), delay, oldcap, esr)
    assert abs(float(baseline)-old['worst_voltage_at_disable_v']) < 1e-12
    old_i_max = (start-3)/(delay/oldcap+esr)
    rows = []
    # Requirements sweep; no named capacitor is qualified by these numbers.
    for uf, ma, us, resistance in itertools.product([47, 100, 150, 220], [10, 15, 20, 25, 30], [20.1, 30, 50], [0.05, 0.1]):
        v = voltage(start, F(ma)/1000, F(str(us))/1000000, F(uf)/1000000, F(str(resistance)))
        rows.append(dict(cap_effective_uf=uf, total_discharge_ma=ma, delay_us=us, esr_ohm=resistance,
                         at_disable_v=float(v), above_3v=v>3, above_3v_by_5mv=v>=F('3.005')))
    # Deliberately conservative sum of resistor paths, with zero driver drop.
    # This is only a partial ledger; do not label it maximum total consumption.
    vmax = F('3.6')
    ledger = dict(bleed=vmax/(2200*F('.99')), sense_divider=vmax/(16000*F('.999')),
                  oe_pullup_low=vmax/(10000*F('.99')),
                  reset_pullup_low=vmax/(4700*F('.99')),
                  two_receiver_high=2*(vmax/2200+F('.0001')),
                  set_resistor_possible_path=vmax/(35100*F('.999')))
    active = sum(ledger[k] for k in ['bleed','sense_divider','oe_pullup_low','two_receiver_high'])
    inhibited = sum(ledger[k] for k in ['bleed','sense_divider','reset_pullup_low'])
    # Recovery sink up to15mA is described on LT3042 RevC p22. Its activation
    # depends on OUTS versus SET and VIN. It is not asserted always active.
    recovery_stress = active + F('.015') + ledger['set_resistor_possible_path']
    required_cap = F('.025')*delay/(start-F('3.005')-F('.025')*esr)
    proposed = voltage(start, F('.025'), delay, F('.000150'), esr)
    assert baseline>3 and voltage(start,F('.025'),delay,oldcap,esr)<3
    assert proposed>F('3.005')
    proxy_cases = [(47,10,20.1,.05,True), (47,25,20.1,.05,False),
                   (150,25,20.1,.05,True), (150,25,50,.05,True), (150,30,50,.1,False)]
    proxies=[]
    for index, (uf,ma,us,r,expected) in enumerate(proxy_cases):
        folder=OUT/'review-proxy'/str(index)
        folder.mkdir(parents=True, exist_ok=True)
        circuit=folder/'discharge.cir'
        circuit.write_text('\n'.join(['NET36 conditional charge stress - NOT vendor regulator or supervisor',
            f'C1 store 0 {uf}u IC={float(start):.17g}',f'R1 store rail {r}',f'I1 rail 0 {ma/1000}',
            '.control','set wr_singlescale','set wr_vecnames',f'tran 5n {us+1}u uic',
            'wrdata values.dat v(rail)','quit','.endc','.end'])+'\n')
        run=run_limited(['ngspice','-b','discharge.cir'],folder,timeout=20,memory_mb=256,cpu_seconds=10,output_mb=2)
        assert run['exit']==0 and not run['wall_timeout']
        samples=[list(map(float,line.split())) for line in (folder/'values.dat').read_text().splitlines()[1:]]
        t,v=min(samples,key=lambda row:abs(row[0]-us*1e-6))
        analytical=float(start)-ma/1000*(t/(uf*1e-6)+r)
        assert abs(v-analytical)<1e-5 and (v>3)==expected
        (folder/'execution.json').write_text(json.dumps(run,indent=2)+'\n')
        proxies.append(dict(effective_uf=uf,ma=ma,delay_us=us,esr_ohm=r,voltage_v=v,
                            above_3v=expected,classified_as_expected=True))
    paths=['tools/check_sync_hold_up_review.py','hardware/vga_sync_window/design.json',
           'verification/net35/window-results.json','references/net20/tps3808.pdf',
           'references/net34/sn74lvc1g132.pdf','references/net23/sn74lvc2g125.pdf']
    sources=[dict(path=p,sha256=sha(ROOT/p)) for p in paths if (ROOT/p).is_file()]
    versions={name:subprocess.run(command,capture_output=True,text=True).stdout for name,command in
              [('ngspice',['ngspice','--version']),('python',['python3','--version'])]}
    report=dict(scope='Conditional charge-budget stress and primary-source review; no hardware change or vendor transient/POR simulation',
        date='2026-11-27',base_commit='2a7fbab2a34c678e15bdde94d1073e52818125d4',command=sys.argv,
        python=platform.python_version(),versions=versions,source_capture=capture,sources=sources,
        start_after_5pct_overdrive_v=float(start),net35_reproduced_v=float(baseline),
        net35_current_limit_for_3v_ma=float(old_i_max*1000),
        partial_resistor_ledger_ma={k:float(v*1000) for k,v in ledger.items()},
        partial_active_ma=float(active*1000),partial_inhibited_ma=float(inhibited*1000),
        recovery_stress_partial_ma=float(recovery_stress*1000),
        recovery_stress_voltage_47uf_v=float(voltage(start,recovery_stress,delay,oldcap,esr)),
        proposed_requirement=dict(total_discharge_ma=25,effective_cap_min_uf=150,esr_max_ohm=.05,
            delay_max_us=20.1,at_disable_v=float(proposed),target_margin_mv=5,
            minimum_uf_for_target_margin=float(required_cap*1000000),qualified=False),
        sweep=rows,passive_proxies=proxies,
        unresolved=['TPS3808 timing at RESET4.7k versus specified100k/50pF; total inhibit path not proven.',
          'No-load recovery sink up to15mA in application text is not a complete full-PVT transient current specification.',
          'Output sink/clamp activation and input collapse must be solved with actual SET dynamics, not assumed concurrent.',
          'Supply/DeltaICC/switching/leakage/cable charge and total discharge remain unbounded.',
          'No exact capacitor part, effective capacitance/ESR/ESL versus temperature/bias/frequency/aging, stability or footprint qualified.',
          '3.6V upper and release margins unchanged; larger capacitor does not solve overshoot, startup, abrupt clamp or POR.'],
        hardware_changed=False,net35_promoted=False,physical_power_qualified=False,production_released=False,failures=[])
    (OUT/'hold-up-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['net35_reproduced_v','net35_current_limit_for_3v_ma',
        'partial_active_ma','recovery_stress_partial_ma','recovery_stress_voltage_47uf_v','proposed_requirement']}))


if __name__=='__main__': main()
