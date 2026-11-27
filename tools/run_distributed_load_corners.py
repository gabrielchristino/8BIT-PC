"""Separate NET30 CPU write/restart regression at opposite50ppm corners."""
import hashlib
import inspect
import json
from pathlib import Path
import sys
import run_distributed_load_cpu_fault as previous
import run_common_request_cpu_corners as template

ROOT=Path(__file__).resolve().parents[1]
source=inspect.getsource(template.main).replace('verification/net24/frequency-corners','verification/net30/frequency-corners')
source=source.replace('tools/run_common_request_cpu_corners.py','tools/run_distributed_load_corners.py')
source=source.replace('native common-request graph','native NET30 load-distribution candidate').replace('native common-request clock group','native NET30 load-distribution candidate')
exec(source,globals())

if __name__=='__main__':
    if '--worker' in sys.argv:raise SystemExit(main())
    import run_distributed_load_job as bounded
    bounded.JOBS={'corners':['tools/run_distributed_load_corners.py','--worker']}
    sys.argv=[sys.argv[0],'corners'];raise SystemExit(bounded.main())
