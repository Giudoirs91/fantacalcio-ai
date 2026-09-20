import urllib.request
import json
import os

api_key = "29418b8d7818c261a563dbf161b1ad8d"
url = f"https://api.the-odds-api.com/v4/sports/soccer_italy_serie_a/odds/?apiKey={api_key}&regions=eu&markets=h2h,totals"

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req) as resp:
        print("Status:", resp.status)
        headers = dict(resp.getheaders())
        print("Requests Remaining:", headers.get("x-requests-remaining"))
        print("Requests Used:", headers.get("x-requests-used"))
        raw = resp.read().decode("utf-8")
        data = json.loads(raw)
        print(f"Retrieved {len(data)} matches from Serie A:")
        
        # Salva per ispezione
        os.makedirs("data/raw", exist_ok=True)
        with open("data/raw/the_odds_api_serie_a.json", "w", encoding="utf-8") as f:
            f.write(raw)
            
        for match in data:
            home = match.get("home_team")
            away = match.get("away_team")
            commence = match.get("commence_time")
            num_bms = len(match.get("bookmakers", []))
            print(f" - {home} vs {away} [{commence}] ({num_bms} bookmakers)")
except Exception as e:
    print("Error:", e)
