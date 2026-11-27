"""NET26 actual CPU writes/restart at opposite configured source ppm corners."""
import hashlib
import inspect
import json
from pathlib import Path
import run_local_phase_cpu_fault as previous
import run_common_request_cpu_corners as template

ROOT=Path(__file__).resolve().parents[1]
source=inspect.getsource(template.main).replace('verification/net24/frequency-corners','verification/net26/frequency-corners')
source=source.replace('tools/run_common_request_cpu_corners.py','tools/run_local_phase_cpu_corners.py')
source=source.replace('native common-request graph','native local-reset/direct-clock/fast-keyboard graphs')
source=source.replace('native common-request clock group','native local-reset/direct-clock/fast-keyboard variants')
exec(source,globals())

if __name__=='__main__':raise SystemExit(main())
