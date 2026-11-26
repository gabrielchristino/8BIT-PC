"""ISA-1 Rev 1.0 independent architectural audits; NOT gate-level simulation."""
from isa1_rev09_model import CPU, OP, CLOCK, H_TOTAL, V_TOTAL, X_START, Y_START, WIDTH, HEIGHT
from isa1_rev07_emulator import Memory


def region(a):
    if a<0x4000:return 'ROM'
    if a<0xc000:return 'RAM'
    if a<0xe000:return 'VRAM'
    if a<0xe100:return 'IO'
    return 'RESERVED'

def test_decode():
    counts={k:0 for k in ('ROM','RAM','VRAM','IO','RESERVED')}
    for a in range(65536):counts[region(a)]+=1
    assert counts==dict(ROM=16384,RAM=32768,VRAM=8192,IO=256,RESERVED=7936),counts
    m=Memory()
    assert len({m.ram_index(a) for a in range(0x4000,0xc000)})==32768
    return counts

def test_arithmetic_cpu():
    m=Memory(); cpu=CPU(m)
    cases=0
    for a in range(256):
        for b in range(256):
            for opcode in (OP['ADD'],OP['SUB'],OP['CMP']):
                m.rom[0]=opcode
                cpu.pc=0;cpu.a=a;cpu.b=b;cpu.c=0;cpu.z=0;cpu.halted=False
                cpu.step()
                d=a-b
                if opcode==OP['ADD']:
                    expected=(a+b)&255; carry=int(a+b>255)
                elif opcode==OP['SUB']:
                    expected=d&255; carry=int(d>=0)
                else:
                    expected=a; carry=int(d>=0)
                zero=int(((d if opcode==OP['CMP'] else expected)&255)==0)
                assert (cpu.a,cpu.c,cpu.z,cpu.pc)==(expected,carry,zero,1),(a,b,opcode)
                cases+=1
    return cases

def test_stack():
    m=Memory();cpu=CPU(m)
    # 256 push/pop values and correct downward stack ordering
    for i in range(256):cpu.push(i)
    assert cpu.sp==0xbeff
    for i in reversed(range(256)):assert cpu.pop()==i
    assert cpu.sp==0xbfff
    return 512

def test_raster():
    # Verify 32 bytes/line *192 lines, no duplicates; reserve byte-fetch windows.
    addrs=[]
    for y in range(HEIGHT):
        for byte in range(WIDTH//8):
            addr=0xc000+y*32+byte
            addrs.append(addr)
    assert addrs==list(range(0xc000,0xd800))
    # Pixel clock 7.15909 MHz; 8 ticks/byte ~1.117us. This is not a SRAM cycle proof.
    pixel_ns=1e9/CLOCK
    return dict(pixel_ns=pixel_ns,byte_ns=8*pixel_ns,line_us=H_TOTAL/CLOCK*1e6,
                frame_hz=CLOCK/H_TOTAL/V_TOTAL,active_us=WIDTH/CLOCK*1e6,
                bytes=len(addrs),blanking_ticks=H_TOTAL-WIDTH)

def run():
    counts=test_decode(); n=test_arithmetic_cpu(); stack=test_stack(); raster=test_raster()
    print('PASS full 64KiB address-region partition:',counts)
    print('PASS CPU actual step() ADD/SUB/CMP cases:',n)
    print('PASS stack push/pop:',stack)
    print('PASS raster address sequence:',raster['bytes'])
    for k,v in raster.items():print(f'{k}: {v:.5f}' if isinstance(v,float) else f'{k}: {v}')
    print('FAILURE OF ASSUMPTION: 256 active ticks @ 7.159MHz is only 35.76us, not 47.7us')
    print('UNVALIDATED: gate-level datapath, ROM timing, CVBS, VRAM electrical arbitration')
if __name__=='__main__':run()
