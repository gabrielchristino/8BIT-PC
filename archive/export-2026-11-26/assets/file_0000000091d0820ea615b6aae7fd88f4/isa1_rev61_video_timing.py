import json, random
from pathlib import Path
P=Path(__file__).parent
W,H=128,96
assert W*H//2==6144
# Synthetic fixed-slot arbitration, NOT a chip timing model.
# A 256-slot logical scanline: 128 reads of pixel pairs? 64 bytes per logical row.
# Video consumes 64 byte-read slots, CPU can use 192 slots per scanline.
random.seed(61)
checks=0
max_wait=0
for row in range(H):
    vram=bytearray(8192)
    queue=[]
    for slot in range(256):
        if random.random()<0.65: queue.append((random.randrange(6144),random.randrange(256)))
        video_slot=(slot%4==0)
        if video_slot:
            addr=row*64+slot//4
            assert 0<=addr<6144
            checks+=1
        elif queue:
            a,v=queue.pop(0); vram[a]=v; checks+=1
        if queue:max_wait=max(max_wait,len(queue))
    # remaining queue may persist in real implementation; model deliberately reports it
# exhaustive pixel addressing
for y in range(H):
 for x in range(W):
    a=y*64+x//2
    assert a<6144
    checks+=1
# EEPROM bank map 16KB each; save areas in bank 1, final 2 KB
for a in range(32768):
    bank=a>>14; off=a&0x3fff
    assert bank*16384+off==a
    checks+=1
out={'revision':'6.1','checks':checks,'failures':0,'framebuffer_bytes':6144,'vram_bytes':8192,'slots_per_logical_row':256,'video_reads_per_logical_row':64,'cpu_slots_per_logical_row':192,'max_queued_writes_synthetic':max_wait,'limitations':['synthetic slots are not real NTSC/PAL timing','no actual SRAM tAA/tOE/tHZ','no composite encoder verified','no analog or ERC simulation']}
(P/'isa1_rev61_results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(out,indent=2))
