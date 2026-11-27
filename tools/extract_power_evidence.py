"""Extract existing primary datasheets, without turning typical CPD into a bound."""
import hashlib
import json
from pathlib import Path
import resource
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net28/power-evidence'

def main():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(60,)*2)
    resource.setrlimit(resource.RLIMIT_FSIZE,(4*1024**2,)*2)
    inventory=ROOT/'verification/net26/load-inventory.json'
    totals=json.loads(inventory.read_text())['totals']
    special={'AT28HC64B':'references/microchip/at28hc64b.pdf',
        'AT28C256_28PDIP':'references/microchip/at28c256-industrial.pdf',
        'AS7C256A_28SOJ':'references/alliance/as7c256a.pdf',
        'TPS3808G01DBVR':'references/net20/tps3808.pdf',
        'ACH_CPU_CONFIG':'references/net22/abracon-ach.pdf',
        'ACH_MASTER_CONFIG':'references/net22/abracon-ach.pdf',
        'SN74AHC164':'references/net22/sn74ahc164.pdf',
        'SN74LVC1G27':'references/net22/sn74lvc1g27.pdf'}
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[]
    for family,count in totals.items():
        if family in {'R','C','J8'}:continue
        source=ROOT/special.get(family,'references/ti/'+family.lower()+'.pdf')
        assert source.is_file(),family
        target=OUT/(family.lower()+'.txt')
        command=['pdftotext','-layout',str(source),str(target)]
        result=subprocess.run(command,capture_output=True,text=True,timeout=20)
        assert result.returncode==0 and target.is_file(),family
        rows.append({'family':family,'count':count,'pdf':source.relative_to(ROOT).as_posix(),
            'pdf_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'extraction':target.relative_to(ROOT).as_posix(),'extraction_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'command':command,'exit':result.returncode,'stderr':result.stderr})
    report={'date':'2026-11-26','scope':'Primary archived datasheet evidence for current NET26 union; no new hardware or dynamic current qualification.',
        'inventory_sha256':hashlib.sha256(inventory.read_bytes()).hexdigest(),'rows':rows,
        'pdftotext':subprocess.run(['pdftotext','-v'],capture_output=True,text=True).stderr,
        'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'production_released':False}
    (OUT/'extractions.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'extracted_families':len(rows),'ics':sum(r['count'] for r in rows if not r['family'].startswith('ACH_'))}))

if __name__=='__main__':main()
