"""NET-03: bus controller pin graph, ROM CPU regressions and fault injection."""
import copy
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from run_rtl import ROOT,BASE,fixtures,program_fixture,run
from make_stack_cpu import transform_bench
from build_transaction_bank import convert,definitions

OUT=ROOT/"verification/net03"


def main():
    OUT.mkdir(parents=True,exist_ok=True);quick="--quick" in sys.argv
    models=[ROOT/n for n in ("sim/hdl/hc_models.sv","sim/hdl/counter_load_candidate.sv","sim/net02/package_models.sv",
      "hardware/stack_bank/stack_bank_netlist.sv","sim/net03/package_models.sv","hardware/transaction_bank/transaction_bank_netlist.sv",
      "sim/net03/isa1_cpu_bus.sv","sim/rtl/isa1_memory.sv")]
    benches=["tb_rtl_cpu","tb_rtl_safety","tb_stack_guards","tb_rtl_program"]
    sources=[*models,Path(__file__),ROOT/"tools/run_rtl.py",ROOT/"tools/make_stack_cpu.py",ROOT/"tools/build_stack_bank.py",
      ROOT/"tools/build_transaction_bank.py",ROOT/"tools/make_transaction_cpu.py",ROOT/"sim/net03/tb_transaction_bank.sv",ROOT/"sim/net03/tb_timing_negative.sv",
      ROOT/"hardware/transaction_bank/transaction_bank.kicad_sch",OUT/"transaction_bank.xml",ROOT/"firmware/rtl01_diagnostic.asm"]
    sources += [ROOT/"sim/tests"/(n+".sv") for n in benches]
    sources += [BASE/f"control_lane{i}.bin" for i in range(4)]
    sources += [BASE/n for n in ("cpu.py","system.py","control.py","microcode.py","sequencer.py","assembler.py")]
    report={"iteration":"NET-03","date":"2026-11-25","quick":quick,"platform":platform.platform(),"python":platform.python_version(),
      "iverilog":subprocess.run(["iverilog","-V"],capture_output=True,text=True).stdout.splitlines()[0],
      "scope":"Pin-connected bus transaction FSM and payload/MDR storage integrated with NET-02 SP. Not complete-board timing or electrical validation.",
      "sources":[{"path":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],"runs":[],"negative_checks":[]}
    def save():(OUT/"results.json").write_text(json.dumps(report,indent=2)+"\n")
    with tempfile.TemporaryDirectory(prefix="isa1-net03-") as temporary:
        work=Path(temporary)
        lanes=[(BASE/f"control_lane{i}.bin").read_bytes() for i in range(4)]
        (work/"control.hex").write_text("".join(f"{sum(lanes[l][a]<<(8*l) for l in range(4)):08x}\n" for a in range(8192)))
        rows,coverage=fixtures(quick);report["opcode_cases"]=coverage
        vectors="".join("".join(f"{v:08x}\n" for v in row) for row in rows)
        (work/"vectors.hex").write_text(vectors);report["vector_sha256"]=hashlib.sha256(vectors.encode()).hexdigest()
        report["program"],frame,png=program_fixture(work)
        for bench in benches:
            text=transform_bench((ROOT/"sim/tests"/(bench+".sv")).read_text())
            if bench=="tb_stack_guards":
                assert text.count("if(req!==allowed")==1
                text=text.replace("if(req!==allowed","if(dut.bus_start!==allowed")
            (work/(bench+".sv")).write_text(text)
        shutil.copyfile(ROOT/"sim/net03/tb_transaction_bank.sv",work/"tb_transaction_bank.sv")
        configurations=[("tb_transaction_bank",0),("tb_transaction_bank",1),("tb_rtl_cpu",0),("tb_rtl_cpu",1),
                        ("tb_rtl_safety",0),("tb_rtl_safety",1),("tb_stack_guards",0)]
        if not quick:configurations += [("tb_rtl_program",0),("tb_rtl_program",1)]
        for bench,variant in configurations:
            command=["iverilog","-g2012","-Wall","-s",bench]
            configuration={}
            if bench=="tb_transaction_bank":
                configuration={"timed":variant,"transactions":256 if quick else 65536}
                command += [f"-P{bench}.TIMED={variant}",f"-P{bench}.CASES={configuration['transactions']}"]
            if bench in ("tb_rtl_cpu","tb_rtl_safety","tb_rtl_program"):
                configuration["hc191"]=variant;command += [f"-P{bench}.USE_HC191={variant}"]
            if bench=="tb_rtl_cpu":command += [f"-P{bench}.CASES={len(rows)}"]
            if bench=="tb_rtl_program":
                command += [f"-P{bench}.RETIREMENTS={report['program']['retirements']}",f"-P{bench}.BUS_COUNT={report['program']['transactions']}"]
                if variant:command += [f"-P{bench}.CPU_HALF=7",f"-P{bench}.VIDEO_HALF=5"]
            command += ["-o",str(work/"bench.vvp"),*map(str,models),str(work/(bench+".sv"))]
            row={"bench":bench,"configuration":configuration,"compile":run(command,work)}
            if row["compile"]["exit"]==0:
                row["execution"]=run(["vvp",str(work/"bench.vvp")],work,timeout=600)
                if bench=="tb_rtl_program" and row["execution"]["exit"]==0:
                    row["frame_matches_reference"]=(work/"frame.ppm").read_bytes()==frame
                    if not row["frame_matches_reference"]:row["execution"]["exit"]=1
                    else:shutil.copyfile(work/"frame.ppm",OUT/"frame.ppm");(OUT/"frame.png").write_bytes(png)
            report["runs"].append(row);save();print(json.dumps(row),flush=True)
            if row["compile"]["exit"] or row.get("execution",{}).get("exit")!=0:return 1
        tree=ET.parse(OUT/"transaction_bank.xml")
        ground=next(n for n in tree.getroot().findall("./nets/net") if n.get("name").removeprefix("/")=="GND")
        for net in tree.getroot().findall("./nets/net"):
            for node in list(net.findall("node")):
                if node.get("ref")=="U3" and node.get("pin")=="1":net.remove(node);ground.append(copy.deepcopy(node))
        tree.write(work/"bad-enable.xml");convert(work/"bad-enable.xml",definitions(),work/"bad-bank.sv")
        negative_models=[p for p in models if p.name!="transaction_bank_netlist.sv"]+[work/"bad-bank.sv"]
        compiled=run(["iverilog","-g2012","-Wall","-s","tb_transaction_bank","-Ptb_transaction_bank.CASES=8","-o",str(work/"bad.vvp"),
          *map(str,negative_models),str(work/"tb_transaction_bank.sv")],work)
        executed=run(["vvp",str(work/"bad.vvp")],work) if compiled["exit"]==0 else None
        report["negative_checks"].append({"case":"Address capture enable stuck active","expected_rejection":True,
          "passed":executed is not None and executed["exit"]!=0 and "retained payload mismatch" in executed["stdout"],"compile":compiled,"execution":executed})
        tree=ET.parse(OUT/"transaction_bank.xml")
        for net in tree.getroot().findall("./nets/net"):
            for node in list(net.findall("node")):
                if node.get("ref")=="U2" and node.get("pin")=="2":net.remove(node)
        tree.write(work/"floating.xml")
        try:convert(work/"floating.xml",definitions(),work/"floating.sv")
        except ValueError as error:message=str(error)
        else:message="No rejection"
        report["negative_checks"].append({"case":"Floating first ACK synchronizer D input","expected_rejection":True,
          "passed":"Floating input U2/2" in message,"message":message})
        for case,expected in enumerate(["DFF data setup","HC377 data hold","HC377 enable setup","HC377 enable hold"]):
            compiled=run(["iverilog","-g2012","-Wall","-s","tb_timing_negative",f"-Ptb_timing_negative.CASE={case}","-o",str(work/"negative.vvp"),
              str(ROOT/"sim/net03/package_models.sv"),str(ROOT/"sim/net03/tb_timing_negative.sv")],work)
            executed=run(["vvp",str(work/"negative.vvp")],work) if compiled["exit"]==0 else None
            report["negative_checks"].append({"case":expected,"expected_rejection":True,"passed":executed is not None and executed["exit"]!=0 and expected+" violation" in executed["stdout"],
               "compile":compiled,"execution":executed})
        save();print(json.dumps({"negative_checks":report["negative_checks"]}),flush=True)
        return int(not all(r["passed"] for r in report["negative_checks"]))


if __name__=="__main__":raise SystemExit(main())
