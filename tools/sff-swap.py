#!/usr/bin/env python3
"""Append-swap one sprite in an SFF v2 file (IKEMEN GO / MUGEN).

Usage: sff-swap.py <sff> <group> <number> <png> [--dry-run]
- Finds the (group, number) node, reads its 4-byte data prefix (the engine
  skips the first 4 bytes of a PNG sprite's data), appends
  [prefix + png bytes] at EOF, and updates the node's dataOfs/dataLen/w/h/fmt.
- fmt is set to 12 (truecolor PNG) since the replacement is an RGB PNG.
- tofs is moved to the new EOF (the tofs block was empty; keep it empty).
- The old sprite data stays orphaned in the file (unreferenced, harmless).
Layout (from repos/mugen-studio/app/sffaudit.js):
  header: sprOfs@36, sprNum@40, lofs@52, tofs@60 (all u32 LE)
  subfile header (28 bytes): group@+0 u16, number@+2 u16, w@+4 u16, h@+6 u16,
    x@+8 i16, y@+10 i16, link@+12 u16, fmt@+14 u8, dataOfs@+16 u32,
    dataLen@+20 u32, palIdx@+24 u16, flags@+26 u16
  data: base = lofs if flags&1==0 else tofs; start = base+dataOfs;
    PNG bytes = buf[start+4 : start+dataLen]
"""
import struct, sys
from PIL import Image

def parse_sff(buf):
    assert buf[:11] == b'ElecbyteSpr', 'not an SFF file'
    assert buf[15] == 2, 'not SFF v2'
    sprOfs, sprNum = struct.unpack_from('<II', buf, 36)
    lofs, tofs = struct.unpack_from('<I', buf, 52)[0], struct.unpack_from('<I', buf, 60)[0]
    nodes = []
    for n in range(sprNum):
        o = sprOfs + n * 28
        g, i, w, h = struct.unpack_from('<HHHH', buf, o)
        link = struct.unpack_from('<H', buf, o + 12)[0]
        fmt = buf[o + 14]
        dataOfs, dataLen = struct.unpack_from('<II', buf, o + 16)
        palIdx, flags = struct.unpack_from('<HH', buf, o + 24)
        nodes.append(dict(n=n, g=g, i=i, w=w, h=h, link=link, fmt=fmt,
                          dataOfs=dataOfs, dataLen=dataLen, palIdx=palIdx,
                          flags=flags, hdr_off=o))
    return dict(sprOfs=sprOfs, sprNum=sprNum, lofs=lofs, tofs=tofs, nodes=nodes)

def node_data(buf, sff, node):
    base = sff['lofs'] if (node['flags'] & 1) == 0 else sff['tofs']
    start = base + node['dataOfs']
    return buf[start:start + node['dataLen']]

def main():
    sff_path, group, number, png_path = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    dry = '--dry-run' in sys.argv
    buf = bytearray(open(sff_path, 'rb').read())
    sff = parse_sff(bytes(buf))
    node = next((n for n in sff['nodes'] if n['g'] == group and n['i'] == number), None)
    if node is None:
        raise SystemExit(f'no sprite ({group},{number}) in {sff_path}')
    old = node_data(bytes(buf), sff, node)
    prefix = bytes(old[:4])
    png = open(png_path, 'rb').read()
    im = Image.open(png_path)
    print(f'sprite ({group},{number}): old w={node["w"]} h={node["h"]} fmt={node["fmt"]} '
          f'dataLen={node["dataLen"]} flags={node["flags"]} prefix={prefix.hex()}')
    print(f'  new PNG: {im.size[0]}x{im.size[1]} {len(png)} bytes')
    if dry:
        print('  dry run, not writing')
        return
    base = sff['lofs'] if (node['flags'] & 1) == 0 else sff['tofs']
    new_ofs = len(buf) - base
    buf += prefix + png
    o = node['hdr_off']
    struct.pack_into('<HH', buf, o + 4, im.size[0], im.size[1])  # w, h
    buf[o + 14] = 12  # fmt = truecolor PNG
    struct.pack_into('<II', buf, o + 16, new_ofs, 4 + len(png))  # dataOfs, dataLen
    struct.pack_into('<I', buf, 60, len(buf))  # tofs = new EOF (block stays empty)
    open(sff_path, 'wb').write(bytes(buf))
    print(f'  wrote: dataOfs={new_ofs} dataLen={4 + len(png)} new size={len(buf)}')

if __name__ == '__main__':
    main()
