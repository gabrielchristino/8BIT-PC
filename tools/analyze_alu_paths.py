"""Conservative path envelope for the selected NET-05 package delay model.

Not STA: no minimum delay, skew, voltage waveform, trace or load extraction.
"""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net05'


def analyze():
    source=OUT/'alu_bank.xml';root=ET.parse(source).getroot()
    specs=json.loads((ROOT/'hardware/alu_bank/package-functions.json').read_text())
    pins={}
    for net in root.findall('./nets/net'):
        for node in net.findall('node'):pins[node.get('ref'),node.get('pin')]=net.get('name').removeprefix('/')
    arcs=[]
    for comp in root.findall('./components/comp'):
        ref=comp.get('ref');kind='C' if ref.startswith('C') else comp.findtext('value')
        if kind=='C':continue
        fs={s['name']:pins.get((ref,p)) for p,s in specs[kind]['pins'].items()}
        def arc(output,inputs,delay):
            n=fs.get(output)
            if n and not n.startswith('unconnected-'):arcs.append({'net':n,'inputs':[fs[i] for i in inputs],'delay_ns':delay,'pin':ref+'/'+output})
        if kind=='CD74HC283':
            inputs=['CIN']+[f'{p}{i}' for p in ('A','B') for i in range(4)]
            for i in range(4):arc(f'S{i}',inputs,58)
            arc('COUT',inputs,49)
        elif kind=='SN74HC138':
            for i in range(8):arc(f'Y{i}',['A','B','C','G1','G2A_N','G2B_N'],45)
        elif kind in ('SN74HC08','SN74HC32','SN74HC86'):
            for i in range(4):arc(f'Y{i}',[f'A{i}',f'B{i}'],31)
        elif kind=='SN74HC04':
            for i in range(6):arc(f'Y{i}',[f'A{i}'],24)
        elif kind=='SN74HC125':
            for i in range(4):arc(f'Y{i}',[f'A{i}',f'OE{i}_N'],36)
        else:raise ValueError('No timing arcs for '+kind)
    arrival={n:{'ns':0,'path':[]} for n in ['+5V','GND','C_IN']+[f'{p}_{i}' for p,k in [('A',8),('B',8),('OP',4)] for i in range(k)]}
    pending=arcs.copy()
    while pending:
        ready=[a for a in pending if all(n in arrival for n in a['inputs'])]
        if not ready:raise ValueError('Cycle or undriven timing dependency')
        for a in ready:
            worst=max((arrival[n] for n in a['inputs']),key=lambda x:x['ns'])
            if a['net'] in arrival:raise ValueError('Duplicate timing driver '+a['net'])
            arrival[a['net']]={'ns':worst['ns']+a['delay_ns'],'path':worst['path']+[a['pin']]}
            pending.remove(a)
    outputs={n:arrival[n] for n in [*[f'RESULT_{i}' for i in range(8)],'C_OUT','ZERO']}
    bound=max(x['ns'] for x in outputs.values())
    report={'date':'2026-11-25','sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [source,ROOT/'hardware/alu_bank/package-functions.json',Path(__file__)]],
      'scope':'Selected constant-delay combinational envelope only; not board timing closure',
      'assumptions':'HC at 4.5 V, -40..85 C, CL <=50 pF; package delays conservatively grouped; external input changes at time zero; no trace/skew/minimum modeling',
      'arcs':len(arcs),'outputs':outputs,'max_settle_ns':bound,'bench_settle_ns':1000,'passed':bound<1000}
    (OUT/'path-envelope.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'arcs':len(arcs),'max_settle_ns':bound,'bench_settle_ns':1000,'passed':report['passed']}))
    return int(not report['passed'])


if __name__=='__main__':raise SystemExit(analyze())
