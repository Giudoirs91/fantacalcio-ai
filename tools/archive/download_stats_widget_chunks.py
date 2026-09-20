import re
import subprocess

with open('webpack.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

idx = code.find('a.u=')
snippet = code[idx:idx+3500]

custom_names = {"5226": "a22dc6a2", "6347": "781e3532", "7422": "0b843f00", "8243": "794cd036"}
hashes_snippet = snippet.split('+"."+({')[1].split('})[e]')[0]
hashes = dict(re.findall(r'(\d+):"([^"]+)"', hashes_snippet))

widget_chunks = ['8243', '9503', '9791', '8412', '8055', '7184', '7134']

for cid in widget_chunks:
    name_part = custom_names.get(cid, cid)
    h = hashes.get(cid)
    if h:
        cfilename = f"{name_part}.{h}.js"
        url = f"https://www.legaseriea.it/_next/static/chunks/{cfilename}"
        outpath = f"chunks/{name_part}.js"
        print(f"Downloading {cfilename}...")
        subprocess.run(f'curl.exe -s "{url}" -o "{outpath}"', shell=True)

print("Downloaded, now inspecting API calls...")
for cid in widget_chunks:
    name_part = custom_names.get(cid, cid)
    fpath = f"chunks/{name_part}.js"
    try:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        print(f"\n=== Chunk {name_part} ({len(code)} bytes) ===")
        # search for API routes
        routes = re.findall(r'[`"\'](/[a-zA-Z0-9_\-/{}]+)[\'"`]', code)
        for r in set(routes):
            if any(k in r for k in ['stats', 'player', 'team', 'season', 'comp', 'leader', 'table', 'standings', 'ranking']):
                print("  Route:", r)
        
        # search for full URLs
        urls = re.findall(r'https?://[^\s"\'`<>]+', code)
        for u in set(urls):
            print("  Full URL:", u)
    except Exception as e:
        print(f"Error {fpath}: {e}")
