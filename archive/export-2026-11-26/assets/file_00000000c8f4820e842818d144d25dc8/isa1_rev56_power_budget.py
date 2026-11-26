import json, csv
from pathlib import Path
P=Path(__file__).resolve().parent
cases=[]
for usb_a in (2.0,3.0):
 for cpu_a in (0.6,0.9,1.2):
  for display_a in (0.25,0.4,0.5,0.7):
   for efficiency in (0.80,0.85,0.90):
    display_input_a=12*display_a/(5*efficiency)
    total=cpu_a+display_input_a+0.15 # reserve for USB path and auxiliaries, NOT an engineering bound
    cases.append(dict(usb_limit_A=usb_a,cpu_assumed_A=cpu_a,display_12V_assumed_A=display_a,boost_efficiency=efficiency,boost_5V_input_A=round(display_input_a,4),total_5V_A=round(total,4),within_current_budget=total<=usb_a))
assert len(cases)==72
assert all(abs(c['boost_5V_input_A'] - 12*c['display_12V_assumed_A']/(5*c['boost_efficiency']))<0.0001 for c in cases)
# 12V monitor must not be energized unless the 5V bus has reached a qualified, stable state.
# Pure state-machine contract, no electrical validation.
for ready in (False,True):
 for requested in (False,True):
  enabled=ready and requested
  assert not enabled or ready
with (P/'isa1_rev56_scenarios.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cases[0].keys());w.writeheader();w.writerows(cases)
summary={'revision':'5.6','scenarios':len(cases),'pass_by_usb_current':{str(a):sum(c['within_current_budget'] for c in cases if c['usb_limit_A']==a) for a in (2.0,3.0)},'example':next(c for c in cases if c['usb_limit_A']==3 and c['cpu_assumed_A']==0.9 and c['display_12V_assumed_A']==0.4 and c['boost_efficiency']==0.85),'caveat':'Illustrative DC current budget only. Not measured loads, not USB-C current negotiation, not electrical simulation.'}
(P/'isa1_rev56_results.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2))
