import urllib.request
import re
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

LEAGUES_TO_CHECK = {
    'Serie B': 56,
    'Eredivisie': 57,
    'Liga Portugal': 61,
    'Championship': 48,
    'Belgian Pro League': 40,
    'Brasileirao': 268,
    'Super Lig': 52,
    'Super League Greece': 67
}

discovered_seasons = {}

for lname, lid in LEAGUES_TO_CHECK.items():
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
                if sl.get('Name') in ['2025/2026', '2025']:
                    discovered_seasons[lname] = {
                        'league_id': lid,
                        'tournament_id': sl.get('TournamentId'),
                        'season_name': sl.get('Name'),
                        'path': sl.get('RelativePath')
                    }
                    print(f"-> Found: {lname:<20} | Season: {sl.get('Name')} | TournamentId: {sl.get('TournamentId')}")
                    break
    except Exception as e:
        print(f"Error {lname}: {e}")

print("\nAll Discovered Extra Leagues for 2025/2026:", discovered_seasons)
with open('config/extra_leagues_2025_26_map.json', 'w', encoding='utf-8') as f:
    json.dump(discovered_seasons, f, indent=2)
