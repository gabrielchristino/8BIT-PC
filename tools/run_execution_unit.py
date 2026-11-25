"""NET-08 isolated guard/handshake tests and deliberate connection failures."""
import hashlib
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
from run_rtl import ROOT,run
from build_execution_bank import convert,definitions
OUT=ROOT/'verification/net08'


def main():
    model=ROOT/'sim/net03/package_models.sv';bank=ROOT/'hardware/execution_bank/execution_bank_netlist.sv'
    bench=ROOT/'sim/net08/tb_execution_bank.sv';source=OUT/'execution_bank.xml'
    sources=[model,bank,bench,source,Path(__file__),ROOT/'tools/build_execution_bank.py']
    report={'date':'2026-11-25','sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],'runs':[],'negative_checks':[]}
    with tempfile.TemporaryDirectory(prefix='isa1-execution-unit-') as tmp:
        work=Path(tmp)
        def execute(path,timed):
            compiled=run(['iverilog','-g2012','-Wall','-s','tb_execution_bank',f'-Ptb_execution_bank.TIMED={timed}','-o',str(work/'bench.vvp'),str(model),str(path),str(bench)],work)
            executed=run(['vvp',str(work/'bench.vvp')],work,timeout=900) if compiled['exit']==0 else None
            return {'timed':timed,'compile':compiled,'execution':executed}
        for timed in (0,1):
            row=execute(bank,timed);report['runs'].append(row)
            (OUT/'unit-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(row),flush=True)
            if row['compile']['exit'] or row['execution']['exit']:return 1
        tree=ET.parse(source);ground=next(n for n in tree.getroot().findall('./nets/net') if n.get('name').removeprefix('/')=='GND')
        for net in tree.getroot().findall('./nets/net'):
            for node in list(net.findall('node')):
                if node.get('ref')=='U1' and node.get('pin')=='3':net.remove(node);ground.append(node)
        tree.write(work/'stuck.xml');convert(work/'stuck.xml',definitions(),work/'stuck.sv');bad=execute(work/'stuck.sv',0)
        report['negative_checks'].append({'case':'Response state D stuck low','expected_rejection':True,'passed':bad['execution'] is not None and bad['execution']['exit']!=0 and 'Guard mismatch' in bad['execution']['stdout'],**bad})
        tree=ET.parse(source)
        for net in tree.getroot().findall('./nets/net'):
            for node in list(net.findall('node')):
                if node.get('ref')=='U1' and node.get('pin')=='1':net.remove(node)
        tree.write(work/'floating.xml')
        try:convert(work/'floating.xml',definitions(),work/'floating.sv')
        except ValueError as error:message=str(error)
        else:message='No rejection'
        report['negative_checks'].append({'case':'Execution state clear floating','expected_rejection':True,'passed':'Floating input U1/1' in message,'message':message})
    (OUT/'unit-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'negative_checks':report['negative_checks']}),flush=True)
    return int(not all(x['passed'] for x in report['negative_checks']))


if __name__=='__main__':raise SystemExit(main())
