import subprocess
import json

season_ids = [
    "5f0e080fc3a44073984b75b3a8e06a8a",
    "1e32f55e98fc408a9d1fc27c0ba43243",
    "104a84bc07f641e685f70a850c6399eb",
    "65f4d59dedbb43b68197b0ff0529fa21",
    "ed7fdc2a3e7b408b942ec177b7b956b5",
    "emdmtfr1v8rey2qru3xzfwges",
    "b25u56idqlgo8s1rahhltqd5g",
    "3r8v8kb4vebxrtcj5d7ofk1zo",
    "278"
]

for sid in season_ids:
    for entity in ['players', 'teams']:
        url = f"https://seriea-api.prd.sdp.deltatre.digital/v1/seriea/football/seasons/{sid}/stats/{entity}?locale=it-IT"
        cmd = f'curl.exe -s -H "Accept: text/plain; x-api-version=1.0" "{url}"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        body = res.stdout.strip()
        try:
            d = json.loads(body)
            p_val = d.get(entity)
            if p_val is not None:
                print(f"--> SUCCESS! sid={sid} entity={entity} count={len(p_val)}")
                with open(f"stats_{sid}_{entity}.json", 'w', encoding='utf-8') as f:
                    json.dump(d, f, indent=2)
            else:
                pass
        except Exception:
            pass
print("Finished test.")
