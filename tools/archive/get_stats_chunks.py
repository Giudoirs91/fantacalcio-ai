import re
import subprocess

with open('webpack.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

chunk_map = dict(re.findall(r'(\d+):"([a-f0-9]+)"', code))

target_chunks = ['3349', '2331', '9077', '6159', '1007', '7674', '8551', '1486', '2286', '5381', '2520', '2727', '8004', '568', '3859', '9397', '8754', '7030', '5325', '7318', '2920']

print("Target chunks to download:")
for cid in target_chunks:
    chash = chunk_map.get(cid)
    if chash:
        cname = f"{cid}-{chash}.js"
        print(f"Downloading {cname}...")
        subprocess.run(f'curl.exe -s "https://www.legaseriea.it/_next/static/chunks/{cname}" -o "chunks/{cname}"', shell=True)

import glob
for fpath in glob.glob("chunks/*.js"):
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    # Search for fetch / API / URLs
    urls = re.findall(r'https?://[^\s"\'`<>]+', content)
    for u in set(urls):
        if any(k in u.lower() for k in ['dapi', 'api', 'stats', 'deltatre', 'seriea']):
            print(f"URL in {fpath}:", u)
    
    # Search for endpoint paths or GraphQL / REST queries
    paths = re.findall(r'[`"\'](/[a-zA-Z0-9_\-/]+(?:stats|player|season|championship|leaderboard|ranking|statistics|table)[a-zA-Z0-9_\-/]*)[\'"`]', content, re.IGNORECASE)
    for p in set(paths):
        print(f"Path in {fpath}:", p)
