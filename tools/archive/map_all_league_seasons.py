import urllib.request
import re
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

LEAGUES = {
    'Serie A': 55,
    'Premier League': 47,
    'La Liga': 87,
    'Ligue 1': 53,
    'Bundesliga': 54,
    'Serie B': 56
}

season_2526_map = {}

for lname, lid in LEAGUES.items():
    url = f"https://www.fotmob.com/it/leagues/{lid}/overview"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if m:
            props = json.loads(m.group(1))['props']['pageProps']
            stat_links = props.get('stats', {}).get('seasonStatLinks', [])
            for sl in stat_links:
                if sl.get('Name') == '2025/2026':
                    season_2526_map[lname] = {
                        'league_id': lid,
                        'tournament_id': sl.get('TournamentId'),
                        'path': sl.get('RelativePath'),
                        'url': f"https://www.fotmob.com/it/leagues/{lid}/stats/season/{sl.get('TournamentId')}/players/expected_goals"
                    }
                    print(f"-> {lname:<15}: Season 2025/2026 Tournament ID = {sl.get('TournamentId')}")
    except Exception as e:
        print(f"Error {lname}: {e}")

with open('config/leagues_2025_26_map.json', 'w', encoding='utf-8') as f:
    json.dump(season_2526_map, f, indent=2)

print("\nSaved season_2526_map to config/leagues_2025_26_map.json")
