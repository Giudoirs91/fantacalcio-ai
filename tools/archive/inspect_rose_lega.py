import sys
sys.stdout.reconfigure(encoding='utf-8')
import struct
import re

def parse_biff_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    print(f"File Size: {len(data)} bytes")
    
    # 1. Search for UTF-16LE strings
    utf16_strings = []
    # Find sequences of printable utf-16 characters
    pattern = re.compile(b'(?:[\x20-\x7e]\x00){3,}')
    for m in pattern.finditer(data):
        try:
            s = m.group(0).decode('utf-16le').strip()
            if len(s) > 2:
                utf16_strings.append(s)
        except:
            pass

    print(f"Total UTF-16LE strings: {len(utf16_strings)}")
    print("Sample UTF-16LE strings:")
    for s in utf16_strings[:40]:
        print("  -", s)

    # 2. Extract all readable words / player names / numbers
    print("\n--- Searching for player names and numbers ---")
    all_text = []
    i = 0
    while i < len(data) - 4:
        # Check for length-prefixed strings
        # BIFF8 string: length (2 bytes), flags (1 byte)
        length = struct.unpack('<H', data[i:i+2])[0]
        if 1 <= length <= 100:
            flags = data[i+2]
            is_unicode = (flags & 0x01) != 0
            if is_unicode:
                str_bytes = length * 2
                if i + 3 + str_bytes <= len(data):
                    try:
                        decoded = data[i+3:i+3+str_bytes].decode('utf-16le')
                        if decoded.isprintable() and len(decoded.strip()) > 1:
                            all_text.append(decoded.strip())
                    except:
                        pass
            else:
                str_bytes = length
                if i + 3 + str_bytes <= len(data):
                    try:
                        decoded = data[i+3:i+3+str_bytes].decode('latin1')
                        if decoded.isprintable() and len(decoded.strip()) > 1:
                            all_text.append(decoded.strip())
                    except:
                        pass
        i += 1

    # Deduplicate while preserving order
    unique_text = []
    seen = set()
    for t in all_text:
        if t not in seen and len(t) > 1 and not t.startswith('?') and not t.startswith('Workbook'):
            seen.add(t)
            unique_text.append(t)

    print(f"Extracted {len(unique_text)} structured tokens/strings:")
    for t in unique_text:
        print(t)

if __name__ == "__main__":
    parse_biff_file('Rose-Lega-2025-2026.xls')
