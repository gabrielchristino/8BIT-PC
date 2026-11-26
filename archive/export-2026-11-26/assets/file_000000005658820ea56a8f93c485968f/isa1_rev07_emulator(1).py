"""ISA-1 Rev 0.7: functional reference model, NOT gate-level hardware simulation."""
from dataclasses import dataclass

ROM_START, RAM_START, VRAM_START, IO_START = 0x0000, 0x4000, 0xC000, 0xE000
ROM_END, RAM_END, VRAM_END, IO_END = 0x3FFF, 0xBFFF, 0xDFFF, 0xE0FF

class Memory:
    def __init__(self):
        self.rom = bytearray(0x4000)
        self.ram = bytearray(0x8000)
        self.vram = bytearray(0x2000)
        self.io = bytearray(0x100)
    def ram_index(self, address):
        assert RAM_START <= address <= RAM_END
        # SRAM A0..A13 = CPU A0..A13, SRAM A14 = CPU A15
        return (address & 0x3fff) | ((address & 0x8000) >> 1)
    def read(self, a):
        a &= 0xffff
        if a <= ROM_END: return self.rom[a]
        if a <= RAM_END: return self.ram[self.ram_index(a)]
        if a <= VRAM_END: return self.vram[a - VRAM_START]
        if a <= IO_END: return self.io[a - IO_START]
        return 0xff
    def write(self, a, v):
        a &= 0xffff; v &= 0xff
        if a <= ROM_END: return # ROM is read-only in normal CPU execution
        if a <= RAM_END: self.ram[self.ram_index(a)] = v
        elif a <= VRAM_END: self.vram[a - VRAM_START] = v
        elif a <= IO_END: self.io[a - IO_START] = v
    def pixel(self, x, y, on=True):
        assert 0 <= x < 256 and 0 <= y < 192
        addr = 0xc000 + y * 32 + (x >> 3)
        bit = 0x80 >> (x & 7)
        v = self.read(addr)
        self.write(addr, (v | bit) if on else (v & ~bit))

# PROVISIONAL software ISA. No assertion of a completed 74HC datapath or microcode.
OP = {'NOP':0x00,'LDA_IMM':0x10,'LDB_IMM':0x11,'ADD':0x20,'SUB':0x21,
      'AND':0x22,'OR':0x23,'XOR':0x24,'SHL':0x25,'SHR':0x26,
      'LDA_ABS':0x30,'STA_ABS':0x31,'JMP':0x40,'JZ':0x41,
      'CALL':0x50,'RET':0x51,'PUSH_A':0x52,'POP_A':0x53,'HALT':0xff}

@dataclass
class CPU:
    mem: Memory
    pc: int = 0
    sp: int = 0xbfff
    a: int = 0
    b: int = 0
    z: int = 0
    c: int = 0
    halted: bool = False
    def fetch(self):
        v = self.mem.read(self.pc); self.pc = (self.pc + 1) & 0xffff; return v
    def word(self):
        lo = self.fetch(); return lo | (self.fetch() << 8)
    def push(self, v):
        if not 0x4000 <= self.sp <= 0xbfff: raise RuntimeError('stack outside RAM')
        self.mem.write(self.sp, v); self.sp = (self.sp - 1) & 0xffff
    def pop(self):
        self.sp = (self.sp + 1) & 0xffff
        if not 0x4000 <= self.sp <= 0xbfff: raise RuntimeError('stack outside RAM')
        return self.mem.read(self.sp)
    def set_a(self, v):
        self.a = v & 0xff; self.z = int(self.a == 0)
    def step(self):
        if self.halted: return
        op = self.fetch()
        if op == OP['NOP']: pass
        elif op == OP['LDA_IMM']: self.set_a(self.fetch())
        elif op == OP['LDB_IMM']: self.b = self.fetch()
        elif op == OP['ADD']:
            v = self.a + self.b; self.c = int(v > 255); self.set_a(v)
        elif op == OP['SUB']:
            v = self.a - self.b; self.c = int(v >= 0); self.set_a(v)
        elif op == OP['AND']: self.set_a(self.a & self.b)
        elif op == OP['OR']: self.set_a(self.a | self.b)
        elif op == OP['XOR']: self.set_a(self.a ^ self.b)
        elif op == OP['SHL']:
            self.c = (self.a >> 7) & 1; self.set_a(self.a << 1)
        elif op == OP['SHR']:
            self.c = self.a & 1; self.set_a(self.a >> 1)
        elif op == OP['LDA_ABS']: self.set_a(self.mem.read(self.word()))
        elif op == OP['STA_ABS']: self.mem.write(self.word(), self.a)
        elif op == OP['JMP']: self.pc = self.word()
        elif op == OP['JZ']:
            target = self.word()
            if self.z: self.pc = target
        elif op == OP['CALL']:
            target = self.word(); self.push((self.pc >> 8) & 255); self.push(self.pc & 255); self.pc = target
        elif op == OP['RET']: self.pc = self.pop() | (self.pop() << 8)
        elif op == OP['PUSH_A']: self.push(self.a)
        elif op == OP['POP_A']: self.set_a(self.pop())
        elif op == OP['HALT']: self.halted = True
        else: raise RuntimeError(f'unknown opcode {op:02X} at {self.pc-1:04X}')
    def run(self, limit=10000):
        for i in range(limit):
            if self.halted: return i
            self.step()
        raise RuntimeError('instruction limit reached')

