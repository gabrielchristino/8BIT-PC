"""Bounded ACK phase tests, independent of the longer CPU regressions."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import ROOT,run


def main():
    sources=[ROOT/n for n in ("sim/hdl/hc_models.sv","sim/net03/package_models.sv",
       "hardware/transaction_bank/transaction_bank_netlist.sv","sim/net03/tb_ack_phase.sv")]
    report={"date":"2026-11-25","scope":"Digital ACK offsets around clock edges; no metastability or MTBF proof",
       "sources":[{"path":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in [*sources,Path(__file__)]],"runs":[]}
    with tempfile.TemporaryDirectory(prefix="isa1-ack-phase-") as temporary:
        work=Path(temporary)
        for timed in (0,1):
            compiled=run(["iverilog","-g2012","-Wall","-s","tb_ack_phase",f"-Ptb_ack_phase.TIMED={timed}","-o",str(work/"phase.vvp"),*map(str,sources)],work)
            executed=run(["vvp",str(work/"phase.vvp")],work) if compiled["exit"]==0 else None
            report["runs"].append({"timed":timed,"compile":compiled,"execution":executed})
    (ROOT/"verification/net03/ack-phase.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report),flush=True)
    return int(any(r['compile']['exit'] or r['execution'] is None or r['execution']['exit'] for r in report['runs']))


if __name__=="__main__":raise SystemExit(main())
