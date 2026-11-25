"""NET-14B free-running reset scenarios and real pin/timing fault calibrations."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from run_rtl import run
from build_video_raster import ROOT,OUT,VERIFY,convert


def main():
    old_grant=VERIFY/'development/grant-late/video_raster_netlist.sv.txt'
    old_sync=VERIFY/'development/sync-decode-late/video_raster_netlist.sv.txt'
    common=[ROOT/n for n in ['sim/hdl/hc_models.sv','sim/net03/package_models.sv','sim/net04/package_models.sv','sim/net13/memory_devices.sv',
      'hardware/memory_decode/memory_decode_netlist.sv','hardware/memory_bus_access/memory_access_netlist.sv','hardware/memory_bus/memory_bus_netlist.sv','sim/net14b/package_models.sv']]
    tested=[*common,old_grant,old_sync,OUT/'video_raster_netlist.sv',VERIFY/'video_raster.xml',ROOT/'sim/net14b/tb_raster_reset.sv',ROOT/'sim/net14b/tb_video_raster.sv',Path(__file__)]
    report={'iteration':'NET-14B','date':'2026-11-25',
      'scope':'Selected free-running release offsets outside first synchronizer recovery aperture; no metastability/MTBF or physical reset/WE sequence approval',
      'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in tested],
      'runs':[],'negative':[],'failures':[]}
    def save():(VERIFY/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='isa1-raster-checks-') as tmp:
        w=Path(tmp)
        def execute(bench,netlist,early=0):
            cmd=['iverilog','-g2012','-Wall','-s',bench,f'-P{bench}.TIMED=1','-o',str(w/'test.vvp')]
            if bench=='tb_video_raster':cmd.append(f'-P{bench}.EARLY_CAPTURE={early}')
            cmd += [*map(str,common),str(netlist),str(ROOT/'sim/net14b'/(bench+'.sv'))]
            r={'bench':bench,'compile':run(cmd,w)}
            if not r['compile']['exit']:r['execution']=run(['vvp',str(w/'test.vvp')],w,timeout=90)
            return r
        r=execute('tb_raster_reset',OUT/'video_raster_netlist.sv')
        r['passed']=r['compile']['exit']==0 and r.get('execution',{}).get('exit')==0 and 'reset_cuts=16 captured_pixels=512' in r['execution']['stdout']
        report['runs'].append(r)
        if not r['passed']:report['failures'].append('Free-running reset')
        save();print(json.dumps(r),flush=True)
        if report['failures']:return 1
        for description,netlist,early,expected in [('Prior phase-1 grant',old_grant,0,'DFF data setup violation'),('Prior serial HSYNC decoder',old_sync,1,'sync mismatch')]:
            r=execute('tb_video_raster',netlist,early);r.update(case=description,expected_rejection=True)
            r['passed']=r['compile']['exit']==0 and r.get('execution',{}).get('exit',0)!=0 and expected in r['execution']['stdout']
            report['negative'].append(r)
            if not r['passed']:report['failures'].append(description)
            save();print(json.dumps(r),flush=True)
        for ref,pin,kind,expected in [('U1','1','floating','Floating input U1/1'),('U4','8','power','Wrong power U4')]:
            tree=ET.parse(VERIFY/'video_raster.xml');root=tree.getroot();node=None
            for net in root.findall('./nets/net'):
                for candidate in net.findall('node'):
                    if candidate.get('ref')==ref and candidate.get('pin')==pin:
                        node=candidate;net.remove(node);break
                if node is not None:break
            assert node is not None
            if kind=='power':next(n for n in root.findall('./nets/net') if n.get('name').removeprefix('/')=='+5V').append(node)
            path=w/'bad.xml';tree.write(path)
            try:convert(path,w/'bad.sv')
            except ValueError as e:message=str(e)
            else:message='No rejection'
            r={'case':kind+' '+ref+'/'+pin,'expected_rejection':True,'message':message,'passed':expected in message}
            report['negative'].append(r)
            if not r['passed']:report['failures'].append(r['case'])
            save();print(json.dumps(r),flush=True)
    return int(bool(report['failures']))


if __name__=='__main__':raise SystemExit(main())
