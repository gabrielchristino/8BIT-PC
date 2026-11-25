"""NET-09 deliberately breaks increment and clear connection, separately from acceptance."""
import hashlib
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
from run_rtl import ROOT,run
from build_x_register_bank import convert,definitions
OUT=ROOT/'verification/net09'


def main():
    source=OUT/'x_register_bank.xml';bench=ROOT/'sim/net09/tb_x_register_bank.sv'
    models=[ROOT/'sim/hdl/hc_models.sv',ROOT/'sim/net02/package_models.sv']
    sources=[source,bench,*models,Path(__file__),ROOT/'tools/build_x_register_bank.py']
    report={'date':'2026-11-25','scope':'Expected negative connection tests, not normal regression failures',
      'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],'checks':[]}
    with tempfile.TemporaryDirectory(prefix='isa1-x-negative-') as tmp:
        work=Path(tmp);tree=ET.parse(source)
        ground=next(n for n in tree.getroot().findall('./nets/net') if n.get('name').removeprefix('/')=='GND')
        for net in tree.getroot().findall('./nets/net'):
            for node in list(net.findall('node')):
                if node.get('ref')=='U3' and node.get('pin')=='6':net.remove(node);ground.append(node)
        tree.write(work/'bad.xml');convert(work/'bad.xml',definitions(),work/'bad.sv')
        compiled=run(['iverilog','-g2012','-Wall','-s','tb_x_register_bank','-o',str(work/'bad.vvp'),*map(str,models),str(work/'bad.sv'),str(bench)],work)
        executed=run(['vvp',str(work/'bad.vvp')],work) if compiled['exit']==0 else None
        report['checks'].append({'case':'Low-bit adder constant tied zero','expected_rejection':True,'passed':executed is not None and executed['exit']!=0 and 'X mismatch' in executed['stdout'],'compile':compiled,'execution':executed})
        tree=ET.parse(source)
        for net in tree.getroot().findall('./nets/net'):
            for node in list(net.findall('node')):
                if node.get('ref')=='U1' and node.get('pin')=='1':net.remove(node)
        tree.write(work/'floating.xml')
        try:convert(work/'floating.xml',definitions(),work/'floating.sv')
        except ValueError as error:message=str(error)
        else:message='No rejection'
        report['checks'].append({'case':'X clear disconnected','expected_rejection':True,'passed':'Floating input U1/1' in message,'message':message})
    (OUT/'negative.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'checks':len(report['checks']),'passed':sum(x['passed'] for x in report['checks'])}))
    return int(not all(x['passed'] for x in report['checks']))


if __name__=='__main__':raise SystemExit(main())
