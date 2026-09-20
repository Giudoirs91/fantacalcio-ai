import json

players = json.load(open('data/processed/processed_players_master.json', encoding='utf-8'))
tactical = json.load(open('config/tactical_db.json', encoding='utf-8'))
team_stats = json.load(open('data/raw/fotmob_team_stats_2026_27.json', encoding='utf-8'))
cal = json.load(open('data/processed/calendario_serie_a_2026_27.json', encoding='utf-8'))

r5 = next(x for x in cal if x['giornata'] == 5)
match_map = {m['home']: {'opp': m['away'], 'is_home': True} for m in r5['matches']}
match_map.update({m['away']: {'opp': m['home'], 'is_home': False} for m in r5['matches']})

AVG_XGA = 6.03
AVG_XG = 6.04
AVG_GC = 1.54

def calc_fotmob_rating(p):
    team = p.get('team')
    m_info = match_map.get(team)
    if not m_info or p.get('is_injured') or (p.get('titolarita', 50) < 50):
        return -999.0
    
    opp = m_info['opp']
    is_home = m_info['is_home']
    role = p.get('role')
    
    my_s = team_stats.get(team, {})
    opp_s = team_stats.get(opp, {})
    
    my_xg = my_s.get('xg_team', AVG_XG)
    my_xga = my_s.get('xga_team', AVG_XGA)
    my_gc = my_s.get('goals_conceded_match', 1.5)
    my_cs = my_s.get('clean_sheets', 0)
    
    opp_xg = opp_s.get('xg_team', AVG_XG)
    opp_xga = opp_s.get('xga_team', AVG_XGA)
    opp_gc = opp_s.get('goals_conceded_match', 1.5)
    opp_bc = opp_s.get('big_chances', 5.0)
    opp_box = opp_s.get('touches_opp_box', 80.0)
    
    ovr = p.get('ovr', 75)
    fm = p.get('fm_2627') or p.get('fm') or 6.0
    mv = p.get('mv_2627') or p.get('mv') or 6.0
    xg90 = p.get('xg90_2627') or p.get('xg90') or 0.0
    xa90 = p.get('xa90_2627') or p.get('xa90') or 0.0
    gol = p.get('gol_2627', 0)
    ass = p.get('assist_2627', 0)
    
    # 1. PORTIERI: Clean Sheet & Defense Rating (CSDR)
    if role == 'P':
        # Base affidabilità portiere
        score = 65.0 + (ovr * 0.18) + (fm * 2.5)
        
        # Solidità della propria difesa
        cs_factor = (my_cs * 8.0) - (my_gc * 6.0) - (my_xga / AVG_XGA * 5.0)
        score += cs_factor
        
        # Fattore campo: +18% probabilità clean sheet storico a domicilio
        if is_home:
            score += 10.0
            
        # Minaccia offensiva avversaria: xG e Big Chances avversarie
        # Penalizzazione non lineare se opp_xg supera la media
        xg_diff = opp_xg - AVG_XG
        if xg_diff > 0:
            score -= (xg_diff ** 1.35) * 8.5 # Penalità esponenziale per attacchi devastanti (Inter, Roma)
        else:
            score += abs(xg_diff) * 6.0 # Bonus se l'avversario ha attacco debole (Lecce, Genoa, Venezia)
            
        score -= (opp_bc / 4.0) * 3.0
        return round(score, 1)

    # 2. DIFENSORI: Modificatore & Flank Exploitation Index (MCAI & FEI)
    elif role == 'D':
        score = 60.0 + (ovr * 0.22) + (fm * 3.5) + (mv * 3.0)
        
        # Matchup difensivo: meno l'avversario tocca palla in area, meno malus/cartellini
        box_diff = (opp_box - 80.0) / 20.0
        score -= box_diff * 4.0
        
        # Vulnerabilità della difesa avversaria per terzini/saltatori
        score += (opp_xga / AVG_XGA) * 6.0
        
        if is_home: score += 6.0
        
        # Status Tattico OOP (Terzino impiegato come quinto o ala)
        if p.get('is_oop'): score += 14.0
        if p.get('is_punizioni') or p.get('is_corner'): score += 7.0
        
        # Metriche offensive del difensore
        score += xg90 * 20.0 + xa90 * 20.0 + gol * 8.0 + ass * 6.0
        return round(score, 1)

    # 3. CENTROCAMPISTI & ATTACCANTI: Expected Finishing Conversion (EFC) & KBAS
    else:
        score = 55.0 + (ovr * 0.22) + (fm * 4.0) + (mv * 2.5)
        
        # Moltiplicatore scientifico: quanto concede la difesa avversaria rispetto alla media
        xga_ratio = opp_xga / AVG_XGA # es. Venezia (10.1/6.03 = 1.67x)
        gc_ratio = opp_gc / AVG_GC # es. Venezia (2.8/1.54 = 1.81x)
        score += (xga_ratio - 1.0) * 22.0
        score += (gc_ratio - 1.0) * 16.0
        
        if is_home: score += 7.0
        
        # Bonus rigorista matematico (+0.76 xG atteso)
        if p.get('is_rigorista_1'): score += 18.0
        elif p.get('is_rigorista_2'): score += 8.0
        
        if p.get('is_oop'): score += 12.0
        if p.get('is_punizioni') or p.get('is_corner'): score += 6.0
        
        score += (xg90 * xga_ratio) * 25.0
        score += (xa90 * xga_ratio) * 20.0
        score += gol * 7.0 + ass * 5.0
        return round(score, 1)

ranked = sorted(players, key=calc_fotmob_rating, reverse=True)

print("=== VERIFICA CALCOLO FOTMOB DETERMINISTICO ===")
print("\n--- PORTIERI (P) ---")
for p in [x for x in ranked if x['role'] == 'P'][:5]:
    m = match_map[p['team']]
    print(f"{p['name']:15} ({p['team']:10} vs {m['opp']:10} {'[C]' if m['is_home'] else '[T]'}) | Score: {calc_fotmob_rating(p)}")

sv = next(x for x in players if x['name'] == 'Svilar')
print(f"Svilar vs Inter: {calc_fotmob_rating(sv)}")

print("\n--- ATTACCANTI (A) ---")
for p in [x for x in ranked if x['role'] == 'A'][:5]:
    m = match_map[p['team']]
    print(f"{p['name']:15} ({p['team']:10} vs {m['opp']:10} {'[C]' if m['is_home'] else '[T]'}) | Score: {calc_fotmob_rating(p)}")

print("\n--- CENTROCAMPISTI (C) ---")
for p in [x for x in ranked if x['role'] == 'C'][:5]:
    m = match_map[p['team']]
    print(f"{p['name']:15} ({p['team']:10} vs {m['opp']:10} {'[C]' if m['is_home'] else '[T]'}) | Score: {calc_fotmob_rating(p)}")
