"""NET19A: replace the last behavioral MMIO with existing native pin leaves.

Reset remains the predecessor global stimulus here. NET18 analog power domains
are not silently claimed integrated by connecting the keyboard.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification/net19a'


def once(s, old, new):
    if s.count(old) != 1:
        raise ValueError('Unexpected predecessor: ' + old[:90])
    return s.replace(old, new)


def main():
    base = ROOT / 'sim/net14c/isa1_memory_video.sv'
    text = base.read_text()
    text = once(text, 'MMIO remains a model; raster/slot/capture are native pin netlists.',
                'MMIO/keyboard/controller and raster/slot/capture are native pin netlists; switch contacts are ideal functional stimuli.')
    text = once(text, 'output reg boot,output reg [1:0] vb,row,output reg eb,',
                'output wire boot,output wire [1:0] vb,row,output wire eb,')
    text = once(text, 'wire vram_slot;reg [7:0] io_value;reg [15:0] cols;',
                'wire vram_slot,key_ready;wire [7:0] io_value;tri [3:0] row_wires;tri [15:0] column_wires;')
    text = once(text, 'memory_access_netlist #(.TIMED(TIMED)) access_controller(',
                'keyboard_access_netlist #(.TIMED(TIMED)) access_controller(')
    text = once(text, '.vram_slot(vram_slot),',
                '.vram_slot(vram_slot),.key_ready(key_ready),.io_col_lo(io_select[4]),.io_col_hi(io_select[5]),')
    start = text.index(' function [15:0] columns;')
    end = text.index(' always @(posedge acknowledge)', start)
    text = text[:start] + ''' // Actual sampled columns and MMIO state come ONLY from the pin netlist.
 keyboard_500_netlist #(.TIMED(TIMED)) peripheral(
   backend_clk,safe,safe,io_commit,io_select,saved_data,row_wires,column_wires,
   boot,eb,vb,row,io_value,key_ready);
 genvar rr,cc;
 generate for(rr=0;rr<4;rr=rr+1)begin:MEMBRANE_ROW
   for(cc=0;cc<16;cc=cc+1)begin:MEMBRANE_COLUMN
     tranif1 contact(row_wires[rr],column_wires[cc],keys[rr*16+cc]);
   end
 end endgenerate
 always @(posedge backend_clk)if(safe && vram_owner && h<160)
   $fatal(1,"CPU owns VRAM during active video");
''' + text[end:]
    destination = ROOT / 'sim/net19a/isa1_memory_keyboard.sv'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text)
    OUT.mkdir(parents=True, exist_ok=True)
    sources = [base, Path(__file__), destination]
    (OUT / 'adapter-origin.json').write_text(json.dumps({'date': '2026-11-26',
        'transformation': 'Separate NET14C memory adapter replaces behavioral MMIO/column closure with NET17 keyboard pins, actual sampled columns/quiet timer, NET15 extended controller and ideal intact contact switches. Existing reset stimulus retained; analog power domains not integrated.',
        'files': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]}, indent=2) + '\n')
    print('Generated separate pin-keyboard CPU/raster adapter')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
