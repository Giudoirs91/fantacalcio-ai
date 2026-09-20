import subprocess
import json

season_id = "5f0e080fc3a44073984b75b3a8e06a8a"
opta_id = "emdmtfr1v8rey2qru3xzfwges"

endpoints = [
    f"https://seriea-api.prd.sdp.deltatre.digital/v1/seriea/football/seasons/{season_id}/statistics/players",
    f"https://seriea-api.prd.sdp.deltatre.digital/v1/seriea/football/seasons/{season_id}/stats/players",
    f"https://seriea-api.prd.sdp.deltatre.digital/v1/seriea/football/seasons/{season_id}/players/stats",
    f"https://seriea-api.prd.sdp.deltatre.digital/v1/seriea/football/seasons/{season_id}/leaderboards",
    f"https://seriea-api.prd.sdp.deltatre.digital/v1/seriea/football/seasons/{season_id}/players",
    f"https://seriea-api.prd.sdp.deltatre.digital/v1/seriea/football/seasons/{season_id}/standings",
    f"https://seriea-api.prd.sdp.deltatre.digital/v1/seriea/football/statistics/players?seasonId={season_id}",
    f"https://seriea-api.prd.sdp.deltatre.digital/v1/seriea/football/stats/players?seasonId={season_id}",
    f"https://seriea-api.prd.sdp.deltatre.digital/v1/seriea/football/seasons/{opta_id}/statistics/players",
    f"https://seriea-api.prd.sdp.deltatre.digital/v1/seriea/football/seasons/{opta_id}/stats/players",
    f"https://dapi.legaseriea.it/v2/stats/it-it/seasons/{season_id}/players",
    f"https://dapi.legaseriea.it/v2/content/it-it/seasons/{season_id}/stats",
]

for url in endpoints:
    cmd = f'curl.exe -s -w "\\nHTTP_CODE:%{{http_code}}" -H "Accept: text/plain; x-api-version=1.0" "{url}"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    lines = res.stdout.strip().split('\n')
    http_code = lines[-1] if lines else 'UNKNOWN'
    body = '\n'.join(lines[:-1])
    print(f"URL: {url}")
    print(f"  Result: {http_code} | Body length: {len(body)}")
    if '200' in http_code and len(body) > 50:
        print(f"  Body preview: {body[:300]}")
        with open('valid_endpoint_response.json', 'w', encoding='utf-8') as f:
            f.write(body)
        print("  --> SAVED valid_endpoint_response.json!")
