import re
import glob

for fpath in glob.glob("*.js") + glob.glob("chunks/*.js"):
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    if 'stats/players' in content:
        print(f"\nFound 'stats/players' in {fpath}")
        idx = content.find('stats/players')
        while idx != -1:
            print("Context:", content[max(0, idx-200):min(len(content), idx+400)])
            print("="*60)
            idx = content.find('stats/players', idx+1)
