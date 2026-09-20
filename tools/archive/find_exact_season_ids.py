import urllib.request
import re
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

LEAGUES = {
    'Premier League': 47,
    'La Liga': 87,
    'Ligue 1': 53,
    'Bundesliga': 54,
    'Serie A': 55,
    'Serie B': 56
}

for lname, lid in LEAGUES.items():
    # Fetch stats page with expected_goals
    url = f"https://www.fotmob.com/it/leagues/{lid}/stats/players/expected_goals"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if m:
            data = json.loads(m.group(1))['props']['pageProps']['data']
            seasons = data.get('seasons', [])
            print(f"=== {lname} (id: {lid}) ===")
            for s in seasons[:4]:
                print(f"  Season: {s.get('name'):<12} | ID: {s.get('id')}")
    except Exception as e:
        print(f"Error on {lname}: {e}")
