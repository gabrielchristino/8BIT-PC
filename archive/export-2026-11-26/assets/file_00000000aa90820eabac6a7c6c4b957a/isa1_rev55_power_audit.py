#!/usr/bin/env python3
"""ISA-1 rev5.5: deterministic logic audit, NOT analog/electrical simulation."""
import itertools,json,pathlib
P=pathlib.Path(__file__).parent
checks=0
rows=[]
for pg,run,decoded,request in itertools.product((0,1),repeat=4):
    # Requests and decoding are untrusted while CPU is not running.
    write_permit=bool(pg and run and decoded and request)
    we_n=not write_permit
    assert we_n or (pg and run and decoded and request)
    if not pg or not run: assert we_n
    rows.append(dict(power_good=pg,cpu_run=run,address_decoded=decoded,write_request=request,WE_N=int(we_n)))
    checks+=3
# Explicit regression: simple decode/request only is unsafe in brownout.
unsafe=[r for r in rows if not r['power_good'] and r['address_decoded'] and r['write_request']]
assert len(unsafe)==2
checks+=1
# A supervised release still needs an actual oscillator and reset synchronizer.
for initial in range(65536):
    ff=[0,0,0]
    pc=initial
    # asynchronous supervisor assertion clears FF, PC only at clock edge
    for edge in range(1,5):
        run_before=ff[2]
        clr_n_before=ff[1]
        if not clr_n_before: pc=0
        elif run_before: pc=(pc+1)&0xffff
        ff=[1,ff[0],ff[1]]
        if edge<=3: assert pc==0
        if edge==4: assert pc==1
        checks+=1
out={'revision':'5.5','scope':'ideal boolean write inhibit and synchronous startup only','assertions':checks,'errors':0,'truth_table':rows,'unsafe_simple_decode_cases':len(unsafe),'power_failsafe_verified':False,'analog_simulation':False,'erc':False}
(P/'isa1_rev55_results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print('PASS',checks,'logical assertions; physical power-fail safety NOT validated')
