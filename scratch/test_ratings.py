import json

players = json.load(open('data/processed/processed_players_master.json', encoding='utf-8'))
tactical = json.load(open('config/tactical_db.json', encoding='utf-8'))
team_stats = json.load(open('data/raw/fotmob_team_stats_2026_27.json', encoding='utf-8'))
cal = json.load(open('data/processed/calendario_serie_a_2026_27.json', encoding='utf-8'))

r5 = next(x for x in cal if x['giornata'] == 5)
match_map = {m['home']: {'opp': m['away'], 'is_home': True} for m in r5['matches']}
match_map.update({m['away']: {'opp': m['home'], 'is_home': False} for m in r5['matches']})

def calc_score(p):
    team = p.get('team')
    m_info = match_map.get(team)
    if not m_info or p.get('is_injured') or (p.get('titolarita', 50) < 50):
        return -999
    
    opp = m_info['opp']
    is_home = m_info['is_home']
    role = p.get('role')
    
    opp_tac = tactical.get(opp, {})
    opp_dif_stars = opp_tac.get('dif_stars', 3)
    opp_att_stars = opp_tac.get('att_stars', 3)
    
    opp_stats = team_stats.get(opp, {})
    opp_xga = opp_stats.get('xga_team', 5.0)
    opp_gc = opp_stats.get('goals_conceded_match', 1.3)
    opp_xg = opp_stats.get('xg_team', 5.0)
    
    my_stats = team_stats.get(team, {})
    my_cs = my_stats.get('clean_sheets', 0)
    my_xga = my_stats.get('xga_team', 5.0)

    ovr = p.get('ovr', 75)
    fm = p.get('fm_2627') or p.get('fm') or 6.0
    mv = p.get('mv_2627') or p.get('mv') or 6.0

    if role == 'P':
        base = 70.0 + (ovr * 0.2) + (fm * 3.0)
        opp_danger = (opp_xg - 4.5) * 8.0 + (opp_att_stars - 3) * 14.0
        base -= opp_danger
        if my_cs >= 2: base += 14.0
        elif my_cs == 1: base += 7.0
        base -= (my_xga / 4.0) * 5.0
        if is_home: base += 12.0
        if opp_att_stars <= 2: base += 20.0
        if opp_att_stars >= 5: base -= 40.0
        return round(base, 1)

    elif role == 'D':
        base = 65.0 + (ovr * 0.25) + (fm * 4.0) + (mv * 3.0)
        if opp_att_stars >= 5: base -= 18.0
        elif opp_att_stars <= 2: base += 14.0
        if is_home: base += 8.0
        if p.get('is_oop'): base += 15.0
        if p.get('is_punizioni') or p.get('is_corner'): base += 8.0
        base += (p.get('xg90_2627', 0) or 0) * 18.0
        base += (p.get('xa90_2627', 0) or 0) * 18.0
        base += (p.get('gol_2627', 0) or 0) * 8.0
        base += (p.get('assist_2627', 0) or 0) * 6.0
        return round(base, 1)

    else:
        base = 60.0 + (ovr * 0.25) + (fm * 4.5) + (mv * 2.5)
        base += (5 - opp_dif_stars) * 7.0
        base += (opp_xga - 4.5) * 4.0
        base += (opp_gc - 1.0) * 6.0
        if is_home: base += 8.0
        if p.get('is_rigorista_1'): base += 16.0
        elif p.get('is_rigorista_2'): base += 8.0
        if p.get('is_oop'): base += 12.0
        if p.get('is_punizioni') or p.get('is_corner'): base += 6.0
        base += (p.get('xg90_2627', 0) or 0) * 22.0
        base += (p.get('xa90_2627', 0) or 0) * 18.0
        base += (p.get('gol_2627', 0) or 0) * 7.0
        base += (p.get('assist_2627', 0) or 0) * 5.0
        return round(base, 1)

ranked = sorted(players, key=calc_score, reverse=True)

print("=== CLASSICO ===")
for r in ['P', 'D', 'C', 'A']:
    sub = [p for p in ranked if p['role'] == r][:3]
    items = [f"{p['name']} ({p['team']} vs {match_map[p['team']]['opp']}) [{calc_score(p)}]" for p in sub]
    print(f"{r}: {', '.join(items)}")

print("\n=== MANTRA ===")
for pos in ['Por', 'Dd', 'Ds', 'Dc', 'B', 'E', 'M', 'C', 'T', 'W', 'A', 'Pc']:
    sub = [p for p in ranked if p.get('mantra') and pos in p['mantra'].split(';')][:3]
    items = [f"{p['name']} ({p['team']} vs {match_map[p['team']]['opp']})" for p in sub]
    print(f"{pos:3}: {', '.join(items)}")
