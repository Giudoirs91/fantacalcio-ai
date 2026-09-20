import subprocess
import glob
import re

hashes = {
    "8243": ("794cd036", "8d143c8dd07eb414"),
    "9503": ("9503", "72c4cd8a395b1f20"),
    "9791": ("9791", "c980fd6af3efee98"),
    "8412": ("8412", "48a52105af17a252"),
    "8055": ("8055", "40fa69b3a7afc4a9"),
    "7184": ("7184", "43791f276e82309f"),
    "7134": ("7134", "bb16d439bb9d78db")
}

for cid, (name, h) in hashes.items():
    cfilename = f"{name}.{h}.js"
    url = f"https://www.legaseriea.it/_next/static/chunks/{cfilename}"
    outpath = f"chunks/{name}.js"
    print(f"Downloading {cfilename}...")
    subprocess.run(f'curl.exe -s "{url}" -o "{outpath}"', shell=True)

print("Downloaded! Now analyzing API endpoints in stats widget...")
for cid, (name, h) in hashes.items():
    fpath = f"chunks/{name}.js"
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    print(f"\n=== Chunk {name} ({len(code)} bytes) ===")
    # find API paths
    paths = re.findall(r'[`"\'](/[a-zA-Z0-9_\-/{}]+)[\'"`]', code)
    for p in set(paths):
        if any(k in p.lower() for k in ['stats', 'player', 'team', 'season', 'comp', 'leader', 'table', 'standings', 'ranking', 'statistiche']):
            print("  Route:", p)
    # find URLs
    urls = re.findall(r'https?://[^\s"\'`<>]+', code)
    for u in set(urls):
        print("  URL:", u)
