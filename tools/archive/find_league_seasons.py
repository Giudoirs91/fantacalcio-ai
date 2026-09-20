import urllib.request
import re
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

LEAGUES = {
    'Premier League': 47,
    'La Liga': 87,
    'Ligue 1': 53,
    'Bundesliga': 54,
    'Serie B': 56
}

season_ids = {}

for lname, lid in LEAGUES.items():
    url = f"https://www.fotmob.com/it/leagues/{lid}/overview"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if m:
            page_props = json.loads(m.group(1))['props']['pageProps']
            seasons = page_props.get('allAvailableSeasons', page_props.get('seasons', []))
            print(f"{lname:<15} (id: {lid}) -> Seasons: {[(s.get('seasonName') or s.get('name'), s.get('seasonId') or s.get('id')) for s in seasons[:3]]}")
            if seasons:
                season_ids[lname] = {'league_id': lid, 'season_2526_id': seasons[0].get('seasonId') or seasons[0].get('id')}
    except Exception as e:
        print(f"Error on {lname}: {e}")

print("\nDiscovered Season IDs for 2025/26:", season_ids)
