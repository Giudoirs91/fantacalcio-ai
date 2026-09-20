import sys
sys.stdout.reconfigure(encoding='utf-8')
import struct
import pandas as pd

def decode_rk(rk_val):
    if rk_val & 0x02:
        val = rk_val >> 2
    else:
        val = struct.unpack('<d', struct.pack('<II', 0, rk_val & 0xFFFFFFFC))[0]
    if rk_val & 0x01:
        val /= 100.0
    return val

def extract_ole_streams(data):
    # OLE Header
    header = data[:512]
    sig = header[:8]
    if sig != b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
        print("Not an OLE file, treating as raw stream")
        return {'Workbook': data}

    sector_size = 1 << struct.unpack('<H', header[30:32])[0]
    num_fat_sectors = struct.unpack('<I', header[44:48])[0]
    first_dir_sector = struct.unpack('<I', header[48:52])[0]
    first_minifat_sector = struct.unpack('<I', header[60:64])[0]
    num_minifat_sectors = struct.unpack('<I', header[64:68])[0]
    
    # Read FAT table
    fat_sectors = struct.unpack(f'<{min(109, num_fat_sectors)}I', header[76:76 + min(109, num_fat_sectors)*4])
    fat = []
    for fs in fat_sectors:
        sec_offset = (fs + 1) * sector_size
        fat.extend(struct.unpack(f'<{sector_size // 4}I', data[sec_offset:sec_offset + sector_size]))

    def get_chain(start_sec):
        chain = []
        curr = start_sec
        while curr != 0xFFFFFFFE and curr < len(fat):
            chain.append(curr)
            curr = fat[curr]
        return chain

    def read_chain(start_sec):
        res = bytearray()
        for sec in get_chain(start_sec):
            off = (sec + 1) * sector_size
            res.extend(data[off:off + sector_size])
        return bytes(res)

    # Read directory entries
    dir_data = read_chain(first_dir_sector)
    streams = {}
    for i in range(0, len(dir_data), 128):
        entry = dir_data[i:i+128]
        name_len = struct.unpack('<H', entry[64:66])[0]
        if name_len == 0:
            continue
        name = entry[:name_len].decode('utf-16le', errors='ignore').rstrip('\x00')
        obj_type = entry[66]
        start_sec = struct.unpack('<I', entry[116:120])[0]
        size = struct.unpack('<I', entry[120:124])[0]
        
        if obj_type == 2: # Stream
            stream_content = read_chain(start_sec)[:size]
            streams[name] = stream_content
            print(f"Extracted Stream: '{name}' ({len(stream_content)} bytes)")

    return streams

def parse_workbook(wb_data):
    p = 0
    sst = []
    cells = {}
    
    # Collect all records
    records = []
    while p < len(wb_data) - 4:
        rec_type, rec_len = struct.unpack('<HH', wb_data[p:p+4])
        p += 4
        rec_content = wb_data[p:p+rec_len]
        p += rec_len
        records.append((rec_type, rec_content))

    for rec_type, rec_content in records:
        if rec_type == 0x00FC: # SST
            total_strings, unique_strings = struct.unpack('<II', rec_content[:8])
            sp = 8
            for _ in range(unique_strings):
                if sp >= len(rec_content) - 2:
                    break
                char_len = struct.unpack('<H', rec_content[sp:sp+2])[0]
                flags = rec_content[sp+2]
                sp += 3
                is_unicode = (flags & 0x01) != 0
                if is_unicode:
                    byte_len = char_len * 2
                    s = rec_content[sp:sp+byte_len].decode('utf-16le', errors='ignore')
                    sp += byte_len
                else:
                    byte_len = char_len
                    s = rec_content[sp:sp+byte_len].decode('latin1', errors='ignore')
                    sp += byte_len
                sst.append(s)

    for rec_type, rec_content in records:
        if rec_type == 0x00FD: # LABELSST
            row, col, xf, sst_idx = struct.unpack('<HHHI', rec_content[:10])
            if sst_idx < len(sst):
                cells[(row, col)] = sst[sst_idx]
        elif rec_type == 0x027E: # RK
            row, col, xf, rk_val = struct.unpack('<HHHI', rec_content[:10])
            cells[(row, col)] = decode_rk(rk_val)
        elif rec_type == 0x00BD: # MULRK
            row, col_first = struct.unpack('<HH', rec_content[:4])
            col_last = struct.unpack('<H', rec_content[-2:])[0]
            col_count = col_last - col_first + 1
            for k in range(col_count):
                xf, rk_val = struct.unpack('<HI', rec_content[4 + k*6 : 10 + k*6])
                cells[(row, col_first + k)] = decode_rk(rk_val)
        elif rec_type == 0x0203: # NUMBER
            row, col, xf = struct.unpack('<HHH', rec_content[:6])
            val = struct.unpack('<d', rec_content[6:14])[0]
            cells[(row, col)] = val
        elif rec_type == 0x0004 or rec_type == 0x0204: # LABEL
            row, col, xf = struct.unpack('<HHH', rec_content[:6])
            char_len = struct.unpack('<H', rec_content[6:8])[0]
            flags = rec_content[8]
            is_unicode = (flags & 0x01) != 0
            if is_unicode:
                s = rec_content[9:9+char_len*2].decode('utf-16le', errors='ignore')
            else:
                s = rec_content[9:9+char_len].decode('latin1', errors='ignore')
            cells[(row, col)] = s

    if not cells:
        print("No cells found in Workbook stream.")
        return None

    max_r = max(r for r, c in cells.keys())
    max_c = max(c for r, c in cells.keys())
    grid = [[None for _ in range(max_c + 1)] for _ in range(max_r + 1)]
    for (r, c), v in cells.items():
        grid[r][c] = v

    return pd.DataFrame(grid)

with open('Rose-Lega-2025-2026.xls', 'rb') as f:
    streams = extract_ole_streams(f.read())
    wb_data = streams.get('Workbook') or streams.get('Book')
    if wb_data:
        df = parse_workbook(wb_data)
        if df is not None:
            print(f"\nSuccessfully parsed DataFrame shape: {df.shape}")
            pd.set_option('display.max_columns', 30)
            pd.set_option('display.max_rows', 100)
            pd.set_option('display.width', 1000)
            print(df.to_string())
