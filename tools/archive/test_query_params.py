import subprocess
import json

season_id = "5f0e080fc3a44073984b75b3a8e06a8a"
base_url = f"https://seriea-api.prd.sdp.deltatre.digital/v1/seriea/football/seasons/{season_id}/stats/players"

params_list = [
    "",
    "?locale=it-IT",
    "?locale=it-IT&pageSize=50",
    "?statsType=basic-stats",
    "?type=basic",
    "?statsId=basic-stats",
    "?statsId=General",
    "?statsCategory=General",
    "?pageSize=100&pageNumber=1",
    "?statIds=GP,G,FC,FS,OFF,YC,RC,C",
    "?statGroup=basic",
    "?competitionId=ec93b94f74294dc98ab5bcfd67fc0d88",
    "?competition=serie-a",
]

for p in params_list:
    url = base_url + p
    cmd = f'curl.exe -s -H "Accept: text/plain; x-api-version=1.0" "{url}"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    body = res.stdout.strip()
    try:
        data = json.loads(body)
        has_players = data.get('players') is not None
        tot_pages = data.get('pagination', {}).get('totalPages', 0)
        print(f"Param: {p:40s} -> Players: {has_players} | totalPages: {tot_pages} | Len: {len(body)}")
        if has_players and len(data.get('players', [])) > 0:
            print("  FOUND PLAYERS! Count:", len(data['players']))
            with open('found_players_stats.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Param: {p} -> Error / Not JSON: {body[:100]}")
