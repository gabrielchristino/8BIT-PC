"""Compatibility trials of unmodified official PSpice library in ngspice.

Solver assistance changes the numerical problem: completion is not PVT signoff.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net18/vendor-trial'
LIB = ROOT / 'references/vendor/tps63070/original/SLVMBP8/TPS63070_PSPICE_TRANS/TPS63070_TRANS.LIB'


def main():
    before = hashlib.sha256(LIB.read_bytes()).hexdigest()
    base = (OUT / 'gear-startup.cir').read_text().replace('54.2k', '55.4k')
    variants = [
        ('relaxed-gear', '.options method=gear reltol=.01 abstol=1n vntol=10u trtol=10'),
        ('shunted-gear', '.options method=gear reltol=.003 abstol=1n vntol=1u rshunt=1e12 cshunt=1e-15'),
        ('relaxed-trap', '.options method=trap reltol=.01 abstol=1n vntol=10u trtol=10'),
    ]

    def one(pair):
        name, options = pair
        deck = OUT / (name + '.cir')
        log = OUT / (name + '.log')
        deck.write_text(base.replace('.options method=gear', options))
        with tempfile.TemporaryDirectory(prefix='isa1-vendor-') as tmp:
            Path(tmp, '.spiceinit').write_text('set ngbehavior=ps\n')
            cmd = ['ngspice', '-b', '-o', str(log), str(deck)]
            try:
                proc = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, timeout=60)
                code, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
            except subprocess.TimeoutExpired:
                code, stdout, stderr = None, '', 'Timeout 60s: incomplete, never approved'
        output = log.read_text(errors='replace')
        match = re.search(r'^final_v\s*=\s*([-+\d.eE]+)', output, re.M)
        value = float(match.group(1)) if match else None
        row = {'name': name, 'command': cmd, 'spiceinit': 'set ngbehavior=ps',
               'options': options, 'exit': code, 'stdout': stdout, 'stderr': stderr,
               'deck': deck.relative_to(ROOT).as_posix(), 'log': log.relative_to(ROOT).as_posix(),
               'final_v': value, 'completed': code == 0 and value is not None,
               'nominal_target_v': .8 * (1 + 55400 / 10000),
               'vendor_library_sha256': before, 'production_released': False}
        (OUT / (name + '.json')).write_text(json.dumps(row, indent=2) + '\n')
        return row

    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(one, variants))
    if hashlib.sha256(LIB.read_bytes()).hexdigest() != before:
        raise RuntimeError('Original library changed')
    report = {'date': '2026-11-26', 'library_unchanged': True, 'runs': rows,
              'status': 'Compatibility research; numerical changes and missing temperature/IQ models prevent physical qualification',
              'production_released': False}
    (OUT / 'solver-trials.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('name', 'exit', 'completed', 'final_v')} for r in rows]))
    return 0  # research collector; individual completion is checked explicitly


if __name__ == '__main__':
    raise SystemExit(main())
