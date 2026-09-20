import subprocess
import os
import re

if not os.path.exists('webpack.js'):
    subprocess.run('curl.exe -s "https://www.legaseriea.it/_next/static/chunks/webpack-e011fb0ebd706d56.js" -o webpack.js', shell=True)

with open('webpack.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

chunk_map = dict(re.findall(r'(\d+):"([a-f0-9]+)"', code))
print(f"Total dynamic chunks found: {len(chunk_map)}")

# Let's download and inspect the chunks that relate to statistics:
# Let's download a batch of chunks and search for endpoints
stats_chunks = []
for cid, chash in chunk_map.items():
    cname = f"{cid}-{chash}.js"
    curl_cmd = f'curl.exe -s "https://www.legaseriea.it/_next/static/chunks/{cname}" -o "chunks/{cname}"'
    stats_chunks.append((cid, chash, cname))

subprocess.run("if not exist chunks mkdir chunks", shell=True)
print(f"Downloading {len(stats_chunks)} chunks into chunks/ directory...")

for cid, chash, cname in stats_chunks:
    subprocess.run(f'curl.exe -s "https://www.legaseriea.it/_next/static/chunks/{cname}" -o "chunks/{cname}"', shell=True)

print("Downloaded! Now searching for stats API / endpoints...")
import glob
for fpath in glob.glob("chunks/*.js"):
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    if any(k in content.lower() for k in ['/statistics', '/leaderboard', '/standings', 'deltatre', 'dapi.legaseriea', 'getplayers', 'statistiche']):
        endpoints = re.findall(r'https?://[^\s"\'`<>]+', content)
        paths = re.findall(r'[`"\'](/[a-zA-Z0-9_\-/]+(?:stats|player|season|championship|leaderboard|ranking|statistics)[a-zA-Z0-9_\-/]*)[\'"`]', content, re.IGNORECASE)
        if endpoints or paths:
            print(f"\n--- {fpath} ---")
            for ep in set(endpoints):
                if any(x in ep.lower() for x in ['api', 'stats', 'deltatre', 'seriea']):
                    print("  Full URL:", ep)
            for p in set(paths):
                print("  Path:", p)
