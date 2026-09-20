import subprocess
import glob
import re

chunks = [
    "4bd1b696-182b6b13bdad92e3.js",
    "1255-f5c4f3c719acc9db.js",
    "main-app-234525b5e3ddebfb.js",
    "9919-af89ead98f955257.js",
    "9031-4a6fadff7bd74420.js",
    "8730-90442a9b50c93038.js",
    "3323-029b35a8213d87d2.js",
    "6016-13cacdfd23c4ef0f.js",
    "2249-b9ce5e9fc61b829d.js",
    "751-7e9014a432154094.js",
    "b9e39b43-b5eda7c146674b07.js",
    "aaea2bcf-884442894952ffeb.js",
    "13b76428-c75990430d19f963.js",
]

for c in chunks:
    subprocess.run(f'curl.exe -s "https://www.legaseriea.it/_next/static/chunks/{c}" -o "chunks/{c}"', shell=True)

print("Downloaded, now scanning for zm: or stats query...")
for fpath in glob.glob("chunks/*.js"):
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    if 'zm:' in code:
        print(f"FOUND zm: in {fpath}!")
        idx = code.find('zm:')
        print(code[max(0, idx-100):min(len(code), idx+1000)])
