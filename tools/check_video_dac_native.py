"""Independent pin faults and native schematic previews for NET33."""
import copy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import build_dac_video_adapter as build
import build_dac_leaf as native
from check_dac_leaf import move
from limited_process import run_limited

ROOT=build.ROOT
OUT=build.OUT

def main():
    vd,vp,_=build.video_configuration();dd,dp=build.dac_configuration()
    rows=[]
    fixtures=[('video','dac_packet_video',vd,vp,[('clock_wrong_phase','U35','12','P0'),
                ('blue_buffer_wrong_source','U27','9','PIXEL_1'),
                ('sync_clear_unbuffered','U38','1','LOCAL_RESET_N'),
                ('sync_data_wrong_polarity','U38','3','HSYNC_N')]),
              ('dac','vga_dac_rgb332',dd,dp,[('red_msb_wrong_bit','U1','1','PIXEL_6'),
                ('blue_buffer_bypassed','U3','5','PIXEL_1'),
                ('sleep_high','U1','15','+5V'),('complement_wrong_rail','U1','21','+5V')])]
    for label,name,defs,parts,cases in fixtures:
        source=OUT/label/(name+'.xml');original=ET.parse(source).getroot()
        for case,ref,pin,net in cases:
            root=copy.deepcopy(original);move(root,ref,pin,net)
            target=OUT/'pin-negatives'/(label+'-'+case+'.xml');target.parent.mkdir(parents=True,exist_ok=True)
            ET.ElementTree(root).write(target,encoding='utf-8',xml_declaration=True)
            try:native.validate(target,defs,parts)
            except AssertionError as error:rows.append({'case':case,'leaf':label,'rejected':True,'reason':str(error),'file':target.relative_to(ROOT).as_posix()})
            else:rows.append({'case':case,'leaf':label,'rejected':False})
        jobs={}
        for key,cmd in [('pdf',[native.KICAD,'sch','export','pdf','-o',str(OUT/label/'schematic.pdf'),str(ROOT/'hardware'/name/(name+'.kicad_sch'))]),
                        ('preview',['pdftoppm','-scale-to','2000','-singlefile','-png',str(OUT/label/'schematic.pdf'),str(OUT/label/'preview')])]:
            jobs[key]=run_limited(cmd,ROOT,timeout=120,memory_mb=2048,cpu_seconds=90,output_mb=2)
            build.save(OUT/label/'preview-commands.json',jobs)
            assert jobs[key]['exit']==0 and not jobs[key]['wall_timeout'],jobs[key]
    report={'date':'2026-11-27','scope':'Pin faults in copied XMLs and preview export only; no hardware release.',
        'pin_negatives':rows,'failures':[r['case'] for r in rows if not r['rejected']],
        'sources':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in [
            'tools/check_video_dac_native.py','tools/check_dac_leaf.py','tools/build_dac_video_adapter.py','tools/build_dac_leaf.py',
            'verification/net33/video/dac_packet_video.xml','verification/net33/dac/vga_dac_rgb332.xml']],
        'production_released':False}
    build.save(OUT/'pin-negative-results.json',report)
    print(json.dumps({'pin_negatives':len(rows),'failures':report['failures']}))
    assert not report['failures']

if __name__=='__main__':main()
