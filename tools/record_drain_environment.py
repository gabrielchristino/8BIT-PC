"""Supplementary tools/ROMs and primary AHC04 extraction for NET25."""
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
from build_cpu_global import KICAD
from run_rtl import BASE
import record_reset_environment as previous

ROOT=Path(__file__).resolve().parents[1]
source=inspect.getsource(previous.main).replace('verification/net20','verification/net25')
source=source.replace('8af86e361e6eb510ff32c5f4c45cabc7ae633c85','5a871ff3ddc58986ae1fb7998690bb9ec3711d5b').replace('tools/record_reset_environment.py','tools/record_drain_environment.py')
exec(source,globals())

def research():
    names=['references/ti/sn74ahc04.pdf','verification/net25/ahc04-research.txt','tools/record_drain_environment.py']
    r={'date':'2026-11-26','source_url':'https://www.ti.com/lit/ds/symlink/sn74ahc04.pdf','revision':'SCLS231P June2023 preserved original PDF',
       'command':['pdftotext','-layout',names[0],names[1]],'transformation':'Unchanged original PDF to separate layout extraction',
       'selected_condition':'5V+/-0.5V, -40..85C, CL50pF','rise_and_fall_min_ns':1,'rise_and_fall_max_ns':8.5,
       'scope':'Research only, no new clock distribution implemented. Q/QB single gate bound still needs native pin budget and strict regressions.',
       'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names]}
    (ROOT/'verification/net25/ahc04-reference.json').write_text(json.dumps(r,indent=2)+'\n')

if __name__=='__main__':main();research()
