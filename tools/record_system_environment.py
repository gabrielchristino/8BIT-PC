"""Supplement the run records with versions and unchanged original ROM inputs."""
import hashlib
import json
from pathlib import Path
import subprocess
from build_cpu_global import KICAD

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net19a'
BASE='9a21166ebdcd8d0dd118345e27b735ee75296984'


def main():
    versions=[]
    for cmd in [['python3','--version'],['iverilog','-V'],['vvp','-V'],[KICAD,'version'],['pdftotext','-v']]:
        p=subprocess.run(cmd,capture_output=True,text=True)
        versions.append({'command':cmd,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    roms=[]
    for lane in range(4):
        name=f'revisions/rev983/control_lane{lane}.bin';path=ROOT/name
        before=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
        data=path.read_bytes();assert data==before,'Original ROM differs from preserved base'
        roms.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'baseline_git_commit':BASE,'unchanged_from_baseline':True})
    report={'date':'2026-11-26','collected_after_runs':True,
            'note':'Supplementary environment and shared ROM inventory. CPU/vector/batch records also captured compiler version before execution. Batch/scan collectors do not list ROM hashes individually; these original files are unchanged from preserved baseline. This is metadata collection, not a new test execution.',
            'versions':versions,'shared_rom_inputs':roms,
            'sources':[{'path':'tools/record_system_environment.py','sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}]}
    (OUT/'environment.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'tool_versions_recorded':len(versions),'unchanged_shared_roms':len(roms)}))


if __name__=='__main__':main()
