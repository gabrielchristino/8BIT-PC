"""Inventory current candidate leaves without inventing an ICC/CPD budget."""
import hashlib
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/net18'
MODULES=['cpu_global','memory_decode','keyboard_access','memory_bus','video_system','keyboard_500','reset_domains']
def main():
    modules=[];totals=Counter();sources=[]
    for name in MODULES:
        p=ROOT/'hardware'/name/'design.json';parts=json.loads(p.read_text())['parts'];counts=Counter(x['part'] for x in parts);totals.update(counts)
        modules.append({'module':name,'components':len(parts),'counts':dict(counts),'status':'Candidate leaf, not an approved assembled global BOM'})
        sources.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    passive={'C','R','J8'};ics=sum(n for k,n in totals.items() if k not in passive)
    assert ics==455 and totals['C']==456
    report={'date':'2026-11-26','modules':modules,'totals':dict(totals),'integrated_candidate_ic_count':ics,'global_board_integrated':False,'sources':sources,
      'power_budget':[{'family':k,'count':n,'icc_guaranteed_max_a':None,'dynamic_cpd_guaranteed_max_f':None,'external_output_load_bound_a':None,'status':'OPEN: populate guaranteed bounds/conditions; do not substitute typical CPD or zero'} for k,n in sorted(totals.items()) if k not in passive],
      'notes':['455 is a candidate union count, not measured consumption or a completed global netlist','HCT/AHCT TTL input levels can add delta-ICC; guaranteed logic compatibility alone does not close supply current','Memory active/standby currents and output charging loads must be counted by operating mode','1.5A in the hold-up study is a proposed fault-envelope limit, not a derived or measured board current'],
      'production_released':False}
    (OUT/'load-inventory.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'candidate_ics':ics,'capacitors':totals['C'],'families_with_open_current_bounds':len(report['power_budget']),'production_released':False}))
if __name__=='__main__':main()
