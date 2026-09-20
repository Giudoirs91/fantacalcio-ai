import urllib.request
import re
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

LEAGUES = {
    'Premier League': 47,
    'La Liga': 87,
    'Ligue 1': 53,
    'Bundesliga': 54,
    'Serie A': 55
}

for lname, lid in LEAGUES.items():
    url = f"https://www.fotmob.com/it/leagues/{lid}/overview"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if m:
            props = json.loads(m.group(1))['props']['pageProps']
            stats_obj = props.get('stats', {})
            seasons_with_links = stats_obj.get('seasonsWithLinks', [])
            print(f"=== {lname} (id: {lid}) ===")
            for s in seasons_with_links[:4]:
                print(f"  Season: {s.get('name')} | ID: {s.get('id')} | Link: {s.get('link')}")
    except Exception as e:
        print(f"Error on {lname}: {e}")
