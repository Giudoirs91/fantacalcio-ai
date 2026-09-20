import re

with open('legaseriea.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

scripts = re.findall(r'<script[^>]*src="([^"]+)"', html)
for s in scripts:
    print(s)
