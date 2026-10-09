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
    oppBox = float(oppStats.get('touches_opp_box') or 80.0)

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
    elif role == 'D':
        score = 60.0 + (ovr * 0.22) + (fm * 3.5) + (mv * 3.0)
        boxDiff = (oppBox - 80.0) / 20.0
        score -= boxDiff * 4.0
        score += (oppXga / LEAGUE_AVG_XGA) * 6.0
        if isHome: score += 5.0
        if player.get('is_oop'): score += 8.0
        if player.get('is_punizioni') or player.get('is_corner'): score += 5.0
        score += (gol * 8.0) + (ass * 5.0)
        return round(score, 1)
    elif role == 'C':
        score = 55.0 + (ovr * 0.25) + (fm * 4.0) + (xg90 * 25.0) + (xa90 * 20.0)
        score += (oppXga / LEAGUE_AVG_XGA) * 8.0
        score += (oppGc * 5.0)
        if isHome: score += 4.0
        if player.get('is_rigorista_1'): score += 12.0
        if player.get('is_punizioni'): score += 6.0
        if player.get('is_oop'): score += 7.0
        score += (gol * 6.0) + (ass * 4.0)
        return round(score, 1)
    else:
        score = 50.0 + (ovr * 0.30) + (fm * 4.5)
        xgaRatio = oppXga / LEAGUE_AVG_XGA
        score += (oppGc * 8.0) + (xgaRatio * 10.0)
        if isHome: score += 5.0
        if player.get('is_rigorista_1'): score += 15.0
        if player.get('is_punizioni') or player.get('is_corner'): score += 6.0
        score += (xg90 * xgaRatio) * 25.0
        score += (xa90 * xgaRatio) * 20.0
        score += (gol * 7.0) + (ass * 5.0)
        return round(score, 1)

# Formula specifica per scommesse predittive (giocatori meno forti / low-cost con alto differenziale)
def calc_opportunity_score(player, matchInfo):
    tit = float(player.get('titolarita') if player.get('titolarita') is not None else 0)
    if tit < 50: return -500.0
    if player.get('role') == 'P' and tit < 70: return -500.0

    ovr = float(player.get('ovr') or 70)
    # Una scommessa DEVE essere un giocatore NON top-tier (OVR <= 80 oppure FVM <= 28)
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

    # Opportunity score: penalizza OVR elevato, premia il valore per credito / sorpresa di giornata
    score = 50.0 + (fm * 3.5) + (tit * 0.12)
    if isHome: score += 8.0
    if player.get('is_rigorista_1'): score += 20.0
    if player.get('is_oop'): score += 16.0
    if player.get('is_punizioni'): score += 10.0

    if role == 'P':
        # Portiere sorpresa di giornata: in casa o contro attacco spuntato
        if oppXg < 5.5: score += 18.0
        if isHome: score += 10.0
    elif role == 'D':
        score += (oppXga / LEAGUE_AVG_XGA) * 12.0 + (oppGc * 6.0)
        score += (gol * 10.0) + (ass * 7.0)
    else:
        score += (oppXga / LEAGUE_AVG_XGA) * 16.0 + (oppGc * 8.0)
        score += (gol * 8.0) + (ass * 5.0)

    return round(score, 1)

print("=== SELEZIONE CLASSIC: 2 TOP + 2 SCOMMESSE PER RUOLO ===")
for r in ['P', 'D', 'C', 'A']:
    pool = [p for p in players if p.get('role') == r and p.get('team') in fix_map and not p.get('is_injured')]
    
    # 1. Top 2
    pool_top = [p for p in pool if calc_score(p, fix_map[p['team']]) > 0]
    pool_top.sort(key=lambda p: -calc_score(p, fix_map[p['team']]))
    
    top_selected = []
    seen_teams = set()
    for p in pool_top:
        if r == 'P' and p['team'] in seen_teams: continue
        seen_teams.add(p['team'])
        top_selected.append(p)
        if len(top_selected) == 2: break
        
    top_ids = {p['id'] for p in top_selected}

    # 2. Scommesse 2
    pool_bets = [p for p in pool if p['id'] not in top_ids and calc_opportunity_score(p, fix_map[p['team']]) > 0]
    pool_bets.sort(key=lambda p: -calc_opportunity_score(p, fix_map[p['team']]))

    bet_selected = []
    for p in pool_bets:
        if r == 'P' and p['team'] in seen_teams: continue
        seen_teams.add(p['team'])
        bet_selected.append(p)
        if len(bet_selected) == 2: break

    print(f"\nReparto {r}:")
    print(f"  🥇 TOP 1: {top_selected[0]['name']} ({top_selected[0]['team']}, OVR {top_selected[0]['ovr']}) - score {calc_score(top_selected[0], fix_map[top_selected[0]['team']])}")
    print(f"  🥈 TOP 2: {top_selected[1]['name']} ({top_selected[1]['team']}, OVR {top_selected[1]['ovr']}) - score {calc_score(top_selected[1], fix_map[top_selected[1]['team']])}")
    print(f"  🔮 SCOMMESSA 1: {bet_selected[0]['name']} ({bet_selected[0]['team']}, OVR {bet_selected[0]['ovr']}, FVM {bet_selected[0]['fvm']}) - opp_score {calc_opportunity_score(bet_selected[0], fix_map[bet_selected[0]['team']])}")
    print(f"  💎 SCOMMESSA 2: {bet_selected[1]['name']} ({bet_selected[1]['team']}, OVR {bet_selected[1]['ovr']}, FVM {bet_selected[1]['fvm']}) - opp_score {calc_opportunity_score(bet_selected[1], fix_map[bet_selected[1]['team']])}")
