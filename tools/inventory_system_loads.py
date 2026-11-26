"""Candidate leaf inventory after the controller package substitution."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net19a'
MODULES=['cpu_global','memory_decode','system_access','memory_bus','video_system','keyboard_500','power_reset']


def main():
    sources=[];modules=[];totals=Counter()
    for name in MODULES:
        path=ROOT/'hardware'/name/'design.json';parts=json.loads(path.read_text())['parts'];counts=Counter(p['part'] for p in parts);totals.update(counts)
        modules.append({'module':name,'components':len(parts),'counts':dict(counts)})
        sources.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    passive={'R','C','J8'};ics=sum(n for k,n in totals.items() if k not in passive)
    assert ics==456 and totals['SN74AHC174']==3 and totals['C']==458
    for name in ['tools/inventory_system_loads.py','references/ti/sn74ahc174.pdf']:
        sources.append({'path':name,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()})
    report={'date':'2026-11-26','modules':modules,'totals':dict(totals),'candidate_union_ic_count':ics,'global_board_integrated':False,
            'sources':sources,'power_budget':[{'family':k,'count':n,'board_icc_upper_bound_a':None,'dynamic_current_upper_bound_a':None,'status':'OPEN: operating modes, rail/TTL levels, activity and external loads not closed'} for k,n in sorted(totals.items()) if k not in passive],
            'ahc174_datasheet_static_icc':{'maximum_a_per_package':40e-6,'conditions':'VCC=5.5V, VI=VCC or GND, IO=0; does not include switching/output charging or establish actual board input conditions'},
            'notes':['Same 456 candidate packages as NET18 union, three HC174 replaced by AHC174, 30 families. Not an assembled approved BOM.','1.5A remains the proposed power fault-envelope bound, not measured/derived current. USB/converter/DAC/oscillator packages are not in this union.'],
            'production_released':False}
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'load-inventory.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'candidate_ics':ics,'families_with_open_board_current_bounds':len(report['power_budget']),'production_released':False}))


if __name__=='__main__':main()
