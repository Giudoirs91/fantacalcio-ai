import urllib.request
import json
import re

headers = {'User-Agent': 'Mozilla/5.0'}
for test_id in range(50, 160):
    url = f"https://www.fotmob.com/it/leagues/{test_id}/overview"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=3) as resp:
            html = resp.read().decode('utf-8')
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if m:
            data = json.loads(m.group(1))['props']['pageProps']
            details = data.get('details', {})
            name = details.get('name', '')
            country = details.get('country', '')
            if 'italy' in country.lower() or 'serie' in name.lower():
                print(f"ID {test_id}: {name} ({country})")
    except:
        pass
