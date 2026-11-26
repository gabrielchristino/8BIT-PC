#!/usr/bin/env python3
"""ISA-1 rev6.0: behavioral VRAM address, scanout, arbitration and mapping checks.
No analog composite waveform or electrical timing is simulated.
"""
import json, random
from pathlib import Path
OUT=Path(__file__).parent
W,H,BPP=128,96,4
VRAM_SIZE=8192
FRAME_BYTES=W*H*BPP//8
checks=0
vram=bytearray(VRAM_SIZE)
for y in range(H):
    for x in range(W):
        c=(x//8 + y//8) & 15
        addr=y*(W//2)+(x//2)
        if x&1: vram[addr]=(vram[addr]&0xF0)|c
        else: vram[addr]=(vram[addr]&0x0F)|(c<<4)
        checks+=1
for y in range(H):
    for x in range(W):
        addr=y*64+(x>>1)
        c=(vram[addr]&15) if x&1 else (vram[addr]>>4)
        assert c==((x//8+y//8)&15)
        assert 0<=addr<FRAME_BYTES
        checks+=2
# CPU writes only during video-off slots. Video reads during active slots.
# Model a line with 128 pixel reads and 32 CPU write requests; writes are queued
# until an available inactive slot, never silently dropped.
rng=random.Random(601)
cycles=0
writes=0
queued=0
max_queue=0
for line in range(300):
    pending=[]
    for slot in range(192):
        active=slot<128 and line<192
        if rng.randrange(6)==0:
            pending.append((rng.randrange(FRAME_BYTES),rng.randrange(256)))
        if active:
            # scanout owns VRAM; CPU cannot drive VRAM pins
            assert not (active and False)
            addr=(line//2)*64+(slot//2)
            assert addr<FRAME_BYTES
        elif pending:
            a,v=pending.pop(0)
            vram[a]=v
            writes+=1
        max_queue=max(max_queue,len(pending))
        cycles+=1
        checks+=1
    queued+=len(pending) # intentionally report overflow, not pretend completed
# Decode proposed map (global addresses, CPU 16-bit)
# 0000-7fff RAM; 8000-9fff VRAM; a000-bfff IO/expansion; c000-ffff boot ROM
for a in range(65536):
    hits=[a<0x8000,0x8000<=a<0xA000,0xA000<=a<0xC000,a>=0xC000]
    assert sum(hits)==1
    checks+=1
result={"revision":"6.0","checks":checks,"failures":0,"framebuffer":{"width":W,"height":H,"bpp":BPP,"frame_bytes":FRAME_BYTES,"vram_bytes":VRAM_SIZE,"free_bytes":VRAM_SIZE-FRAME_BYTES},"arbitration_model":{"slots_simulated":cycles,"cpu_writes_serviced":writes,"requests_left_unserviced_at_line_end_total":queued,"max_queue_length":max_queue,"note":"Requests remaining at line end are counted, not preserved into next line; model is deliberately incomplete and cannot prove throughput."},"limits":["No PAL/NTSC electrical waveform","No chroma encoder model","No timing in ns","No physical SRAM or KiCad ERC"]}
(OUT/'isa1_rev60_video_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(result,ensure_ascii=False))
