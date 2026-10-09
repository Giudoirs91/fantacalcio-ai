import json

players = json.load(open('data/processed/processed_players_master.json', encoding='utf-8'))
cal = json.load(open('config/calendario_serie_a_2026_27.json', encoding='utf-8'))
team_stats = json.load(open('config/team_stats_2026_27.json', encoding='utf-8')) if False else {}

g6 = next(r for r in cal if r['giornata'] == 6)
fix_map = {}
for m in g6['matches']:
    fix_map[m['home']] = {'opp': m['away'], 'isHome': True}
    fix_map[m['away']] = {'opp': m['home'], 'isHome': False}

print("=== STARTING GOALKEEPERS G6 (titolarita >= 60) ===")
valid_keepers = []
for p in players:
    if p.get('role') != 'P':
        continue
    tit = p.get('titolarita')
    tit_val = int(tit) if (tit is not None and str(tit).isdigit()) else 0
    if tit_val < 60:
        continue
    if p.get('is_injured'):
        continue
    tm = p.get('team')
    if tm not in fix_map:
        continue
    valid_keepers.append(p)
    print(f"- {p['name']} ({tm}): tit={tit_val}%, ovr={p.get('ovr')}, vs {fix_map[tm]['opp']} (home={fix_map[tm]['isHome']})")

print(f"\nTotal valid starting keepers: {len(valid_keepers)}")
