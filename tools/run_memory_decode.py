"""Exhaustive address-map checks and pin mutations for NET-11."""
import hashlib
import json
import platform
import subprocess
import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
from build_memory_decode import ROOT,OUT,VERIFY,convert
from run_rtl import run


def main():
    sources=[ROOT/p for p in ('tools/build_memory_decode.py','tools/run_memory_decode.py','sim/net11/tb_memory_decode.sv','hardware/memory_decode/design.json','hardware/memory_decode/package-functions.json','hardware/memory_decode/memory_decode_netlist.sv','verification/net11/memory_decode.xml','tools/build_x_register_bank.py','tools/build_stack_bank.py','tools/build_microcode_bank.py')]
    report={'date':'2026-11-25','iteration':'NET-11','scope':'Address decode only, no physical memory strobe/CDC/write timing approval',
      'python':platform.python_version(),'iverilog':subprocess.run(['iverilog','-V'],capture_output=True,text=True).stdout.splitlines()[0],
      'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],'runs':[],'negative':[]}
    def save():(VERIFY/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='isa1-memdecode-') as tmp:
        work=Path(tmp)
        def test(source,timed=0,smoke=0):
            cmd=['iverilog','-g2012','-Wall','-s','tb_memory_decode',f'-Ptb_memory_decode.TIMED={timed}',f'-Ptb_memory_decode.SMOKE={smoke}','-o',str(work/'test.vvp'),str(source),str(ROOT/'sim/net11/tb_memory_decode.sv')]
            row={'timed':timed,'compile':run(cmd,work)}
            if not row['compile']['exit']:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=900)
            return row
        for timed in (0,1):
            row=test(OUT/'memory_decode_netlist.sv',timed);report['runs'].append(row);save();print(json.dumps(row),flush=True)
            if row['compile']['exit'] or row.get('execution',{}).get('exit')!=0:return 1
        tree=ET.parse(VERIFY/'memory_decode.xml');root=tree.getroot()
        eb=next(n for n in root.findall('./nets/net') if n.get('name').removeprefix('/')=='EB')
        ground=next(n for n in root.findall('./nets/net') if n.get('name').removeprefix('/')=='GND')
        node=eb.find('node');eb.remove(node);ground.append(node)
        bad=work/'bad.xml';tree.write(bad);convert(bad,work/'bad.sv')
        row=test(work/'bad.sv',1,1);row.update(case='EEPROM bank EB input stuck low',expected_rejection=True)
        row['passed']=row['compile']['exit']==0 and row.get('execution',{}).get('exit')!=0 and 'physical address mismatch' in row['execution']['stdout']
        report['negative'].append(row)
        tree=ET.parse(VERIFY/'memory_decode.xml');root=tree.getroot();safe=next(n for n in root.findall('./nets/net') if n.get('name').removeprefix('/')=='SAFE');node=safe.find('node');safe.remove(node);tree.write(bad)
        try:convert(bad,work/'floating.sv')
        except ValueError as e:message=str(e)
        else:message='No rejection'
        report['negative'].append({'case':'SAFE qualifier floating','expected_rejection':True,'message':message,'passed':'Floating input' in message})
        save();print(json.dumps(report['negative']),flush=True)
    return int(not all(r['passed'] for r in report['negative']))


if __name__=='__main__':raise SystemExit(main())
