import re
import subprocess

with open('webpack.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

idx = code.find('a.u=')
snippet = code[idx:idx+3500]

# parse custom names map: ({5226:"a22dc6a2", ...})
custom_names = dict(re.findall(r'(\d+):"([^"]+)"', snippet.split('(({')[1].split('})')[0])) if '(({ ' in snippet or '(({5226' in snippet else {}

# parse hashes map: ({18:"673c...", ...})
hashes_snippet = snippet.split('+"."+({')[1].split('})[e]')[0]
hashes = dict(re.findall(r'(\d+):"([^"]+)"', hashes_snippet))

print(f"Parsed {len(hashes)} chunk hashes")

target_cids = ['3349', '2331', '9077', '6159', '1007', '25428', '8551', '2286', '5381', '7674', '2727', '8004']

for cid in target_cids:
    if cid in hashes:
        name_part = custom_names.get(cid, cid)
        h = hashes[cid]
        cfilename = f"{name_part}.{h}.js"
        url = f"https://www.legaseriea.it/_next/static/chunks/{cfilename}"
        outpath = f"chunks/{name_part}.js"
        print(f"Downloading {url} -> {outpath}")
        subprocess.run(f'curl.exe -s "{url}" -o "{outpath}"', shell=True)

import glob
for fpath in glob.glob("chunks/*.js"):
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    if len(content) > 500 and not content.startswith("<!DOCTYPE"):
        print(f"\n=== VALID CHUNK: {fpath} ({len(content)} bytes) ===")
        # search for strings like "stats", "deltatre", "http", "api"
        urls = re.findall(r'https?://[^\s"\'`<>]+', content)
        for u in set(urls):
            print("  URL:", u)
        paths = re.findall(r'[`"\'](/v[0-9]/[a-zA-Z0-9_\-/]+|/api/[a-zA-Z0-9_\-/]+)[\'"`]', content)
        for p in set(paths):
            print("  API Path:", p)
