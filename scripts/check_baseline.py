"""Check the captured Gigatron reference; no modified hardware is validated."""
import hashlib
import json
from pathlib import Path
import platform
import re
import resource
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def run(command,cwd,seconds=10):
    def limit():
        resource.setrlimit(resource.RLIMIT_AS,(128*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_CPU,(5,)*2)
        resource.setrlimit(resource.RLIMIT_FSIZE,(2*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        p=subprocess.run(command,cwd=cwd,stdout=out,stderr=err,timeout=seconds,preexec_fn=limit)
        out.seek(0);err.seek(0)
        return dict(command=list(map(str,command)),exit=p.returncode,stdout=out.read().decode(),stderr=err.read().decode(),
                    limits=dict(memory_mb=128,cpu_seconds=5,wall_seconds=seconds,output_mb_per_file=2))


def main():
    manifest=json.loads((ROOT/'references/gigatron/sources.json').read_text())
    checked=[]
    for row in manifest['files']:
        data=(ROOT/row['path']).read_bytes()
        assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
        checked.append(row['path'])
    with zipfile.ZipFile(ROOT/'references/gigatron/bom-original.xlsx') as bundle:
        assert bundle.testzip() is None and 'xl/workbook.xml' in bundle.namelist()
    assert (ROOT/'references/gigatron/ROMv6.rom').stat().st_size==131072
    source=(ROOT/'references/gigatron/gtemu.c').read_text()
    assert source.count('srand(time(NULL));')==1
    assert source.count('for (long long t=-2; ; t++)')==1
    bounded=source.replace('srand(time(NULL));','srand(1);').replace('for (long long t=-2; ; t++)','int observed_lines=0;\n  for (long long t=-2; t<100000000; t++)')
    start=bounded.index('    if (vgaX++ < 200) {')
    end=bounded.index('    if (hSync > 0) {',start)
    bounded=bounded[:start]+'    vgaX++; // Observer omits character plotting, preserving sync count.\n'+bounded[end:]
    anchor='      vgaX = 0;'
    assert bounded.count(anchor)==1
    bounded=bounded.replace(anchor,'      if (++observed_lines==1024) break;\n'+anchor)
    with tempfile.TemporaryDirectory(prefix='8bit-pc-gigatron-') as tmp:
        work=Path(tmp)
        (work/'reference.c').write_text(bounded)
        comp=run(['gcc','-std=c99','-O2','-Wall','-Wextra','reference.c','-o','reference'],work)
        assert comp['exit']==0,comp
        execution=run([str(work/'reference'),str(ROOT/'references/gigatron/ROMv6.rom')],work)
        assert execution['exit']==0 and not execution['stderr'],execution
        lines=execution.pop('stdout').splitlines()
        completed=[line for line in lines if re.search(r' line +-?\d+\s+xout [0-9a-f]{2} t [0-9.]+$',line)]
        partial=[line for line in lines if line not in completed]
        assert len(completed)==1024, (len(lines),len(completed),lines[:2],lines[-2:])
        assert len(partial)<=1 and (not partial or partial[0]==lines[-1]),partial
        execution.update(output_lines=len(lines),complete_scanline_messages=len(completed),partial_final_line=partial,
                         stdout_sha256=hashlib.sha256(('\n'.join(lines)+'\n').encode()).hexdigest(),last_lines=lines[-3:])
    report=dict(scope='Original Gigatron C emulator, bounded software smoke check. Not TTL/HDL/electrical/PCB or modified architecture qualification.',
        command=sys.argv,python=platform.python_version(),gcc=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0],
        source_files_checked=checked,source_xlsx_crc_ok=True,original_sources_unchanged=True,
        transformation='Temporary C copy: srand(1), maximum100000000cycles, omit character plotting while preserving vgaX increments; stop after1024rising HSYNC messages, including startup.',
        transformed_c_sha256=hashlib.sha256(bounded.encode()).hexdigest(),compile=comp,execution=execution,
        new_hardware_validated=False,production_released=False)
    output=ROOT/'verification/baseline.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(source_files=len(checked),output_lines=len(lines),compile_exit=comp['exit'],execution_exit=execution['exit'],new_hardware_validated=False)))


if __name__=='__main__':main()
