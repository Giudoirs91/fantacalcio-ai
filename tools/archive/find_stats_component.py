import glob
import re

for fpath in glob.glob("chunks/*.js"):
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    if 'TDC' in code or 'TDCW' in code or 'ADCW' in code or 'BIB' in code or 'CALCIATORI' in code:
        print(f"\nFOUND STATS TABLE COMPONENT IN: {fpath} ({len(code)} bytes)")
        # Look for headers or API query inside this chunk
        idx = code.find('TDC')
        print("Context around TDC:\n", code[max(0, idx-200):min(len(code), idx+500)])
        print("="*60)
