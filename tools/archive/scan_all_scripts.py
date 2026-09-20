import re
import urllib.request
import subprocess

with open('legaseriea.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

scripts = re.findall(r'<script[^>]*src="([^"]+)"', html)
print(f"Found {len(scripts)} scripts in HTML")

for s in scripts:
    filename = s.split('/')[-1]
    url = f"https://www.legaseriea.it{s}"
    subprocess.run(f'curl.exe -s "{url}" -o "{filename}"', shell=True)

print("Downloaded scripts, now searching...")
import glob
for fpath in glob.glob("*.js"):
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    if 'deltatre' in code or 'stats' in code.lower():
        # find endpoints
        matches = re.findall(r'[`"\'](https://seriea-api\.prd\.sdp\.deltatre\.digital/v1/[^`"\']+)[\'"`]', code)
        paths = re.findall(r'[`"\'](/[a-zA-Z0-9_\-/]+(?:stats|player|season|championship|leaderboard)[a-zA-Z0-9_\-/]*)[\'"`]', code, re.IGNORECASE)
        if matches or paths:
            print(f"\n--- {fpath} ---")
            for m in set(matches):
                print("  URL:", m)
            for p in set(paths):
                print("  Path:", p)
