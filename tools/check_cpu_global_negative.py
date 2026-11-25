"""Joined CPU pin checker must reject a floating clock and a supply short."""
import hashlib
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
from build_cpu_global import ROOT,VERIFY
from convert_cpu_global import convert


def main():
    source=VERIFY/'cpu_global.xml';report={'date':'2026-11-25','sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [source,Path(__file__),ROOT/'tools/convert_cpu_global.py']],'checks':[]}
    with tempfile.TemporaryDirectory(prefix='isa1-global-negative-') as tmp:
        work=Path(tmp)
        for label,pin,expected in [('Floating SP clock','11','Floating input U1/11'),('SP output shorted to supply','2','Driver count')]:
            tree=ET.parse(source);root=tree.getroot()
            high=next(n for n in root.findall('./nets/net') if n.get('name').removeprefix('/')=='+5V')
            found=False
            for net in root.findall('./nets/net'):
                for node in list(net.findall('node')):
                    if node.get('ref')=='U1' and node.get('pin')==pin:
                        net.remove(node);found=True
                        if pin=='2':high.append(node)
            if not found:raise ValueError('Mutation target absent')
            target=work/'bad.xml';tree.write(target)
            try:convert(target,work/'bad.sv')
            except ValueError as error:message=str(error)
            else:message='No rejection'
            report['checks'].append({'case':label,'expected_rejection':True,'message':message,'passed':expected in message and (pin!='2' or '+5V' in message)})
    (VERIFY/'negative.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['checks']));return int(not all(x['passed'] for x in report['checks']))


if __name__=='__main__':raise SystemExit(main())
