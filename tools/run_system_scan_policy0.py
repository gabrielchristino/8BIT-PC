"""Additional binary reset-boundary scenario, with unchanged native pin graph."""
import hashlib
import json
from pathlib import Path
import run_system_scan as original

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net19a/policy0'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    original.OUT=OUT
    native_run=original.run
    evidence={}

    def run(command,work,timeout=240):
        command=list(command)
        if command[0]=='iverilog':
            source=Path(command[-1]);text=source.read_text()
            assert source.name=='tb_keyboard_scan.sv' and text.count('endmodule')==1
            text=text.replace('endmodule',' defparam memory.raster.RESOLVE_LATE=0;\n defparam memory.peripheral.RESOLVE_LATE=0;\nendmodule')
            path=work/'tb_scan_policy0.sv';path.write_text(text)
            saved=OUT/'compiled-bench.sv';saved.write_text(text)
            command[-1]=str(path)
            evidence.update(path=saved.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(text.encode()).hexdigest(),
                            transformation='Set only the two existing reset-boundary RESOLVE_LATE parameters to 0. No native pins or downstream checks changed.')
        return native_run(command,work,timeout)

    original.run=run
    result=original.main()
    reports=list(OUT.glob('system-scan-*.json'))
    if len(reports)!=1:raise ValueError('Ambiguous policy scenario report')
    data=json.loads(reports[0].read_text());data['binary_reset_resolution_late']=0
    data['compiled_bench']=evidence
    data['sources'].append({'path':'tools/run_system_scan_policy0.py','sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    reports[0].write_text(json.dumps(data,indent=2)+'\n')
    return result


if __name__=='__main__':raise SystemExit(main())
