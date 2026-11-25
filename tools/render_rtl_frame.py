"""Render verified raster samples at 4x horizontal scale (640x480 preview)."""
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT/"verification/rtl01"
    frame = (folder/"frame.ppm").read_bytes()
    header = b"P6\n160 480\n255\n"
    assert frame.startswith(header) and len(frame) == len(header)+160*480*3
    pixels = frame[len(header):]
    rows = []
    for y in range(480):
        line = pixels[y*480:(y+1)*480]
        rows.append(b"\x00"+b"".join(line[i:i+3]*4 for i in range(0,480,3)))
    def chunk(kind, data):
        return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data)&0xffffffff)
    png = b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",640,480,8,2,0,0,0))
    png += chunk(b"IDAT",zlib.compress(b"".join(rows)))+chunk(b"IEND",b"")
    (folder/"frame-display.png").write_bytes(png)
    print("Rendered 160x480 raster samples as a 640x480 display preview")


if __name__ == "__main__":
    main()
