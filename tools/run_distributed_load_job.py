"""Run one isolated candidate regression with persistent logs and own limits."""
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
from tracked_simulation import active,run_tracked

ROOT=Path(__file__).resolve().parents[1]
JOBS={
 'ideal':['tools/run_distributed_load_vectors.py'],
 'timed':['tools/run_distributed_load_vectors.py','--timed','--quick'],
 'early':['tools/run_distributed_load_vectors.py','--timed','--quick','--early'],
 'memory':['tools/run_distributed_load_memory.py'],
 'cpu-fault':['tools/run_distributed_load_cpu_fault.py'],
 'program':['tools/run_distributed_load_program.py']}

def main():
    assert len(sys.argv)==2 and sys.argv[1] in JOBS
    name=sys.argv[1];folder=ROOT/'verification/net30/jobs'/name;folder.mkdir(parents=True,exist_ok=True)
    state=folder/'run-state.json'
    if state.exists():
        status=json.loads(state.read_text())
        if active(status):print(json.dumps({'already_running':name,'pid':status['pid']}));return 0
        raise RuntimeError('Preserve finished attempt before retry: '+str(folder))
    importlib.import_module(Path(JOBS[name][0]).stem)
    paths=set(ROOT.glob('hardware/**/*.sv'))|set(ROOT.glob('sim/**/*.sv'))|set(ROOT.glob('firmware/**/*.asm'))
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path:
            path=Path(path).resolve()
            if path.is_relative_to(ROOT/'tools') and path.suffix=='.py':paths.add(path)
    from run_rtl import BASE
    paths.update(BASE/f'control_lane{i}.bin' for i in range(4))
    origin={'date':'2026-11-26','job':name,'candidate_base':'b5a19c7ee72a9b8543060e77f9c26824daf271ca',
        'head_at_start':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'scope':'Separate NET30 candidate, source files frozen before child launch. Process exit is not itself electrical/production acceptance.',
        'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)],
        'sources_include_conservative_superset':True,'production_released':False}
    (folder/'origin.json').write_text(json.dumps(origin,indent=2)+'\n')
    result=run_tracked([sys.executable,*JOBS[name]],ROOT,folder,'job',3600,1024,3000,8)
    (folder/'process-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'job':name,'exit':result['exit'],'seconds':result['seconds'],'production_released':False}),flush=True)
    return int(result['exit']!=0)

if __name__=='__main__':raise SystemExit(main())
