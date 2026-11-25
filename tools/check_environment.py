"""Record the actual Linux simulation toolchain without modifying it."""
import json
from pathlib import Path
import platform
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
commands = {"iverilog": ["iverilog", "-V"], "vvp": ["vvp", "-V"],
            "ngspice": ["ngspice", "--version"], "kicad-cli": ["kicad-cli", "version"]}
report = {"date": "2026-11-24", "platform": platform.platform(),
          "python": platform.python_version(), "tools": {},
          "policy": "Simulation and construction in Ubuntu WSL; source files remain on the project directory"}
for name, command in commands.items():
    executable = shutil.which(name)
    if executable:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        report["tools"][name] = {"path": executable, "exit_code": result.returncode,
                                 "stdout": result.stdout, "stderr": result.stderr}
    else:
        report["tools"][name] = {"path": None}
target = ROOT / "verification/environment.json"
target.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"available": {k:bool(v["path"]) for k,v in report["tools"].items()},
                  "python": report["python"], "platform": report["platform"]}))
