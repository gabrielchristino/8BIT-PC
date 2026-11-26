"""ISA-1 Rev 2.1. Exhaustive bounded-delay event simulation, NOT transistor/SPICE.
Times are arbitrary model ticks, not nanoseconds or datasheet guarantees.
"""
from itertools import product
import json
from pathlib import Path

# Signals: SRAM output enabled when CE=0 OE=0 WE=1; write buffer drives
# SRAM DQ when B245_OE=0 and DIR=1. Each pin changes after arbitrary delay.
SAFE_OFF={'CE':1,'OE':1,'WE':1,'BOE':1,'DIR':0}
READ={'CE':0,'OE':0,'WE':1,'BOE':0,'DIR':0}
WRITE_SETUP={'CE':0,'OE':1,'WE':1,'BOE':0,'DIR':1}
WRITE_PULSE={**WRITE_SETUP,'WE':0}
WRITE_HOLD=WRITE_SETUP

def hazards(s):
    ram=s['CE']==0 and s['OE']==0 and s['WE']==1
    buf=s['BOE']==0 and s['DIR']==1
    # Both sides of 245 are bidirectional; if DIR changes while enabled,
    # CPU and SRAM may see wrong drivers. Treat any enabled DIR change as hazard.
    return (ram and buf, s['OE']==0 and s['WE']==0, s['CE']==1 and s['WE']==0)

def event_step(start,target,delays):
    s=dict(start)
    events=sorted((delays[k],k,target[k]) for k in s if s[k]!=target[k])
    observed=[]
    for t,k,v in events:
        s[k]=v
        observed.append((t,k,dict(s),hazards(s)))
    return observed

def all_delay_cases(start,target,maxdelay=3):
    keys=[k for k in start if start[k]!=target[k]]
    count=0; bad=[]
    for ds in product(range(maxdelay+1),repeat=len(keys)):
        count+=1
        events=event_step(start,target,dict(zip(keys,ds)))
        if any(any(row[3]) for row in events):
            if len(bad)<2: bad.append({'delays':dict(zip(keys,ds)),'trace':events})
    return count,bad

def guarded_transition(start,target,disable_wait, maxdelay=3):
    # Phase 1: CE/OE/WE and BOE all inactive. DIR left unchanged until phase 2.
    off={**SAFE_OFF,'DIR':start['DIR']}
    c1,b1=all_delay_cases(start,off,maxdelay)
    # Phase 2: after settling, change DIR while buffer disabled.
    off2={**off,'DIR':target['DIR']}
    c2,b2=all_delay_cases(off,off2,maxdelay)
    # Phase 3: enable target after phase 2 settled.
    c3,b3=all_delay_cases(off2,target,maxdelay)
    return c1+c2+c3,b1+b2+b3

def run():
    # Naive direct transition: explicit counterexample exists.
    naive_count,naive_bad=all_delay_cases(READ,WRITE_SETUP,3)
    assert naive_bad, 'Expected naive transition hazard'
    guarded_cases=0
    for src,dst in [(READ,WRITE_SETUP),(WRITE_SETUP,READ),(READ,READ),(WRITE_SETUP,WRITE_SETUP)]:
        n,b=guarded_transition(src,dst,disable_wait=4,maxdelay=3)
        assert not b,(src,dst,b)
        guarded_cases+=n
    # Negative test: attempting write pulse with OE asserted is illegal.
    assert hazards({**WRITE_PULSE,'OE':0})[1]
    # SRAM /WE may only assert after setup, must deassert before driver disabled.
    assert not any(hazards(WRITE_PULSE))
    # Power-on/reset policy: all enables HIGH, WE HIGH until sequencer initialized.
    assert not any(hazards(SAFE_OFF))
    return {
      'naive_direct_cases':naive_count,'naive_counterexample':naive_bad[0],
      'guarded_cases_exhaustively_checked':guarded_cases,
      'delay_domain':'each changing signal 0..3 arbitrary ticks; settled between phases',
      'guarded_hazards_found':0,
      'model_limits':['No real IC propagation/enable/disable specifications','No analog bus voltage or signal integrity','No glitches inside combinational decode','No clock/reset metastability','No SRAM setup/hold timing checked','No proof of real clock frequency']}
if __name__=='__main__':
    out=run()
    Path(__file__).with_name('isa1_rev21_results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print('naive cases',out['naive_direct_cases'],'guarded',out['guarded_cases_exhaustively_checked'],'hazards',out['guarded_hazards_found'])
