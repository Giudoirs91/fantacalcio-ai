import urllib.request
import re
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

LEAGUES = {
    'Premier League': 47,
    'La Liga': 87,
    'Ligue 1': 53,
    'Bundesliga': 54,
    'Serie B': 136
}

for lname, lid in LEAGUES.items():
    url = f"https://www.fotmob.com/it/leagues/{lid}/stats"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if m:
            props = json.loads(m.group(1))['props']['pageProps']
            data = props.get('data', {})
            season_id = data.get('currentSeasonId')
            seasons_list = data.get('seasons', [])
            print(f"{lname:<15} (id: {lid}) -> currentSeasonId: {season_id} | available: {[(s.get('name'), s.get('id')) for s in seasons_list[:2]]}")
    except Exception as e:
        print(f"Error {lname}: {e}")
