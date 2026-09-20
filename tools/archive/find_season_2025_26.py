import json
import subprocess

with open('dapi_seriea.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

tags = d.get('tags', [])
print(f"Checking {len(tags)} tags...")

for t in tags:
    url = t.get('selfUrl')
    if url:
        res = subprocess.run(f'curl.exe -s "{url}"', shell=True, capture_output=True, text=True)
        try:
            tag_data = json.loads(res.stdout)
            title = tag_data.get('title')
            extra = tag_data.get('extraData', {})
            print(f"Title: {title} | SeasonID: {extra.get('seasonId')} | ProviderID: {extra.get('providerId')}")
            if title in ['2025/2026', '2024/2025', '2026/2027']:
                with open(f"tag_{title.replace('/', '_')}.json", 'w', encoding='utf-8') as tf:
                    json.dump(tag_data, tf, indent=2)
        except Exception:
            pass
