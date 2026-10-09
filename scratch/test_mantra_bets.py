import json, sys
sys.stdout.reconfigure(encoding='utf-8')

players = json.load(open('data/processed/processed_players_master.json', encoding='utf-8'))
cal = json.load(open('config/calendario_serie_a_2026_27.json', encoding='utf-8'))
team_stats = json.load(open('data/raw/team_stats_2026_27.json', encoding='utf-8'))

g6 = next(r for r in cal if r['giornata'] == 6)
fix_map = {}
for m in g6['matches']:
    fix_map[m['home']] = {'opp': m['away'], 'isHome': True}
    fix_map[m['away']] = {'opp': m['home'], 'isHome': False}

LEAGUE_AVG_XGA = 6.03
LEAGUE_AVG_XG = 6.04
LEAGUE_AVG_GC = 1.54

def calc_score(player, matchInfo):
    tit = float(player.get('titolarita') if player.get('titolarita') is not None else 0)
    if tit < 50: return -500.0
    if player.get('role') == 'P' and tit < 70: return -500.0

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
    mv = float(player.get('mv_2627') or player.get('mv') or 6.0)
    xg90 = float(player.get('xg90_2627') or player.get('xg90') or 0.0)
    xa90 = float(player.get('xa90_2627') or player.get('xa90') or 0.0)
    gol = float(player.get('gol_2627') or 0)
    ass = float(player.get('assist_2627') or 0)

    if role == 'P':
        score = 65.0 + (ovr * 0.18) + (fm * 2.5)
        score += (myCs * 8.0) - (myGc * 6.0) - ((myXga / LEAGUE_AVG_XGA) * 5.0)
        if isHome: score += 10.0
        xgDiff = oppXg - LEAGUE_AVG_XG
        if xgDiff > 0:
            score -= (xgDiff ** 1.35) * 8.5
        else:
            score += abs(xgDiff) * 6.0
        score -= (oppBc / 4.0) * 3.0
        return round(score, 1)
    else:
        score = 50.0 + (ovr * 0.28) + (fm * 4.0)
        score += (oppXga / LEAGUE_AVG_XGA) * 10.0 + (oppGc * 6.0)
        if isHome: score += 5.0
        if player.get('is_rigorista_1'): score += 12.0
        if player.get('is_punizioni'): score += 6.0
        if player.get('is_oop'): score += 7.0
        score += (gol * 6.0) + (ass * 4.0)
        return round(score, 1)

def calc_opportunity_score(player, matchInfo):
    tit = float(player.get('titolarita') if player.get('titolarita') is not None else 0)
    if tit < 50: return -500.0
    if player.get('role') == 'P' and tit < 70: return -500.0

    ovr = float(player.get('ovr') or 70)
    if ovr > 80: return -500.0

    team = player.get('team')
    opp = matchInfo['opp']
    isHome = matchInfo['isHome']
    role = player.get('role')

    oppStats = team_stats.get(opp, {})
    oppXga = float(oppStats.get('xga_team') or LEAGUE_AVG_XGA)
    oppGc = float(oppStats.get('goals_conceded_match') or LEAGUE_AVG_GC)
    oppXg = float(oppStats.get('xg_team') or LEAGUE_AVG_XG)

    fm = float(player.get('fm_2627') or player.get('fm') or 6.0)
    gol = float(player.get('gol_2627') or 0)
    ass = float(player.get('assist_2627') or 0)

    score = 50.0 + (fm * 3.5) + (tit * 0.12)
    if isHome: score += 8.0
    if player.get('is_rigorista_1'): score += 20.0
    if player.get('is_oop'): score += 16.0
    if player.get('is_punizioni'): score += 10.0

    if role == 'P':
        if oppXg < 5.5: score += 18.0
        if isHome: score += 10.0
    else:
        score += (oppXga / LEAGUE_AVG_XGA) * 15.0 + (oppGc * 7.0)
        score += (gol * 8.0) + (ass * 5.0)

    return round(score, 1)

mantraPositions = ['Por', 'Dd', 'Ds', 'Dc', 'B', 'E', 'M', 'C', 'T', 'W', 'A', 'Pc']

print("=== VERIFICA MANTRA 12 POSIZIONI (2 TOP + 2 SCOMMESSE) ===")
for mPos in mantraPositions:
    pool = []
    for p in players:
        if not p.get('mantra') or p.get('is_injured'): continue
        if p.get('team') not in fix_map: continue
        posList = [s.strip() for s in p['mantra'].split(';')]
        if mPos in posList:
            pool.append(p)

    pool_top = [p for p in pool if calc_score(p, fix_map[p['team']]) > 0]
    pool_top.sort(key=lambda p: -calc_score(p, fix_map[p['team']]))

    top_selected = []
    seen_teams = set()
    for p in pool_top:
        if mPos == 'Por' and p['team'] in seen_teams: continue
        seen_teams.add(p['team'])
        top_selected.append(p)
        if len(top_selected) == 2: break

    top_ids = {p['id'] for p in top_selected}

    pool_bets = [p for p in pool if p['id'] not in top_ids and calc_opportunity_score(p, fix_map[p['team']]) > 0]
    pool_bets.sort(key=lambda p: -calc_opportunity_score(p, fix_map[p['team']]))

    bet_selected = []
    for p in pool_bets:
        if mPos == 'Por' and p['team'] in seen_teams: continue
        seen_teams.add(p['team'])
        bet_selected.append(p)
        if len(bet_selected) == 2: break

    top_names = [f"{p['name']} ({p.get('ovr')})" for p in top_selected]
    bet_names = [f"{p['name']} ({p.get('ovr')})" for p in bet_selected]
    print(f"[{mPos:3s}] Top: {', '.join(top_names)} | Scommesse: {', '.join(bet_names)}")
