#!/usr/bin/env python3
"""ISA-1 rev 2.3: abstract EEPROM image and torn-write recovery tests.
Not an electrical/timing simulation or hardware EEPROM driver.
"""
import json, struct, zlib
from pathlib import Path
SIZE=32768
HEADER=64
SLOT=1024
SAVE_A=SIZE-2*SLOT
SAVE_B=SIZE-SLOT
CODE_START=HEADER
CODE_END=SAVE_A
MAGIC=b'ISA1'
# 32-byte record: marker, generation, payload length, CRC32, reserved
RECORD_HEADER=16

def crc(data): return zlib.crc32(data)&0xffffffff

def encode_record(generation, payload):
    assert len(payload)<=SLOT-RECORD_HEADER
    head=struct.pack('<4sIII',b'SAVE',generation,len(payload),crc(payload))
    return head+payload+b'\xff'*(SLOT-len(head)-len(payload))

def decode_record(slot):
    if len(slot)!=SLOT: return None
    magic,gen,n,checksum=struct.unpack('<4sIII',slot[:RECORD_HEADER])
    if magic!=b'SAVE' or n>SLOT-RECORD_HEADER: return None
    payload=slot[RECORD_HEADER:RECORD_HEADER+n]
    if crc(payload)!=checksum: return None
    return (gen,payload)

def recover(mem):
    valid=[]
    for pos in (SAVE_A,SAVE_B):
        item=decode_record(mem[pos:pos+SLOT])
        if item is not None: valid.append((item[0],item[1],pos))
    return max(valid,key=lambda x:x[0]) if valid else None

def make_image(code):
    assert 0<len(code)<=CODE_END-CODE_START
    mem=bytearray([0xff])*SIZE
    mem[:4]=MAGIC
    struct.pack_into('<HHI',mem,4,CODE_START,len(code),crc(code))
    mem[CODE_START:CODE_START+len(code)]=code
    return mem

def validate_code(mem):
    if mem[:4]!=MAGIC: return False
    off,n,c=struct.unpack_from('<HHI',mem,4)
    return off==CODE_START and 0<n<=CODE_END-CODE_START and crc(mem[off:off+n])==c

def main():
    code=bytes((i*17+3)%256 for i in range(4096))
    original=make_image(code)
    assert validate_code(original)
    assert CODE_END-CODE_START==30656
    old=encode_record(7,b'old progress')
    new=encode_record(8,b'new progress')
    original[SAVE_A:SAVE_A+SLOT]=old
    assert recover(original)[:2]==(7,b'old progress')
    # Power loss while updating the inactive slot: each possible byte cutoff.
    # The old valid slot must remain recoverable. If the new slot is fully valid,
    # it may be selected. For an arbitrary torn write, CRC may accidentally pass;
    # this is not a formal guarantee against adversarial corruption.
    cutoffs=0
    for n in range(SLOT+1):
        mem=bytearray(original)
        mem[SAVE_B:SAVE_B+n]=new[:n]
        rec=recover(mem)
        assert rec is not None and rec[:2] in ((7,b'old progress'),(8,b'new progress'))
        assert validate_code(mem)
        cutoffs+=1
    # Updating a previously occupied slot cannot safely be modeled as a simple
    # prefix overwrite: header-first can temporarily validate stale data with
    # a new generation. Explicitly invalidate the slot marker first, then
    # write the body, then commit the marker last.
    mem=bytearray(original)
    mem[SAVE_B:SAVE_B+SLOT]=new
    assert recover(mem)[:2]==(8,b'new progress')
    nextrec=encode_record(9,b'level three')
    operations=[(SAVE_A+i,0xff) for i in range(4)] + [(SAVE_A+i,nextrec[i]) for i in range(4,SLOT)] + [(SAVE_A+i,nextrec[i]) for i in range(4)]
    torn=bytearray(mem)
    for addr,value in operations:
        torn[addr]=value
        rec=recover(torn)
        assert rec is not None and rec[:2] in ((8,b'new progress'),(9,b'level three'))
        assert validate_code(torn)
        cutoffs+=1
    assert recover(torn)[:2]==(9,b'level three')
    # Header and payload damage must be detected (for these tested bit flips).
    flips=0
    for i in range(RECORD_HEADER,RECORD_HEADER+len(b'old progress')):
        torn=bytearray(old); torn[i]^=1
        assert decode_record(torn) is None
        flips+=1
    # Overlong program rejected.
    try: make_image(bytes(CODE_END-CODE_START+1))
    except AssertionError: pass
    else: raise AssertionError('oversized code accepted')
    result={'model':'abstract image format, no physical EEPROM emulation','eeprom_bytes':SIZE,'header_bytes':HEADER,'program_max_bytes':CODE_END-CODE_START,'save_slot_bytes':SLOT,'save_payload_max_bytes':SLOT-RECORD_HEADER,'power_cut_prefix_cases':cutoffs,'corrupted_payload_cases':flips,'checks':'passed','limitations':['byte-prefix tear model, not actual EEPROM write semantics','CRC32 detects typical corruption, not guaranteed','generation wraparound not implemented','real AT28C256 page write, polling, endurance, write-protection and pinout unverified']}
    Path(__file__).with_name('isa1_rev23_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
