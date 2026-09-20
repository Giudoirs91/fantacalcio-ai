import urllib.request
import urllib.parse
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def search_player(name):
    url = f"https://www.fotmob.com/api/search/suggest?term={urllib.parse.quote(name)}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            sugg = data.get('suggestions', [])
            players = [s for s in sugg if s.get('type') == 'player']
            return players
    except Exception as e:
        print(f"Search error {name}: {e}")
        return []

def get_player_data(player_id):
    url = f"https://www.fotmob.com/api/playerData?id={player_id}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"PlayerData error {player_id}: {e}")
        return None

# Test con Douglas Luiz
print("Searching Douglas Luiz...")
douglas = search_player("Douglas Luiz")
print("Found:", douglas)
if douglas:
    pid = douglas[0]['id']
    pdata = get_player_data(pid)
    if pdata:
        print("\nPlayer Data Keys:", list(pdata.keys()))
        career = pdata.get('careerHistory', {})
        print("Career keys:", list(career.keys()) if isinstance(career, dict) else type(career))
        stats_section = pdata.get('statSeasons', [])
        print(f"Stat seasons found: {len(stats_section)}")
        for s in stats_section[:5]:
            print("  Season:", s.get('seasonName'), "| League:", s.get('tournamentName'), "| Entries:", len(s.get('stats', [])))
