"""Evaluate CVC's separate interpreter after its compiled smoke crashed."""
import hashlib
import inspect
import json
from pathlib import Path
import re
import tempfile
from run_rtl import run
from run_request_skew_probe import once
import calibrate_compiled_simulator as template

ROOT=Path(__file__).resolve().parents[1]
EXE=template.EXE
OUT=template.OUT
source=inspect.getsource(template.main).replace('cvc-calibration.json','cvc-interpreter-calibration.json')
source=source.replace('tools/calibrate_compiled_simulator.py',"tools/calibrate_compiled_simulator.py','tools/calibrate_interpreted_cvc.py")
source=once(source,"cvc_cmd=[str(EXE),'-sv','-o',str(work/'compiled'),str(bench)]", "cvc_cmd=[str(EXE),'-sv','+interp',str(bench)]")
source=once(source,"            if row['compile_cvc']['exit']==0 and (work/'compiled').is_file():row['execution_cvc']=run([str(work/'compiled')],work,timeout=30)",
    "            row['execution_cvc']=row['compile_cvc'] # +interp parses and executes in the same process")
source=source.replace('Default four-state CVC, no2state/no ignored timing flags.', 'CVC+interp evaluates parsing/execution in one process (both stored under compile_cvc/execution_cvc). No2state/no ignored timing flags. Compiled CVC smoke remains rejected separately.')
source=once(source,"cvc.get('exit') not in (None,0)", "('$fatal[' in cvc.get('stdout','') and 'RESULT ' not in cvc.get('stdout',''))")
source=source.replace('Tool calibration only.', 'Tool calibration only. CVC fatal can return exit0; negative recognition requires explicit fatal/guard text and absent RESULT, positive recognition requires exact RESULT equivalence.')
exec(source,globals())

if __name__=='__main__':raise SystemExit(main())
