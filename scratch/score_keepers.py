import json, math

players = json.load(open('data/processed/processed_players_master.json', encoding='utf-8'))
cal = json.load(open('config/calendario_serie_a_2026_27.json', encoding='utf-8'))
team_stats = json.load(open('config/team_stats_2026_27.json', encoding='utf-8')) if False else {}

LEAGUE_AVG_XGA = 6.03
LEAGUE_AVG_XG = 6.04
LEAGUE_AVG_GC = 1.54

g6 = next(r for r in cal if r['giornata'] == 6)
fix_map = {}
for m in g6['matches']:
    fix_map[m['home']] = {'opp': m['away'], 'isHome': True}
    fix_map[m['away']] = {'opp': m['home'], 'isHome': False}

# Score calculation
def calc_score(p, m):
    tit = p.get('titolarita')
    tit_val = int(tit) if (tit is not None and str(tit).isdigit()) else 0
    if tit_val < 65:  # Strict filter for goalkeepers
        return -500
    ovr = float(p.get('ovr') or 75)
    fm = float(p.get('fm_2627') or p.get('fm') or 6.0)
    score = 65.0 + (ovr * 0.18) + (fm * 2.5)
    if m['isHome']:
        score += 10.0
    return round(score, 1)

gks = [p for p in players if p.get('role') == 'P' and p.get('team') in fix_map and not p.get('is_injured')]
scored = []
for p in gks:
    sc = calc_score(p, fix_map[p['team']])
    if sc > 0:
        scored.append((p, sc))

scored.sort(key=lambda x: x[1], reverse=True)
print("=== TOP GOALKEEPERS FOR G6 ===")
for p, sc in scored[:10]:
    print(f"{p['name']} ({p['team']}): score={sc}, tit={p.get('titolarita')}%, ovr={p.get('ovr')}, home={fix_map[p['team']]['isHome']}")
