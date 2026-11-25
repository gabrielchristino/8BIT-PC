"""NET-09 exposes existing EXEC_ACCEPT and uses a spare inverter for memory mode.

Separate native schematic/XML variant: never rewrites accepted NET-08 files.
"""
import copy
import hashlib
import json
import subprocess
from pathlib import Path
import build_execution_bank as base
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/cpu_execution_glue';VERIFY=ROOT/'verification/net09'


def main():
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    defs=base.definitions();parts,gates=base.design(defs)
    spare=None
    for p in parts:
        if p['part']!='SN74HC04':continue
        fs={v['name']:pin for pin,v in defs[p['part']]['pins'].items()}
        for i in range(6):
            if p['nets'][fs[f'Y{i}']] is None:
                p['nets'][fs[f'A{i}']]='MEM_N_2';p['nets'][fs[f'Y{i}']]='WRITE_MODE';spare={'reference':p['reference'],'input_pin':fs[f'A{i}'],'output_pin':fs[f'Y{i}']};break
        if spare:break
    if not spare:raise ValueError('No verified spare inverter')
    previous=base.OUT;base.OUT=OUT
    try:rows=base.emit_schematic(defs,parts)
    finally:base.OUT=previous
    schematic=OUT/'execution_bank.kicad_sch'
    schematic.write_text(schematic.read_text().replace('(rev "NET-08")','(rev "NET-09")').replace('ISA-1 execution handshake / guards / faults','ISA-1 execution with explicit CPU glue outputs'))
    (OUT/'package-functions.json').write_text(json.dumps(defs,indent=2)+'\n')
    (OUT/'design.json').write_text(json.dumps({'iteration':'NET-09','parts':parts,'transformation':'Expose existing EXEC_ACCEPT; wire spare HC04 channel MEM_N_2 -> WRITE_MODE','spare':spare},indent=2)+'\n')
    xml=VERIFY/'execution_glue.xml'
    cmd=['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(xml),str(schematic)]
    result=subprocess.run(cmd,capture_output=True,text=True,check=True)
    dest=OUT/'execution_bank_net09.sv';actual,loads=base.convert(xml,defs,dest)
    text=dest.read_text().replace('module execution_bank_netlist','module execution_bank_net09').replace('fault,state);','fault,state,output wire execute_accept,write_mode);')
    for n in ('EXEC_ACCEPT','WRITE_MODE'):
        if n not in actual.values():raise ValueError('Missing physical glue '+n)
    text=text.replace('endmodule','assign execute_accept=n_EXEC_ACCEPT;\nassign write_mode=n_WRITE_MODE;\nendmodule')
    dest.write_text(text)
    failures=[]
    for row in rows:
        found=actual.get((row['reference'],row['pin']))
        if row['net']=='NC':
            if found and not found.startswith('unconnected-'):failures.append(row)
        elif found!=row['net']:failures.append(row)
    max_load=max(len(v) for n,v in loads.items() if n not in ('GND','+5V'))
    if max_load>4:failures.append('Fanout limit')
    subprocess.run(['kicad-cli','sch','export','pdf','-o',str(VERIFY/'execution_glue.pdf'),str(schematic)],check=True,capture_output=True)
    report={'date':'2026-11-25','base_schema_source':'tools/build_execution_bank.py','base_schema_sha256':hashlib.sha256((ROOT/'tools/build_execution_bank.py').read_bytes()).hexdigest(),
      'command':cmd,'kicad':subprocess.check_output(['kicad-cli','version'],text=True).strip(),'components':len(parts),'pins':len(rows),'spare':spare,'max_signal_input_loads':max_load,'failures':failures,
      'scope':'Separate NET-09 execution schematic variant, same IC count; no board release'}
    (VERIFY/'execution-glue-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report));return int(bool(failures))


if __name__=='__main__':raise SystemExit(main())
