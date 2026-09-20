import urllib.request
import re
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = "https://www.fotmob.com/it/leagues/47/overview"
req = urllib.request.Request(url, headers=HEADERS)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8')

m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
if m:
    props = json.loads(m.group(1))['props']['pageProps']
    print("Tabs:", props.get('tabs'))
    print("Stats keys:", list(props.get('stats', {}).keys()) if isinstance(props.get('stats'), dict) else type(props.get('stats')))
    if 'stats' in props and isinstance(props['stats'], dict):
        players_top = props['stats'].get('players', [])
        print("Players top stats:", len(players_top))
        if players_top:
            print("Sample stat:", players_top[0].get('header'), players_top[0].get('fetchAllUrl'))
