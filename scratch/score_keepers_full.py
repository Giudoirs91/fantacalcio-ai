import json, math

players = json.load(open('data/processed/processed_players_master.json', encoding='utf-8'))
cal = json.load(open('config/calendario_serie_a_2026_27.json', encoding='utf-8'))
team_stats = json.load(open('data/raw/team_stats_2026_27.json', encoding='utf-8'))

LEAGUE_AVG_XGA = 6.03
LEAGUE_AVG_XG = 6.04
LEAGUE_AVG_GC = 1.54

g6 = next(r for r in cal if r['giornata'] == 6)
fix_map = {}
for m in g6['matches']:
    fix_map[m['home']] = {'opp': m['away'], 'isHome': True}
    fix_map[m['away']] = {'opp': m['home'], 'isHome': False}

def calc_score(player, matchInfo):
    tit = (player.get('titolarita') if player.get('titolarita') is not None else 0)
    tit_val = int(tit) if str(tit).isdigit() else 0
    if tit_val < 65:
        return -500

    team = player.get('team')
    opp = matchInfo['opp']
    isHome = matchInfo['isHome']
    role = player.get('role')

    myStats = team_stats.get(team, {})
    oppStats = team_stats.get(opp, {})

    myXga = float(myStats.get('xga_team') or LEAGUE_AVG_XGA)
    myGc = float(myStats.get('goals_conceded_match') or LEAGUE_AVG_GC)
    myCs = float(myStats.get('clean_sheets') or 0)

    oppXg = float(oppStats.get('xg_team') or LEAGUE_AVG_XG)
    oppXga = float(oppStats.get('xga_team') or LEAGUE_AVG_XGA)
    oppGc = float(oppStats.get('goals_conceded_match') or LEAGUE_AVG_GC)
    oppBc = float(oppStats.get('big_chances') or 5.0)

    ovr = float(player.get('ovr') or 75)
    fm = float(player.get('fm_2627') or player.get('fm') or 6.0)

    score = 65.0 + (ovr * 0.18) + (fm * 2.5)
    csFactor = (myCs * 8.0) - (myGc * 6.0) - ((myXga / LEAGUE_AVG_XGA) * 5.0)
    score += csFactor
    if isHome:
        score += 10.0

    xgDiff = oppXg - LEAGUE_AVG_XG
    if xgDiff > 0:
        score -= math.pow(xgDiff, 1.35) * 8.5
    else:
        score += abs(xgDiff) * 6.0

    score -= (oppBc / 4.0) * 3.0
    return round(score, 1)

gks = [p for p in players if p.get('role') == 'P' and p.get('team') in fix_map and not p.get('is_injured')]
scored = []
for p in gks:
    sc = calc_score(p, fix_map[p['team']])
    if sc > 0:
        scored.append((p, sc))

scored.sort(key=lambda x: x[1], reverse=True)
print("=== TOP GOALKEEPERS FOR G6 (EXACT FORMULA) ===")
for p, sc in scored[:10]:
    print(f"{p['name']} ({p['team']}): score={sc}, tit={p.get('titolarita')}%, ovr={p.get('ovr')}, vs {fix_map[p['team']]['opp']} (home={fix_map[p['team']]['isHome']})")
