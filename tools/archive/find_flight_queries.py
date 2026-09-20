import re

with open('legaseriea.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

urls = re.findall(r'https?://[^\s"\'\\<>]+', html)
for u in sorted(set(urls)):
    if any(k in u.lower() for k in ['stats', 'player', 'dapi', 'seriea', 'deltatre', 'sdp', 'api', 'leaderboard', 'table']):
        print("URL in HTML:", u)

# Let's search for any json blobs in HTML
json_blobs = re.findall(r'\{[^{}]*"stats"[^{}]*\}', html)
print(f"JSON blobs with stats: {len(json_blobs)}")
for jb in json_blobs[:5]:
    print("  Blob:", jb[:150])
