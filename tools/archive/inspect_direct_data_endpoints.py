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

league_links = {}

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
            players_stats = stats_obj.get('players', [])
            print(f"League: {lname:<15} (id: {lid}) -> stats count: {len(players_stats)}")
            if players_stats:
                sample_url = players_stats[0].get('fetchAllUrl', '')
                print(f"  sample URL: {sample_url}")
                # Estrai season ID dal sample_url
                m_sid = re.search(r'/season/(\d+)/', sample_url)
                if m_sid:
                    league_links[lname] = {'league_id': lid, 'season_id': m_sid.group(1), 'sample_url': sample_url}
    except Exception as e:
        print(f"Error {lname}: {e}")

print("\nLeague direct data endpoints:", league_links)
