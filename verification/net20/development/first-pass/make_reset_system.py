"""Separate NET20 reset-domain integration; predecessor bytes remain intact."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('Unexpected predecessor: ' + old)
    return text.replace(old, new)


def main():
    source = ROOT / 'sim/net19a/isa1_memory_system.sv'
    text = source.read_text()
    text = once(text, 'CONTROL_EARLY=0)', 'CONTROL_EARLY=0,RESET_POLICY=1)')
    text = once(text, 'wire safe=reset_n && power_good;', '''wire raw_safe=reset_n && power_good;
 wire bank_memory_n,bank_keyboard_n,bank_decode_n,safe_memory,safe_keyboard;
 wire cpu_core_clk,cpu_reset_n,access_clk,keyboard_clk,bank_reset_n,safe;
 system_reset_netlist #(.TIMED(TIMED),.RESOLVE_LATE(RESET_POLICY),
   .ASSERT_DELAY(TIMED?19000:1),.RELEASE_DELAY(TIMED?42000:4)) reset_domains(
   raw_safe,backend_clk,clk,bank_reset_n,cpu_reset_n,safe,
   bank_memory_n,bank_keyboard_n,bank_decode_n,safe_memory,safe_keyboard,
   cpu_core_clk,access_clk,keyboard_clk);''')
    text = once(text, 'vb,1\'b1,safe,select', 'vb,1\'b1,bank_decode_n,select')
    text = once(text, '.clk(backend_clk),.reset_n(reset_n),.power_good(power_good)',
                ".clk(access_clk),.reset_n(bank_memory_n),.power_good(1'b1)")
    text = once(text, '.reset_n(reset_n),.power_good(power_good),.vram_owner',
                '.reset_n(bank_memory_n),.power_good(safe_memory),.vram_owner')
    text = once(text, 'backend_clk,safe,safe,io_commit',
                'keyboard_clk,bank_keyboard_n,safe_keyboard,io_commit')
    # Only already-declared asynchronous synchronizers receive the binary policy.
    text = once(text, 'integer i;', '''integer i;
 defparam raster.RESOLVE_LATE=RESET_POLICY;
 defparam peripheral.RESOLVE_LATE=RESET_POLICY;''')
    destination = ROOT / 'sim/net20/isa1_memory_reset.sv'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text)
    out = ROOT / 'verification/net20'
    out.mkdir(parents=True, exist_ok=True)
    paths = [Path(__file__), source, destination]
    (out / 'adapter-origin.json').write_text(json.dumps({
        'date': '2026-11-26',
        'transformation': 'Separate native reset and clock distribution. CPU peer must use cpu_core_clk/cpu_reset_n. SRAM payload registers retain state across fast CPU clear; memory-affecting state uses delayed bank reset. RAW is a qualified external supervisor forcepoint, not an analog model. Ideal RC delays are scaled to 1/4 ns; timed 19/42 us.',
        'files': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
        'supervisor_output_load_qualified': False,
        'production_released': False}, indent=2) + '\n')
    print('Generated separate reset-domain system adapter')


if __name__ == '__main__':
    main()
