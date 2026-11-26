"""Reuse actual joined pin counting for the separate Schmitt reset leaf."""
import hashlib
import inspect
import json
from pathlib import Path
import check_reset_loads as previous

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net21'

source = inspect.getsource(previous.main)
source = source.replace('files = [Path(__file__)]', "files = [Path(__file__), ROOT / 'tools/check_reset_loads.py']")
source = source.replace('system_reset', 'schmitt_reset').replace('TPS3703F6050DSER', 'TPS3808G01DBVR')
source = source.replace("'buffer': 'SN74AHC125'", "'buffer': 'two SN74AHC14 inverters'")
source = source.replace("'supervisor_timing_test_cl_pf': 10", "'supervisor_timing_test_cl_pf': 50")
source = source.replace("'routing_allowance_pf': 0", "'routing_allowance_pf': 40")
source = source.replace("'example_routing_budget_pf': 2, 'example_total_pf': 12", "'example_routing_budget_pf': 10, 'example_total_pf': 20, 'budget_within_test_load': True")
source = source.replace("'CPU_RESET_N', 'CPU_CORE_CLK'", "'RAW_INVERTED', 'RAW_BUFFERED', 'CPU_RESET_N', 'CPU_CORE_CLK'")
source = source.replace('Even one max-Ci AHC125 consumes all 10pF. NET18/20 hold-up cannot be promoted to a guaranteed physical shutdown bound. Digital RAW tests remain independent.',
                        'One Schmitt input max10pF at5V plus10pF trace budget fits supervisor CL50pF. This closes the chosen load budget, not actual extracted PCB capacitance or analog shutdown/POR guarantee. RC resistor load on RAW_BUFFERED also requires qualification.')
exec(source, globals())


if __name__ == '__main__':
    raise SystemExit(main())
