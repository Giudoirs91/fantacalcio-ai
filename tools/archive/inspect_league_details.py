import urllib.request
import re
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for lid in [47, 87, 53, 54, 56]:
    url = f"https://www.fotmob.com/it/leagues/{lid}/overview"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if m:
            props = json.loads(m.group(1))['props']['pageProps']
            details = props.get('details', {})
            seasons_obj = details.get('seasons', props.get('seasons', []))
            print(f"LID: {lid} ({details.get('name')}) -> seasons: {seasons_obj[:2] if isinstance(seasons_obj, list) else type(seasons_obj)}")
    except Exception as e:
        print(f"Error {lid}: {e}")
