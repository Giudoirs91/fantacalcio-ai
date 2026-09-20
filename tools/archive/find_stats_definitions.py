import re
import glob

for fpath in glob.glob("*.js") + glob.glob("chunks/*.js"):
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    # search for stat ID arrays or mappings
    matches = re.findall(r'statsId[s]?\s*:\s*\[([^\]]+)\]', code)
    if matches:
        print(f"\nStats IDs in {fpath}:")
        for m in set(matches):
            print("  ->", m[:200])
    
    # search for enum or mappings like _Q = { Goals: ... }
    stat_enums = re.findall(r'(\w+\._Q\.\w+)', code)
    if stat_enums:
        print(f"Stat enums in {fpath}: {len(stat_enums)} found")
        for se in list(set(stat_enums))[:10]:
            print("   Enum:", se)
