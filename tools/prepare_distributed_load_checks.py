"""Derive separate projections/runners from NET26; never regenerate ancestors."""
import hashlib
import json
from pathlib import Path
from run_request_skew_probe import once

ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'sim/net30';out.mkdir(parents=True,exist_ok=True)
    paths=['tools/prepare_distributed_load_checks.py','tools/build_distributed_loads.py']
    source='hardware/load_distributed_video/load_distributed_video_netlist.sv';text=(ROOT/source).read_text()
    text=once(text,'EARLY_CAPTURE=0)','EARLY_CAPTURE=0,RESOLVE_LATE=1)')
    text=once(text,'net22_ahc164 #(.TIMED(TIMED),.EARLY_CAPTURE(EARLY_CAPTURE)) U8',
        'net25_warm164 #(.TIMED(TIMED),.BOUNDARY(1),.RESOLVE_LATE(RESOLVE_LATE)) U8')
    for ref in ['U8','U9']:
        rows=text.splitlines();indexes=[i for i,row in enumerate(rows) if ') '+ref+'(' in row];assert len(indexes)==1
        i=indexes[0];assert rows[i].endswith(',checks);');rows[i]=rows[i][:-len(',checks);')]+",1'b1);";text='\n'.join(rows)+'\n'
    for i in range(2):
        text=once(text,f'#(.TIMED(TIMED),.EARLY(0 && EARLY_CAPTURE)) U37_{i}',
            f'#(.TIMED(TIMED),.RESET_BOUNDARY(1),.FIRST_STAGE({1 if i==0 else 0}),.RESOLVE_LATE(RESOLVE_LATE),.EARLY(0 && EARLY_CAPTURE)) U37_{i}')
    dest='sim/net30/load_video_async.sv';(ROOT/dest).write_text(text);paths.extend([source,dest])
    source='sim/net26/isa1_memory_local_phase.sv';text=(ROOT/source).read_text()
    for old,new in [('local_phase_video_netlist','load_distributed_video_netlist'),
        ('local_phase_keyboard_netlist','load_distributed_keyboard_netlist'),('memory_bus_netlist','load_distributed_bus_netlist')]:
        text=once(text,old,new)
    dest='sim/net30/isa1_memory_loads.sv';(ROOT/dest).write_text('// NET30 candidate; four spare data buffers, original reset/clock/CPU unchanged.\n'+text);paths.extend([source,dest])
    for suffix in ['vectors','program','cpu_fault','memory']:
        source='tools/run_local_phase_'+suffix+'.py';dest='tools/run_distributed_load_'+suffix+'.py'
        text=(ROOT/source).read_text()
        for old,new in [('verification/net26','verification/net30'),
            ('hardware/local_phase_keyboard/local_phase_keyboard_netlist.sv','hardware/load_distributed_keyboard/load_distributed_keyboard_netlist.sv'),
            ('sim/net26/isa1_memory_local_phase.sv','sim/net30/isa1_memory_loads.sv'),
            ('sim/net26/local_video_async.sv','sim/net30/load_video_async.sv'),
            ('verification/net30/native/video/local_phase_video.xml','verification/net30/native/video/load_distributed_video.xml'),
            ('verification/net30/native/keyboard/local_phase_keyboard.xml','verification/net30/native/keyboard/load_distributed_keyboard.xml'),
            ('verification/net30/native/reset/local_phase_reset.xml','verification/net26/native/reset/local_phase_reset.xml'),
            ('sim/net26/tb_local_phase_memory.sv','sim/net30/tb_load_memory.sv'),(source,dest)]:text=text.replace(old,new)
        mapping="[('hardware/load_distributed_bus/load_distributed_bus_netlist.sv' if p=='hardware/memory_bus/memory_bus_netlist.sv' else p) for p in PLACEHOLDER]"
        if suffix in ['vectors','program']:
            text=once(text,'    original = base.fixture','    base.MODELS = '+mapping.replace('PLACEHOLDER','base.MODELS')+'\n    original = base.fixture')
        else:
            marker='    sources = names +' if suffix=='cpu_fault' else "    report={'date'"
            text=once(text,marker,'    names = '+mapping.replace('PLACEHOLDER','names')+'\n'+marker)
        extra="'tools/build_distributed_loads.py', 'tools/prepare_distributed_load_checks.py', 'hardware/load_distributed_video/design.json', 'hardware/load_distributed_keyboard/design.json', 'hardware/load_distributed_bus/design.json', 'verification/net30/native/bus/load_distributed_bus.xml', "
        text=text.replace("'tools/build_local_phase_reset.py',",extra+"'tools/build_local_phase_reset.py',")
        # The memory runner uses a different source-list layout.
        if suffix=='memory':text=once(text,"[source,'tools/run_distributed_load_memory.py'","["+extra+"source,'tools/run_distributed_load_memory.py'")
        (ROOT/dest).write_text('# GENERATED NET30 separate candidate; no qualification inherited.\n'+text);paths.extend([source,dest])
    target=ROOT/'verification/net30/adapter-origin.json'
    target.write_text(json.dumps({'date':'2026-11-26','scope':'NET30 separate candidate projections; identical binary reset boundaries/guards, new native data buffers. Original NET26 files and live NET27 inputs untouched.',
        'files':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths]},indent=2)+'\n')

if __name__=='__main__':main()
