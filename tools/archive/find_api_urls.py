import re

with open('legaseriea.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

urls = re.findall(r'https?://[^\s"\'<>]+', content)
print(f"Total URLs found: {len(urls)}")
for u in sorted(set(urls)):
    if any(k in u.lower() for k in ['api', 'stats', 'statistiche', 'data', 'cdn', 'player', 'giocatori']):
        print(u)
