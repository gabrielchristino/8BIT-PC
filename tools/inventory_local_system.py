"""Inventory current candidate leaves, separating CIs from clock modules."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    names=['cpu_global','memory_decode','common_request','memory_bus','local_phase_video','local_phase_keyboard','local_phase_reset']
    totals=Counter();modules=[];sources=[]
    for name in names:
        p=ROOT/'hardware'/name/'design.json';parts=json.loads(p.read_text())['parts']
        counts=Counter(x['part'] for x in parts);totals.update(counts)
        modules.append({'module':name,'counts':dict(counts),'components':len(parts)})
        sources.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    excluded={'R','C','J8','ACH_CPU_CONFIG','ACH_MASTER_CONFIG'}
    ics=sum(n for name,n in totals.items() if name not in excluded)
    assert ics==460 and totals['SN74AHC174']==4 and totals['C']==464
    sources.append({'path':'tools/inventory_local_system.py','sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    report={'date':'2026-11-26','modules':modules,'totals':dict(totals),'candidate_union_ic_count':ics,'oscillator_modules':2,
        'global_board_integrated':False,'sources':sources,
        'power_budget':[{'family':n,'count':c,'board_icc_upper_bound_a':None,'dynamic_current_upper_bound_a':None} for n,c in sorted(totals.items()) if n not in excluded],
        'notes':['+1CI local reset pair compared with NET25. Keyboard HC174 replaced pin-for-pin by AHC174; no package removed.',
            'Count includes memories and supervisor; not all460 are logic. Two ACH modules counted separately. USB-C/converter/isolation/DAC still absent from this candidate union.',
            '1.5A remains a conditional fault-envelope budget, not derived/measured board consumption.'], 'production_released':False}
    (ROOT/'verification/net26/load-inventory.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'candidate_ics':ics,'oscillator_modules':2,'ahc174':totals['SN74AHC174'],'current_budget_closed':False}))

if __name__=='__main__':main()
