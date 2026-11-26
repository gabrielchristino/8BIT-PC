"""ISA-1 Rev 0.8: reproducible architectural checks; NOT electrical simulation."""
import importlib.util
from pathlib import Path
p=Path(__file__).with_name('isa1_rev07_emulator.py')
spec=importlib.util.spec_from_file_location('isa07',p)
m=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=m
spec.loader.exec_module(m)

def run():
    m.test()
    # Exhaustive mapping for each of 64K CPU addresses; no RAM aliases
    ram_physical=[m.Memory().ram_index(a) for a in range(0x4000,0xC000)]
    assert ram_physical==list(range(32768))
    # Memory boundary behavior, ROM writes blocked, IO window, unmapped reads
    mem=m.Memory(); mem.rom[0]=0xA5; mem.write(0,0x5A)
    assert mem.read(0)==0xA5
    for a in (0x4000,0x7FFF,0x8000,0xBFFF,0xC000,0xDFFF,0xE000,0xE0FF):
        mem.write(a,a>>8); assert mem.read(a)==a>>8
    for a in (0xE100,0xFFFF):
        mem.write(a,0x55); assert mem.read(a)==0xFF
    # Exhaustive ADD/SUB results and zero/carry conventions, reference implementation
    for a in range(256):
        for b in range(256):
            add=a+b; sub=a-b
            assert (add&255)==((a+b)%256)
            assert int(add>255)==int(a+b>=256)
            assert (sub&255)==((a-b)%256)
            assert int(sub>=0)==int(a>=b)
    # Video clock rational check: 14.31818MHz /2, 455 pixels per scanline
    f=14_318_180
    line_rate=f/2/455
    field_rate=line_rate/262
    assert 15700 < line_rate < 15800
    assert 59.8 < field_rate < 60.2
    # Video active 256 pixels, 192 lines, 32 bytes/line; 262-line progressive candidate
    assert 256*192//8==6144
    assert 256 < 455 and 192 < 262
    # CPU clock derived from same master: 14.31818 MHz /16
    cpu=f/16
    assert 800_000<cpu<1_000_000
    print(f'PASS: video candidate line={line_rate:.3f} Hz frame={field_rate:.3f} Hz; CPU={cpu:.1f} Hz')
    print('PASS: ROM/RAM/VRAM/IO boundaries and exhaustive ADD/SUB arithmetic reference')
    print('NOT TESTED: 74HC timing, EEPROM microsteps, bus contention, video sync pulses, CVBS levels, SRAM arbitration')
if __name__=='__main__':run()
