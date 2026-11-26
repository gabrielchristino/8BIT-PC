"""Supplementary tool versions and immutable ROMs for NET23."""
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
from build_cpu_global import KICAD
from run_rtl import BASE
import record_reset_environment as previous

ROOT=Path(__file__).resolve().parents[1]
source=inspect.getsource(previous.main).replace('verification/net20','verification/net23')
source=source.replace('8af86e361e6eb510ff32c5f4c45cabc7ae633c85','cbb38703c34cf119612f39ecb0255940e670f974')
source=source.replace('tools/record_reset_environment.py','tools/record_clocked_environment.py')
exec(source,globals())

if __name__=='__main__':main()
