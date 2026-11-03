import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load team stats
with open('data/raw/fotmob_team_stats_2026_27.json', 'r', encoding='utf-8') as f:
    team_stats = json.load(f)

print("Available teams in team_stats:")
for t in team_stats:
    name = t.get('team_name') or t.get('name')
    print(f"- {name}")

# Check specific teams
target_teams = ['Sassuolo', 'Lazio', 'Roma', 'Cagliari']
for t in team_stats:
    name = t.get('team_name') or t.get('name')
    if any(tgt.lower() in name.lower() for tgt in target_teams):
        print(f"\n--- {name} ---")
        for k, v in t.items():
            if k not in ['matches', 'squad']:
                print(f"  {k}: {v}")
