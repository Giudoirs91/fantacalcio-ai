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
    if not m_info:
        return 0
    opp = m_info['opp']
    is_home = m_info['is_home']
    
    # Infortunato?
    if p.get('is_injured'):
        return -100
    
    tit = p.get('titolarita', 50)
    if tit < 50:
        return -50
    
    opp_tac = tactical.get(opp, {})
    opp_dif_stars = opp_tac.get('dif_stars', 3)
    opp_att_stars = opp_tac.get('att_stars', 3)
    
    opp_stats = team_stats.get(opp, {})
    opp_xga = opp_stats.get('xga_team', 5.0)
    opp_gc = opp_stats.get('goals_conceded_match', 1.2)
    opp_xg = opp_stats.get('xg_team', 5.0)
    
    role = p.get('role')
    ovr = p.get('ovr', 75)
    fm26 = p.get('fm_2627') or p.get('fm') or 6.0
    mv26 = p.get('mv_2627') or p.get('mv') or 6.0
    
    score = ovr * 0.4 + fm26 * 5.0 + mv26 * 3.0
    if is_home:
        score += 8.0
        
    if role in ['A', 'C']:
        score += (5 - opp_dif_stars) * 6.0
        score += (opp_gc - 1.0) * 8.0
        score += (opp_xga / 4.0) * 4.0
        if p.get('is_rigorista_1'): score += 12.0
        elif p.get('is_rigorista_2'): score += 6.0
        if p.get('is_punizioni') or p.get('is_corner'): score += 5.0
        if p.get('is_oop'): score += 10.0
        score += (p.get('xg90_2627', 0) or 0) * 20.0
        score += (p.get('xa90_2627', 0) or 0) * 15.0
    else: # P, D
        score += (5 - opp_att_stars) * 7.0
        score += max(0, (2.0 - opp_gc)) * 5.0
        if is_home: score += 4.0
        if p.get('is_oop'): score += 8.0
        if (p.get('rating_fotmob_2627') or 0) >= 7.0: score += 10.0
        if role == 'D':
            score += (p.get('xg90_2627', 0) or 0) * 15.0
            score += (p.get('xa90_2627', 0) or 0) * 15.0
        if role == 'P':
            score += (p.get('clean_sheets_2627', 0) or 0) * 6.0

    return score

ranked = sorted(players, key=calc_score, reverse=True)

print("=== CLASSICO (3 per ruolo) ===")
for role in ['P', 'D', 'C', 'A']:
    print(f"\n--- RUOLO {role} ---")
    sub = [p for p in ranked if p['role'] == role][:3]
    for i, p in enumerate(sub, 1):
        m = match_map.get(p['team'])
        loc = 'CASA' if m['is_home'] else 'TRASFERTA'
        print(f"#{i} {p['name']} ({p['team']}) vs {m['opp']} ({loc}) | Score: {calc_score(p):.1f} | FM: {p.get('fm_2627')} | OVR: {p.get('ovr')}")

print("\n=== MANTRA (3 per posizione) ===")
mantra_roles = ['Por', 'Dd', 'Ds', 'Dc', 'B', 'E', 'M', 'C', 'T', 'W', 'A', 'Pc']
for m_role in mantra_roles:
    print(f"\n--- POSIZIONE {m_role} ---")
    sub = [p for p in ranked if p.get('mantra') and m_role in p['mantra'].split(';')][:3]
    for i, p in enumerate(sub, 1):
        m = match_map.get(p['team'])
        loc = 'CASA' if m['is_home'] else 'TRASFERTA'
        print(f"#{i} {p['name']} ({p['team']}) [{p['mantra']}] vs {m['opp']} ({loc}) | Score: {calc_score(p):.1f} | FM: {p.get('fm_2627')}")
