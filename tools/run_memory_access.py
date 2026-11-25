"""NET-12 directed access, reset/ownership coverage and pin-fault checks."""
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from build_memory_access import ROOT,OUT,VERIFY,convert
from run_rtl import run


def main():
    models=[ROOT/p for p in ['sim/hdl/hc_models.sv','sim/net03/package_models.sv','sim/net04/package_models.sv','hardware/memory_decode/memory_decode_netlist.sv']]
    source=OUT/'memory_access_netlist.sv';bench=ROOT/'sim/net12/tb_memory_access.sv'
    files=[*models,source,bench,*[ROOT/p for p in ['tools/build_memory_access.py','tools/run_memory_access.py','hardware/memory_access/design.json','hardware/memory_access/package-functions.json','verification/net12/memory_access.xml','tools/build_transaction_bank.py','tools/build_microcode_bank.py','tools/build_stack_bank.py']]]
    report={'date':'2026-11-25','iteration':'NET-12','python':platform.python_version(),'iverilog':subprocess.run(['iverilog','-V'],capture_output=True,text=True).stdout.splitlines()[0],
      'scope':'Pin-derived controller and NET-11 decoder; modeled read source delayed 220ns, half-cycle prepared grants; no physical memory/raster, analog reset, minimum/skew/MTBF or production signoff',
      'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'runs':[],'negative':[]}
    def save():(VERIFY/'unit-results.json').write_text(json.dumps(report,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='isa1-memory-access-') as tmp:
        work=Path(tmp)
        def test(src,timed=0,half=500,smoke=0):
            cmd=['iverilog','-g2012','-Wall','-s','tb_memory_access',f'-Ptb_memory_access.TIMED={timed}',f'-Ptb_memory_access.HALF={half}',f'-Ptb_memory_access.SMOKE={smoke}','-o',str(work/'test.vvp'),*map(str,models),str(src),str(bench)]
            row={'timed':timed,'half_ns':half,'compile':run(cmd,work)}
            if not row['compile']['exit']:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=120)
            return row
        for timed,half in [(0,500),(1,500),(1,79.445)]:
            row=test(source,timed,half);report['runs'].append(row);save();print(json.dumps(row),flush=True)
            if row['compile']['exit'] or row.get('execution',{}).get('exit')!=0:return 1
        original=VERIFY/'memory_access.xml'
        for label,ref,pin,constant,expected,smoke in [
          ('Payload enable stuck low','U5','1','GND','held payload changed',1),
          ('VRAM owner no longer qualified by BUS_ACTIVE',None,None,'+5V','VRAM owner reached visible',0)]:
            tree=ET.parse(original);root=tree.getroot()
            if ref is None:
                # Locate the AHC08 driver of VRAM_OWNER by physical net/pins.
                owner=next(n for n in root.findall('./nets/net') if n.get('name').removeprefix('/')=='VRAM_OWNER');driver=owner.find('node');ref=driver.get('ref');outpin=driver.get('pin')
                defs=json.loads((OUT/'package-functions.json').read_text());channel=defs['SN74AHC08']['pins'][outpin]['name'][1:]
                part=next(p for p in json.loads((OUT/'design.json').read_text())['parts'] if p['reference']==ref)
                pin=next(p for p,s in defs['SN74AHC08']['pins'].items() if s['name'] in ('A'+channel,'B'+channel) and part['nets'][p]!='SELECT_1')
            target=next(n for n in root.findall('./nets/net') if n.get('name').removeprefix('/')==constant)
            found=False
            for n in root.findall('./nets/net'):
                for node in list(n.findall('node')):
                    if node.get('ref')==ref and node.get('pin')==pin:n.remove(node);target.append(node);found=True;break
                if found:break
            assert found
            bad=work/'mutated.xml';tree.write(bad);convert(bad,work/'mutated.sv');row=test(work/'mutated.sv',1,500,smoke)
            row.update(case=label,expected_rejection=True,passed=row['compile']['exit']==0 and row.get('execution',{}).get('exit')!=0 and expected in row['execution']['stdout']);report['negative'].append(row);save()
        tree=ET.parse(original);root=tree.getroot();removed=False
        for n in root.findall('./nets/net'):
            for node in list(n.findall('node')):
                if node.get('ref')=='U5' and node.get('pin')=='11':n.remove(node);removed=True
        assert removed;bad=work/'floating.xml';tree.write(bad)
        try:convert(bad,work/'floating.sv')
        except ValueError as e:message=str(e)
        else:message='No rejection'
        report['negative'].append({'case':'Payload clock disconnected','expected_rejection':True,'message':message,'passed':'Floating input U5/11' in message});save();print(json.dumps(report['negative']),flush=True)
    return int(not all(r['passed'] for r in report['negative']))


if __name__=='__main__':raise SystemExit(main())
