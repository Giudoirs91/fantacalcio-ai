import json

players = json.load(open('data/processed/processed_players_master.json', encoding='utf-8'))
cal = json.load(open('config/calendario_serie_a_2026_27.json', encoding='utf-8'))
team_stats = json.load(open('data/raw/team_stats_2026_27.json', encoding='utf-8'))

g6 = next(r for r in cal if r['giornata'] == 6)
fix_map = {}
for m in g6['matches']:
    fix_map[m['home']] = {'opp': m['away'], 'isHome': True}
    fix_map[m['away']] = {'opp': m['home'], 'isHome': False}

print("=== CANDIDATI SCOMMESSE G6 (OVR <= 80, titolarita >= 55) ===")

def calc_bet_score(p, m):
    tm = p.get('team')
    opp = m['opp']
    is_home = m['isHome']
    role = p.get('role')
    tit = int(p.get('titolarita') or 0)
    ovr = float(p.get('ovr') or 70)
    fm = float(p.get('fm_2627') or p.get('fm') or 6.0)
    gol = int(p.get('gol_2627') or 0)
    ass = int(p.get('assist_2627') or 0)

    my_stats = team_stats.get(tm, {})
    opp_stats = team_stats.get(opp, {})
    opp_xga = float(opp_stats.get('xga_team') or 6.0)
    opp_gc = float(opp_stats.get('goals_conceded_match') or 1.5)
    opp_xg = float(opp_stats.get('xg_team') or 6.0)

    score = 50.0 + (fm * 3.0) + (tit * 0.15)
    if is_home: score += 8.0
    if p.get('is_rigorista_1'): score += 18.0
    if p.get('is_oop'): score += 15.0
    if p.get('is_punizioni'): score += 10.0

    if role in ['C', 'A']:
        score += (opp_xga / 6.0) * 15.0 + (opp_gc * 6.0)
        score += (gol * 6.0) + (ass * 4.0)
    elif role == 'D':
        score += (opp_xga / 6.0) * 10.0
        if is_home: score += 5.0
    elif role == 'P':
        # Low opp xg is good for underdog keeper
        if opp_xg < 5.0: score += 15.0
        if is_home: score += 10.0

    return round(score, 1)

by_role = {'P': [], 'D': [], 'C': [], 'A': []}
for p in players:
    if p.get('is_injured'): continue
    tit = int(p.get('titolarita') or 0)
    ovr = float(p.get('ovr') or 70)
    fvm = float(p.get('fvm') or 1)
    tm = p.get('team')
    if tm not in fix_map: continue
    # Scommessa: OVR <= 80 oppure FVM <= 25 (non un top tier globale)
    if ovr <= 80 and tit >= 55:
        sc = calc_bet_score(p, fix_map[tm])
        by_role[p['role']].append((p, sc))

for role, plist in by_role.items():
    plist.sort(key=lambda x: x[1], reverse=True)
    print(f"\n--- TOP SCOMMESSE RUOLO {role} ---")
    for p, sc in plist[:6]:
        rig = " [RIG]" if p.get('is_rigorista_1') else ""
        oop = " [OOP]" if p.get('is_oop') else ""
        fk = " [PIA]" if p.get('is_punizioni') else ""
        print(f"{p['name']} ({p['team']}): score={sc}, OVR={p.get('ovr')}, FVM={p.get('fvm')}, tit={p.get('titolarita')}%, vs {fix_map[p['team']]['opp']} (home={fix_map[p['team']]['isHome']}){rig}{oop}{fk}")
