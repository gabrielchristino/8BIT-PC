"""Preserve a primary research alternative without promoting it to the BOM."""
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT/'references/net23/sn74lvc2g125.pdf'
    path.parent.mkdir(parents=True,exist_ok=True)
    url='https://www.ti.com/lit/ds/symlink/sn74lvc2g125.pdf'
    if not path.exists():
        with urlopen(Request(url,headers={'User-Agent':'ISA1-source-audit'}),timeout=45) as response:
            data=response.read()
        if not data.startswith(b'%PDF-'):raise ValueError('Not PDF')
        path.write_bytes(data)
    extraction=ROOT/'verification/net23/research/sn74lvc2g125.txt'
    extraction.parent.mkdir(parents=True,exist_ok=True)
    command=['pdftotext','-layout',str(path),str(extraction)]
    result=subprocess.run(command,capture_output=True,text=True,check=True)
    report={'date':'2026-11-26','url':url,'path':path.relative_to(ROOT).as_posix(),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'extraction':extraction.relative_to(ROOT).as_posix(),'extraction_sha256':hashlib.sha256(extraction.read_bytes()).hexdigest(),
            'transformation':'Original PDF unchanged; separate pdftotext -layout',
            'command':command,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'selected_for_bom':False,
            'source':{'path':'tools/collect_source_clock_reference.py','sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    (extraction.parent/'source.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
