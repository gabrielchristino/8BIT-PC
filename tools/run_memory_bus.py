"""NET-13 full-address tests, integrated bus handoff and fault calibration."""
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from build_memory_bus import ROOT,OUT,VERIFY,convert
from run_rtl import run


def main():
    common=[ROOT/p for p in ['sim/hdl/hc_models.sv','sim/net03/package_models.sv','sim/net04/package_models.sv','sim/net13/memory_devices.sv','hardware/memory_decode/memory_decode_netlist.sv']]
    ctrl=ROOT/'hardware/memory_bus_access/memory_access_netlist.sv';front=OUT/'memory_bus_netlist.sv'
    sources=[*common,ctrl,front,*[ROOT/p for p in ['tools/build_memory_bus.py','tools/run_memory_bus.py','tools/prepare_memory_bus_access.py','tools/build_memory_bus_access.py','sim/net13/tb_memory_bus.sv','sim/net13/tb_memory_fabric.sv','hardware/memory_bus/design.json','hardware/memory_bus/package-functions.json','verification/net13/memory_bus.xml','verification/net13/access/memory_access.xml','verification/net11/memory_decode.xml']]]
    report={'date':'2026-11-25','iteration':'NET-13','python':platform.python_version(),'iverilog':subprocess.run(['iverilog','-V'],capture_output=True,text=True).stdout.splitlines()[0],
      'scope':'Pin-derived memory/controller/decoder with selected component models; ideal weak pull-ups, analog RC analyzed separately; no physical loads/PCB/PVT or programming approval',
      'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],'runs':[],'negative':[]}
    def save():(VERIFY/'bus-results.json').write_text(json.dumps(report,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='isa1-bus-') as tmp:
        work=Path(tmp)
        def test(bench,timed,early,controller=ctrl,source=front,smoke=0):
            cmd=['iverilog','-g2012','-Wall','-s',bench,f'-P{bench}.TIMED={timed}',f'-P{bench}.EARLY_ON={early}']
            if bench=='tb_memory_fabric':cmd.append(f'-P{bench}.SMOKE={smoke}')
            cmd+=['-o',str(work/'test.vvp'),*map(str,common),str(controller),str(source),str(ROOT/'sim/net13'/(bench+'.sv'))]
            row={'bench':bench,'timed':timed,'early_on':early,'compile':run(cmd,work)}
            if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=900)
            return row
        for bench,timed,early in [('tb_memory_bus',0,0),('tb_memory_bus',1,1),('tb_memory_fabric',1,0),('tb_memory_fabric',1,1)]:
            row=test(bench,timed,early);report['runs'].append(row);save();print(json.dumps(row),flush=True)
            if row['compile']['exit'] or row.get('execution',{}).get('exit')!=0:return 1
        # The previous valid partial controller has no early driver-release
        # phase. The actual front-end must expose its handoff contention.
        row=test('tb_memory_fabric',1,1,ROOT/'hardware/memory_access/memory_access_netlist.sv',smoke=1)
        row.update(case='NET-12 controller without registered driver dead interval',expected_rejection=True)
        row['passed']=row['compile']['exit']==0 and row.get('execution',{}).get('exit')!=0 and 'SRAM output and write buffer overlap VRAM' in row['execution']['stdout'];report['negative'].append(row);save()
        original=VERIFY/'memory_bus.xml'
        for name,ref,pin,ground,expected in [('SRAM WE disconnected','U1','27',False,'Floating input U1/27'),('EEPROM WE grounded','U3','27',True,'EEPROM WE is not permanently protected HIGH')]:
            tree=ET.parse(original);root=tree.getroot();target=next(n for n in root.findall('./nets/net') if n.get('name').removeprefix('/')=='GND');found=False
            for n in root.findall('./nets/net'):
                for node in list(n.findall('node')):
                    if node.get('ref')==ref and node.get('pin')==pin:n.remove(node);found=True;break
                if found:break
            assert found
            if ground:target.append(node)
            path=work/'bad.xml';tree.write(path)
            try:convert(path,work/'bad.sv')
            except ValueError as e:message=str(e)
            else:message='No rejection'
            report['negative'].append({'case':name,'expected_rejection':True,'message':message,'passed':expected in message});save()
        print(json.dumps(report['negative']),flush=True)
    return int(not all(r['passed'] for r in report['negative']))


if __name__=='__main__':raise SystemExit(main())
