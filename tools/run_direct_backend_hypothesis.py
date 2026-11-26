"""Simulation-only local reset pair and single-stage controller clock path."""
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import tempfile
from run_request_skew_probe import once
from run_phase_drain_probe import MODELS
from run_rtl import run
import run_local_sync_hypothesis as previous

ROOT=Path(__file__).resolve().parents[1]
source=inspect.getsource(previous.main)
source=source.replace('local_sync_hypothesis.sv','direct_backend_video_hypothesis.sv')
source=source.replace('local-sync-hypothesis.json','direct-backend-hypothesis.json')
source=source.replace("'sim/net25/package_models_cold_diagnostic.sv' if n=='sim/net24/package_models_pulse_diagnostic.sv' else n",'n')
source=once(source,"    names+=['sim/net25/tb_drain_startup.sv']",'''    bench=(ROOT/'sim/net25/tb_drain_startup.sv').read_text()
    bench=once(bench,'.clk(access_clock)', '.clk(backend)')
    start=bench.index(' always @(control.genblk1.U4_check_second.reset_clock_events)')
    end=bench.index(' initial begin #16000000;',start)
    bench=bench[:start]+bench[end:]
    (ROOT/'sim/net25/tb_direct_backend_hypothesis.sv').write_text('// STRICT original downstream clock monitor; simulation-only bypass of two buffers.\\n'+bench)
    names+=['sim/net25/tb_direct_backend_hypothesis.sv']''')
source=once(source,'    text=once(text,old,new)', '''    new=new.replace('wire local_stage0,local_unused0,local_unused1;',
       'wire local_stage0,local_unused0,local_unused1,local_clock;\\nassign #(TIMED?8.5:0) local_clock=n_P1;')
    new=new.replace('HYP_LOCAL0(n_P1,','HYP_LOCAL0(local_clock,').replace('HYP_LOCAL1(n_P1,','HYP_LOCAL1(local_clock,')
    text=once(text,old,new)''')
source=source.replace('SIMULATION-ONLY extra phase1-clocked AHC74 reset pair. Native circuit not built. All CLR-low OPEN_RESET_CLOCK lines remain unqualified, active clock and recovery guards retained. Not analog/MTBF/PCB approval.',
    'SIMULATION ONLY: extra local AHC74 pair on bufferedP1; controller clock directly from backend, only its leaf buffers remain. Strict original clock/reset guards, NO CLR-low exemption. Native variant not built; no global PVT/MTBF/POR/analog qualification.')
source=source.replace("'strict_cold_clock_pulses_qualified':False", "'global_cold_clock_qualified':False,'strict_selected_cases':True")
source=source.replace("'tools/run_local_sync_hypothesis.py'", "'tools/run_local_sync_hypothesis.py','tools/run_direct_backend_hypothesis.py','sim/net25/tb_drain_startup.sv'")
exec(source,globals())

if __name__=='__main__':raise SystemExit(main())