def test():
    m = Memory()
    addresses = [m.ram_index(a) for a in range(0x4000,0xc000)]
    assert len(set(addresses)) == 32768
    assert addresses[0] == 0 and addresses[-1] == 32767
    assert all(m.ram_index(a) == a-0x4000 for a in range(0x4000,0xc000))
    for a in range(0x4000,0xc000): m.write(a, (a ^ (a>>8)) & 255)
    for a in range(0x4000,0xc000): assert m.read(a) == ((a ^ (a>>8)) & 255)
    assert all(m.read(a)==0 for a in range(0xc000,0xe000))
    # Full frame address coverage and bit packing
    touched = {0xc000+y*32+(x>>3) for y in range(192) for x in range(256)}
    assert len(touched) == 6144 and min(touched) == 0xc000 and max(touched) == 0xd7ff
    for y in range(192):
        for x in range(256): m.pixel(x,y)
    assert all(v == 255 for v in m.vram[:6144])
    assert all(v == 0 for v in m.vram[6144:])
    for y in range(192):
        for x in range(256): m.pixel(x,y,False)
    assert all(v == 0 for v in m.vram)
    # ROM program: A=10, B=20, add, write 0x4000, call subroutine at 0x0010;
    # subroutine sets A=0x81, shifts left -> 0x02 and returns, then HALT
    program = [0x10,10,0x11,20,0x20,0x31,0x00,0x40,0x50,0x10,0x00,0xff]
    m.rom[:len(program)] = bytes(program)
    m.rom[0x10:0x14] = bytes([0x10,0x81,0x25,0x51])
    cpu = CPU(m); n = cpu.run()
    assert m.read(0x4000) == 30
    assert cpu.a == 2 and cpu.c == 1 and cpu.pc == 12 and cpu.sp == 0xbfff
    assert cpu.halted
    # conditional jump and push/pop regression
    nmem = Memory(); nmem.rom[:13] = bytes([0x10,0,0x41,0x07,0,0x10,99,0x10,42,0x52,0x10,0,0x53])
    nmem.rom[13] = 0xff
    ncpu=CPU(nmem); ncpu.run(); assert ncpu.a == 42 and ncpu.sp == 0xbfff
    print('PASS: RAM 32768 unique mapped bytes, read/write roundtrip')
    print('PASS: framebuffer 256x192 pixels, 6144 unique bytes, set/clear all')
    print('PASS: CPU provisional ISA: arithmetic, RAM write, CALL/RET, shift, carry')
    print('PASS: CPU provisional ISA: JZ, PUSH/POP, stack restoration')
    print('NOT TESTED: gate-level logic, microcode, CVBS timing, VRAM arbitration, electrical pinout')
if __name__ == '__main__': test()
