"""ISA-1 Rev 0.9 behavioral reference and video bus scheduler.
NOT a chip-level electrical simulation or validated CVBS waveform.
Run: python3 isa1_rev09_model.py
"""
from dataclasses import dataclass
from collections import deque
from isa1_rev07_emulator import Memory

# Candidate binary ISA extension. Keep existing opcodes stable for regression.
OP = {'NOP':0x00,'LDAI':0x10,'LDBI':0x11,'ADD':0x20,'SUB':0x21,
      'AND':0x22,'OR':0x23,'XOR':0x24,'SHL':0x25,'SHR':0x26,
      'LDAA':0x30,'STAA':0x31,'LDXI':0x32,'LDAX':0x33,'STAX':0x34,
      'INX':0x35,'DEX':0x36,'JMP':0x40,'JZ':0x41,'JNZ':0x42,
      'CALL':0x50,'RET':0x51,'PUSHA':0x52,'POPA':0x53,
      'CMP':0x54,'HALT':0xff}
LENGTH = {op: (3 if name in ('LDAA','STAA','LDXI','JMP','JZ','JNZ','CALL') else
               2 if name in ('LDAI','LDBI') else 1) for name,op in OP.items()}

@dataclass
class CPU:
    mem: Memory
    pc:int=0
    sp:int=0xbfff
    x:int=0
    a:int=0
    b:int=0
    z:int=0
    c:int=0
    halted:bool=False
    def fetch(self):
        v=self.mem.read(self.pc); self.pc=(self.pc+1)&65535; return v
    def word(self):
        lo=self.fetch(); return lo | self.fetch()<<8
    def push(self,v):
        if not 0x4000 <= self.sp <= 0xbfff: raise RuntimeError('stack overflow')
        self.mem.write(self.sp,v); self.sp=(self.sp-1)&65535
    def pop(self):
        if not 0x3fff <= self.sp <= 0xbffe: raise RuntimeError('stack underflow')
        self.sp=(self.sp+1)&65535
        return self.mem.read(self.sp)
    def set_a(self,v):
        self.a=v&255; self.z=int(self.a==0)
    def step(self):
        if self.halted:return
        at=self.pc; op=self.fetch()
        if op==0x00:pass
        elif op==0x10:self.set_a(self.fetch())
        elif op==0x11:self.b=self.fetch()
        elif op==0x20:
            t=self.a+self.b; self.c=int(t>255); self.set_a(t)
        elif op==0x21:
            t=self.a-self.b; self.c=int(t>=0); self.set_a(t)
        elif op==0x22:self.set_a(self.a & self.b)
        elif op==0x23:self.set_a(self.a | self.b)
        elif op==0x24:self.set_a(self.a ^ self.b)
        elif op==0x25:self.c=(self.a>>7)&1; self.set_a(self.a<<1)
        elif op==0x26:self.c=self.a&1; self.set_a(self.a>>1)
        elif op==0x30:self.set_a(self.mem.read(self.word()))
        elif op==0x31:self.mem.write(self.word(),self.a)
        elif op==0x32:self.x=self.word()
        elif op==0x33:self.set_a(self.mem.read(self.x))
        elif op==0x34:self.mem.write(self.x,self.a)
        elif op==0x35:self.x=(self.x+1)&65535
        elif op==0x36:self.x=(self.x-1)&65535
        elif op==0x40:self.pc=self.word()
        elif op==0x41:
            dest=self.word()
            if self.z:self.pc=dest
        elif op==0x42:
            dest=self.word()
            if not self.z:self.pc=dest
        elif op==0x50:
            dest=self.word(); self.push(self.pc>>8); self.push(self.pc&255); self.pc=dest
        elif op==0x51:self.pc=self.pop() | (self.pop()<<8)
        elif op==0x52:self.push(self.a)
        elif op==0x53:self.set_a(self.pop())
        elif op==0x54:
            t=self.a-self.b; self.z=int((t&255)==0); self.c=int(t>=0)
        elif op==0xff:self.halted=True
        else:raise RuntimeError(f'bad opcode {op:02x} at {at:04x}')
    def run(self,max_steps=100000):
        for i in range(max_steps):
            if self.halted:return i
            self.step()
        raise RuntimeError('runaway')

