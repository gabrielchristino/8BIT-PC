"""Test conservative frame admission, cancellation and queue atomicity."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import platform
import random
import time

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net17'
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main():
    started=time.monotonic();reference=module('revisions/rev983/keyboard.py','historical_keyboard_reference')
    Policy=module('sim/net17/keypad_policy.py','candidate_keypad_policy').KeypadPolicy
    electrical=json.loads((OUT/'electrical-results.json').read_text())
    assert not electrical['failures'] and electrical['normal_scenarios']==768
    assert electrical['analytic_bounds']['low_margin_after_settling_budget_v']>0 and electrical['analytic_bounds']['high_margin_after_settling_budget_v']>0
    paths=['tools/run_keypad_policy.py','sim/net17/keypad_policy.py','revisions/rev983/keyboard.py','verification/net17/electrical-results.json']
    report={'date':'2026-11-26','python':platform.python_version(),'scope':'New host reference only, complete stable frames, conditional analog bound; no CPU firmware, arbitrary mixed-frame coherence or measured hardware approval',
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in paths], 'counts':{},'negative':[],'failures':[],'production_released':False}
    keys=list(itertools.product(range(4),range(16)))
    def mask(points):return sum(1<<(r*16+c) for r,c in points)
    cases=observations=legacy_triples=0
    for size in range(4):
        for pressed in itertools.combinations(keys,size):
            actual=mask(pressed);rows=reference.scan(set(pressed));closed=mask((r,c) for r,s in enumerate(rows) for c in s)
            # Direct contacts are guaranteed; distant ghosts may resolve
            # either way. For >2 actual keys, even the minimal observation
            # must block. <=2 has no closed-contact ghost paths.
            for observed in (actual,closed):
                admitted=Policy.admit_static(observed)
                assert admitted==(actual if size<=2 else None)
                observations+=1
            if size==3 and reference.decode(rows)[0]:legacy_triples+=1
            cases+=1
    report['counts'].update(exhaustive_static_sets_0_to_3=cases,extreme_observations=observations,legacy_three_key_sets_with_some_admitted_keys=legacy_triples)
    rng=random.Random(0x17500);large=0
    for _ in range(10000):
        pressed=set(rng.sample(keys,rng.randrange(4,65)));actual=mask(pressed);rows=reference.scan(pressed)
        closure=mask((r,c) for r,s in enumerate(rows) for c in s)
        ghosts=closure & ~actual
        observed=actual | (ghosts & rng.getrandbits(64))
        assert Policy.admit_static(observed) is None;large+=1
    report['counts']['random_large_partial_ghost_frames']=large
    def feed(p,frame,n=3):
        for _ in range(n):p.update(frame)
    p=Policy();feed(p,0);assert not p.blocked
    for frame in [1,0,1,0,1,0]:p.update(frame)
    assert not p.drain() and p.active==0
    feed(p,1);assert p.drain()==[('PRESS',0)]
    feed(p,(1<<16)|(1<<17));assert p.drain()==[('RELEASE',0),('PRESS',16),('PRESS',17)]
    p.update((1<<0)|(1<<16)|(1<<17));assert p.blocked and p.active==0
    assert p.drain()==[('CANCEL','more_than_two_keys'),('ALL_UP',None)]
    feed(p,1,8);assert p.blocked and not p.drain()
    feed(p,0,2);p.update(1);assert p.blocked
    feed(p,0);assert not p.blocked;feed(p,1);assert p.drain()==[('PRESS',0)]
    p.cancel('reset');assert p.active==0 and p.blocked and p.drain()==[('CANCEL','reset'),('ALL_UP',None)]
    p=Policy(capacity=4);feed(p,0);feed(p,1);feed(p,3)
    assert list(p.events)==[('PRESS',0),('PRESS',1)]
    feed(p,12);assert p.overflows==1 and p.blocked and p.active==0
    assert p.drain()==[('CANCEL','queue_overflow'),('ALL_UP',None)]
    report['stateful_sequences']=['startup requires stable empty','bounce suppressed','releases before presses','ambiguity cancels immediately','no rearm while held','stable-empty rearm','reset discards stale events','queue overflow cancels atomically']
    p=Policy(capacity=4);consumer=0;drains=0
    for _ in range(100000):
        frame=mask(rng.sample(keys,rng.randrange(4)))
        if rng.randrange(3)==0:feed(p,frame)
        else:p.update(frame)
        if rng.randrange(100)==0:p.cancel('reset')
        assert p.active.bit_count()<=2 and len(p.events)<=p.capacity
        if p.blocked:assert p.active==0
        if rng.randrange(4)==0:
            for kind,value in p.drain():
                if kind in ('CANCEL','ALL_UP'):consumer=0
                elif kind=='RELEASE':consumer &= ~(1<<value)
                else:assert kind=='PRESS';consumer |= 1<<value
                assert consumer.bit_count()<=2
            assert consumer==p.active;drains+=1
    report['counts'].update(stateful_random_steps=100000,consumer_drains=drains)
    # Calibrate that accepting a third bit violates the chosen admission
    # contract, even when every bit happens to be a real, unambiguous key.
    bad=7 if (7).bit_count()<=3 else None
    report['negative'].append({'case':'Admit a third key','expected_rejection':True,'passed':bad is not None and Policy.admit_static(7) is None})
    # Three identical sequential scan frames are still not proof that all
    # physical contacts coexisted. Keep this counterexample as a limitation.
    mixed=Policy();feed(mixed,0);feed(mixed,(1<<0)|(1<<16))
    assert mixed.active==((1<<0)|(1<<16))
    report['mixed_frame_limitation']={'accepted_repeated_logical_mask':[0,16],'reason':'Row 0 may contain a press in its sampling interval and row 1 a different press later. Three repeated frames alone cannot prove physical simultaneity; this reference does not claim that guarantee.'}
    report['seconds']=round(time.monotonic()-started,3)
    (OUT/'policy-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'counts':report['counts'],'stateful_sequences':report['stateful_sequences'],'failures':report['failures'],'seconds':report['seconds'],'cpu_firmware_implemented':False}));return 0


if __name__=='__main__':raise SystemExit(main())
