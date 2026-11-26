"""Execute real CPU write/restart checks with opposite oscillator ppm corners."""
import hashlib
import json
from pathlib import Path
import run_clocked_cpu_fault as previous

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / 'verification/net23/frequency-corners'
    folder.mkdir(parents=True, exist_ok=True)
    previous.OUT = folder
    original = previous.run
    evidence = []

    def run(command, work, timeout=300):
        command = list(command)
        if command[0] == 'iverilog':
            policy = int(next(x.rsplit('=',1)[1] for x in command if x.startswith('-Ptb_schmitt_cpu_fault.POLICY=')))
            cpu_ppm, master_ppm = (-50,50) if policy==0 else (50,-50)
            ancestor = Path(command[-1])
            text = ancestor.read_text()
            old = 'module tb_schmitt_cpu_fault;'
            assert text.count(old)==1
            text = text.replace(old, old + '\n' +
                f' defparam memory.reset_domains.CPU_PERIOD_NS={10000/(1+cpu_ppm*1e-6):.12f};\n' +
                f' defparam memory.reset_domains.MASTER_PERIOD_NS={39.721946/(1+master_ppm*1e-6):.12f};\n')
            bench = work/'tb_clocked_corner.sv'
            bench.write_text(text)
            command[-1] = str(bench)
            saved = folder/f'compiled-policy{policy}.sv'
            saved.write_bytes(bench.read_bytes())
            evidence.append({'policy':policy,'cpu_initial_temperature_ppm':cpu_ppm,'master_initial_temperature_ppm':master_ppm,
                             'path':saved.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),
                             'ancestor':ancestor.relative_to(ROOT).as_posix(),'ancestor_sha256':hashlib.sha256(ancestor.read_bytes()).hexdigest(),
                             'transformation':'Insert two native oscillator period parameter overrides only; do not force clocks or seed SRAM.'})
        return original(command, work, timeout=timeout)

    previous.run = run
    result = previous.main()
    path = folder/'actual-cpu-write-reset.json'
    data = json.loads(path.read_text())
    data['scope'] = 'Actual CPU write/reset/restart driven by configured native sources at opposite initial/temperature oscillator50ppm corners. Qualified source VDD, RAW/RC and binary boundaries; no jitter, aging/supply/load frequency guarantee or analog/PVT/fabrication signoff.'
    data['compiled_corner_benches'] = evidence
    data['sources'].append({'path':'tools/run_clocked_cpu_corners.py','sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    data['sources'] += [{'path':e['path'],'sha256':e['sha256']} for e in evidence]
    path.write_text(json.dumps(data,indent=2)+'\n')
    return result


if __name__=='__main__':raise SystemExit(main())