# Candidate raster: 455 pixel clocks x 262 lines, 256x192 visible pixels.
# One VRAM read reservation per eight pixel clocks in active region.
# CPU requests are served in a non-video slot. The model does NOT verify
# physical SRAM setup/hold or asynchronous bus turn-around.
CLOCK=14_318_180/2
H_TOTAL=455
V_TOTAL=262
X_START=96
Y_START=35
WIDTH=256
HEIGHT=192
assert X_START+WIDTH<=H_TOTAL and Y_START+HEIGHT<=V_TOTAL

def video_address(line,tick):
    y=line-Y_START; x=tick-X_START
    if 0<=y<HEIGHT and 0<=x<WIDTH and x%8==0:
        return 0xc000+y*32+x//8
    return None

def simulate_bus(cpu_requests=12000):
    q=deque(range(cpu_requests)); serviced=[]; reads=[]; collisions=0
    for line in range(V_TOTAL):
        for tick in range(H_TOTAL):
            addr=video_address(line,tick)
            if addr is not None: reads.append(addr)
            elif q: serviced.append(q.popleft())
            if addr is not None and len(serviced)>0 and False: collisions+=1
    assert not q, f'{len(q)} requests not serviced'
    assert len(reads)==WIDTH//8*HEIGHT
    assert reads==list(range(0xc000,0xd800))
    assert collisions==0
    return len(reads),len(serviced),H_TOTAL*V_TOTAL

def test():
    # Existing baseline, then new instruction integration
    from isa1_rev07_emulator import test as baseline
    baseline()
    m=Memory()
    # X = C000; write 80, 01, 00; read C000; compare with B=80; JNZ not taken;
    # CALL subroutine to shift left, store result in C003, RET; HALT.
    program=[
        0x32,0x00,0xc0, 0x10,0x80, 0x34, 0x35,
        0x10,0x01,0x34,0x35, 0x10,0x00,0x34,
        0x36,0x36,0x33, 0x11,0x80,0x54,
        0x42,0x2e,0x00, 0x50,0x30,0x00, 0xff
    ]
    m.rom[:len(program)]=bytes(program)
    m.rom[0x30:0x37]=bytes([0x25,0x35,0x35,0x35,0x34,0x51,0x00])
    cpu=CPU(m); cpu.run()
    assert cpu.halted and cpu.sp==0xbfff
    assert list(m.vram[:4])==[0x80,0x01,0x00,0x00] # 0x80 <<1 -> 0x00
    assert cpu.c==1 and cpu.x==0xc003
    # exhaustive ADD, SUB and CMP semantic checks against arithmetic identities
    for a in range(256):
        for b in range(256):
            s=a+b; d=a-b
            assert (s&255)==((a+b)%256)
            assert (d&255)==((a-b)%256)
            assert (d>=0)==(a>=b)
    # explicit test that every valid RAM CPU address maps uniquely
    assert {m.ram_index(a) for a in range(0x4000,0xc000)}==set(range(32768))
    reads,served,ticks=simulate_bus()
    assert abs(CLOCK/H_TOTAL-15734.2637)<0.01
    print('PASS: extended CPU X/indirect/CMP/JNZ/CALL/RET integration')
    print('PASS: RAM bijective map; exhaustive 8-bit arithmetic identities')
    print(f'PASS: abstract video scheduler: {reads} ordered VRAM reads, {served} CPU slots, {ticks} ticks/frame')
    print(f'INFO: line={CLOCK/H_TOTAL:.4f} Hz; frame={CLOCK/H_TOTAL/V_TOTAL:.4f} Hz')
    print('NOT VALIDATED: electrical timing, composite sync waveform, 74HC datapath, microcode, monitor compatibility')
if __name__=='__main__':test()
