"""Maximum propagation paths of the selected combinational NET-11 model.

No minimum-delay, analog, PCB/skew, or full PVT signoff is implied.
"""
import hashlib
import json
import xml.etree.ElementTree as ET
from build_memory_decode import ROOT,OUT,VERIFY,ports


def main():
    source=VERIFY/'memory_decode.xml';defs=json.loads((OUT/'package-functions.json').read_text())
    root=ET.parse(source).getroot();actual={}
    for net in root.findall('./nets/net'):
        for node in net.findall('node'):actual[node.get('ref'),node.get('pin')]=net.get('name').removeprefix('/')
    edges={}
    for c in root.findall('./components/comp'):
        ref=c.get('ref');kind=c.findtext('value')
        if ref.startswith('C'):continue
        fs={s['name']:(p,actual.get((ref,p))) for p,s in defs[kind]['pins'].items()}
        count=6 if kind=='SN74HC04' else 4
        delay=24 if kind=='SN74HC04' else 36 if kind=='SN74HC125' else 31
        for i in range(count):
            pin,n=fs[f'Y{i}']
            if not n or n.startswith('unconnected-'):continue
            deps=[fs[f'A{i}']]
            if kind in ('SN74HC08','SN74HC32'):deps.append(fs[f'B{i}'])
            if kind=='SN74HC125':deps.append(fs[f'OE{i}_N'])
            if n in edges:raise ValueError('Multiple drivers '+n)
            edges[n]={'reference':ref,'part':kind,'output_pin':pin,'deps':deps,'delay_ns':delay}
    ins,outs=ports();arrivals={n:(0,[]) for n in [*ins,'GND','+5V']}
    visiting=set()
    def arrival(n):
        if n in arrivals:return arrivals[n]
        if n in visiting:raise ValueError('Combinational cycle '+n)
        if n not in edges:raise ValueError('Unknown driver '+str(n))
        visiting.add(n);e=edges[n]
        choices=[(*arrival(dep),pin,dep) for pin,dep in e['deps']]
        value,path,pin,dep=max(choices,key=lambda row:row[0]);visiting.remove(n)
        step={'reference':e['reference'],'part':e['part'],'input_pin':pin,'input_net':dep,'output_pin':e['output_pin'],'output_net':n,'delay_ns':e['delay_ns']}
        arrivals[n]=(value+e['delay_ns'],path+[step]);return arrivals[n]
    rows=[{'net':n,'port':p,'arrival_ns':arrival(n)[0],'path':arrival(n)[1]} for n,p in outs.items()]
    slow=max(rows,key=lambda r:r['arrival_ns'])
    report={'date':'2026-11-25','sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [source,OUT/'package-functions.json',ROOT/'tools/build_memory_decode.py',ROOT/'tools/analyze_memory_decode.py']],
      'scope':'Longest paths of selected maximum-delay combinational model, zero input arrival; not minimum/hold/hazard/PCB or complete PVT analysis',
      'assumed_settle_interval_ns':1000,'maximum_path_ns':slow['arrival_ns'],'model_settle_margin_ns':1000-slow['arrival_ns'],'slowest_output':slow['net'],'outputs':rows,'production_released':False}
    (VERIFY/'propagation-paths.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['maximum_path_ns','model_settle_margin_ns','slowest_output','production_released']}))
    return int(report['model_settle_margin_ns']<0)


if __name__=='__main__':raise SystemExit(main())
