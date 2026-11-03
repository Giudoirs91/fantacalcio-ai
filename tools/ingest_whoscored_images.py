import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(ROOT_DIR, "config")

TEAM_NORM = {
    'lazio': 'Lazio',
    'bologna': 'Bologna',
    'sassuolo': 'Sassuolo',
    'genoa': 'Genoa',
    'monza': 'Monza',
    'ac milan': 'Milan',
    'milan': 'Milan',
    'inter': 'Inter',
    'lecce': 'Lecce',
    'napoli': 'Napoli',
    'roma': 'Roma',
    'fiorentina': 'Fiorentina',
    'venezia': 'Venezia',
    'torino': 'Torino',
    'udinese': 'Udinese',
    'cagliari': 'Cagliari',
    'frosinone': 'Frosinone',
    'juventus': 'Juventus',
    'parma calcio 1913': 'Parma',
    'parma': 'Parma',
    'atalanta': 'Atalanta',
    'como': 'Como'
}

def normalize_team(name):
    clean = name.strip().lower()
    return TEAM_NORM.get(clean, name.strip())

# 1. Attack Sides (% Left, Middle, Right) - Giornata 10 (Attack_side.png)
attack_sides_raw = [
    ("Lazio", 48, 24, 28),
    ("Sassuolo", 45, 24, 31),
    ("Bologna", 43, 22, 35),
    ("Genoa", 43, 23, 33),
    ("Inter", 40, 28, 32),
    ("AC Milan", 39, 26, 34),
    ("Monza", 38, 26, 35),
    ("Roma", 37, 25, 38),
    ("Napoli", 37, 28, 35),
    ("Torino", 36, 31, 34),
    ("Cagliari", 36, 33, 31),
    ("Udinese", 36, 27, 37),
    ("Frosinone", 35, 23, 42),
    ("Venezia", 35, 25, 40),
    ("Lecce", 35, 26, 39),
    ("Fiorentina", 34, 28, 38),
    ("Parma Calcio 1913", 33, 28, 39),
    ("Juventus", 32, 31, 37),
    ("Atalanta", 29, 31, 40),
    ("Como", 28, 32, 40)
]

# 2. Action Zones (% Own Third, Middle Third, Opposition Third) - Giornata 10 (action_sides.png)
action_zones_raw = [
    ("Cagliari", 34, 45, 20),
    ("Parma Calcio 1913", 34, 44, 22),
    ("Torino", 33, 44, 23),
    ("Genoa", 32, 41, 27),
    ("Venezia", 31, 43, 26),
    ("Napoli", 30, 42, 27),
    ("Sassuolo", 30, 44, 26),
    ("AC Milan", 29, 47, 23),
    ("Bologna", 28, 46, 26),
    ("Atalanta", 28, 41, 30),
    ("Frosinone", 28, 39, 34),
    ("Monza", 27, 46, 27),
    ("Lecce", 27, 44, 29),
    ("Fiorentina", 26, 42, 32),
    ("Como", 25, 43, 32),
    ("Udinese", 25, 46, 30),
    ("Roma", 24, 43, 33),
    ("Juventus", 24, 43, 35),
    ("Lazio", 23, 47, 30),
    ("Inter", 22, 44, 33)
]

# 3. Shot Zones % (% in 6 Yards Box, in 18 Yards Box, Outside of Box) - Giornata 10 (Shot_zones.png)
shot_zones_pct_raw = [
    ("AC Milan", 14, 63, 23),
    ("Lecce", 12, 51, 37),
    ("Inter", 11, 60, 28),
    ("Napoli", 11, 61, 28),
    ("Venezia", 11, 49, 40),
    ("Lazio", 10, 50, 40),
    ("Bologna", 9, 57, 34),
    ("Roma", 9, 61, 30),
    ("Juventus", 9, 46, 45),
    ("Parma Calcio 1913", 9, 59, 32),
    ("Cagliari", 8, 58, 35),
    ("Fiorentina", 7, 52, 41),
    ("Monza", 7, 58, 35),
    ("Torino", 6, 56, 39),
    ("Atalanta", 6, 64, 30),
    ("Frosinone", 6, 58, 36),
    ("Como", 5, 59, 35),
    ("Sassuolo", 4, 54, 42),
    ("Udinese", 3, 56, 40),
    ("Genoa", 0, 65, 35)
]

# 4. Offensive Stats per game (Shots pg, Shots OT pg, Dribbles pg, Fouled pg, Rating) - Giornata 10 (stats_offensive.png)
offensive_stats_raw = [
    ("Inter", 22.0, 7.2, 6.7, 8.5, 6.86),
    ("Como", 20.3, 6.3, 8.7, 9.9, 6.78),
    ("Frosinone", 19.2, 6.6, 7.5, 12.0, 6.86),
    ("Roma", 18.5, 6.3, 8.8, 8.1, 6.95),
    ("Fiorentina", 16.4, 5.0, 8.6, 12.0, 6.46),
    ("Juventus", 16.2, 5.1, 7.3, 9.3, 6.68),
    ("Napoli", 15.6, 5.6, 4.8, 9.1, 6.64),
    ("Udinese", 14.7, 4.4, 6.8, 9.3, 6.43),
    ("Atalanta", 14.5, 5.2, 6.6, 8.5, 6.56),
    ("Lazio", 13.8, 4.6, 6.7, 11.3, 6.83),
    ("Venezia", 13.6, 4.0, 6.9, 8.5, 6.42),
    ("Sassuolo", 13.3, 4.8, 7.2, 12.1, 6.43),
    ("Lecce", 12.7, 5.0, 7.0, 8.9, 6.47),
    ("Monza", 12.6, 5.5, 6.7, 10.2, 6.47),
    ("AC Milan", 12.0, 4.7, 6.9, 11.2, 6.72),
    ("Bologna", 11.6, 4.0, 6.0, 14.0, 6.55),
    ("Genoa", 11.2, 2.9, 5.5, 11.1, 6.53),
    ("Torino", 10.8, 3.7, 7.1, 10.4, 6.51),
    ("Cagliari", 10.6, 4.0, 5.7, 8.2, 6.52),
    ("Parma Calcio 1913", 9.9, 3.3, 5.3, 12.4, 6.44)
]

# 5. Defensive Stats per game (Shots conceded pg, Tackles pg, Interceptions pg, Fouls pg, Offsides pg, Rating) - Giornata 10 (stats_defensive.png)
defensive_stats_raw = [
    ("Frosinone", 18.6, 20.4, 11.9, 14.9, 3.0, 6.86),
    ("Lecce", 15.3, 19.7, 8.3, 13.7, 1.6, 6.47),
    ("Genoa", 16.1, 18.0, 9.9, 9.4, 2.2, 6.53),
    ("Bologna", 11.3, 17.0, 9.5, 13.1, 2.4, 6.55),
    ("Roma", 12.3, 17.0, 10.5, 11.2, 2.8, 6.95),
    ("Como", 12.8, 17.0, 8.5, 8.2, 1.4, 6.78),
    ("Inter", 10.3, 16.6, 8.6, 9.3, 2.4, 6.86),
    ("Monza", 13.5, 16.6, 11.9, 12.2, 2.8, 6.47),
    ("Fiorentina", 13.5, 16.2, 8.0, 11.6, 1.4, 6.46),
    ("Cagliari", 17.9, 16.2, 10.5, 12.4, 2.5, 6.52),
    ("Sassuolo", 15.6, 16.2, 8.1, 9.7, 2.8, 6.43),
    ("AC Milan", 10.7, 15.8, 8.3, 9.6, 1.0, 6.72),
    ("Venezia", 16.5, 15.6, 7.9, 9.6, 2.5, 6.42),
    ("Juventus", 9.0, 15.4, 7.9, 11.9, 3.0, 6.68),
    ("Torino", 16.2, 15.3, 8.1, 9.8, 1.9, 6.51),
    ("Atalanta", 18.2, 14.9, 9.1, 10.0, 1.3, 6.56),
    ("Parma Calcio 1913", 18.1, 14.7, 9.2, 10.5, 1.4, 6.44),
    ("Napoli", 16.4, 14.4, 6.5, 8.6, 2.7, 6.64),
    ("Udinese", 15.6, 14.0, 8.0, 11.3, 1.0, 6.43),
    ("Lazio", 11.6, 13.9, 8.4, 11.1, 1.3, 6.83)
]

# 6. Goal Types Situations (Open Play, Counter Attack, Set Piece, Penalty, Own Goal) - Giornata 10 (Goal_types.png)
goal_types_raw = [
    ("Roma", 23, 1, 4, 0, 0),
    ("Lazio", 18, 2, 2, 1, 1),
    ("Inter", 16, 1, 5, 2, 2),
    ("Frosinone", 15, 3, 5, 1, 0),
    ("AC Milan", 13, 2, 4, 1, 1),
    ("Torino", 12, 0, 2, 0, 0),
    ("Atalanta", 12, 1, 2, 1, 0),
    ("Como", 12, 2, 3, 1, 0),
    ("Napoli", 11, 1, 4, 1, 0),
    ("Fiorentina", 10, 3, 1, 0, 1),
    ("Monza", 9, 2, 3, 2, 1),
    ("Juventus", 9, 0, 4, 0, 0),
    ("Bologna", 8, 0, 3, 2, 1),
    ("Genoa", 8, 1, 1, 0, 0),
    ("Sassuolo", 7, 4, 4, 0, 1),
    ("Udinese", 6, 1, 4, 0, 0),
    ("Parma Calcio 1913", 5, 1, 1, 0, 1),
    ("Cagliari", 4, 2, 1, 2, 0),
    ("Venezia", 3, 3, 0, 0, 0),
    ("Lecce", 2, 2, 7, 0, 0)
]

# 7. xG Statistics Exclude Penalties (xG, Goals*, xGDiff, Shots, xG/Shots, Rating) - Giornata 10 (xG_stats.png)
xg_stats_raw = [
    ("Inter", 27.30, 22, -5.30, 218, 0.13, 6.86),
    ("Roma", 25.40, 28, 2.60, 185, 0.14, 6.95),
    ("Como", 20.86, 17, -3.86, 202, 0.10, 6.78),
    ("Frosinone", 19.88, 23, 3.12, 191, 0.10, 6.86),
    ("AC Milan", 18.56, 19, 0.44, 118, 0.16, 6.72),
    ("Lazio", 16.87, 22, 5.13, 135, 0.12, 6.83),
    ("Napoli", 16.25, 16, -0.25, 154, 0.11, 6.64),
    ("Atalanta", 16.04, 15, -1.04, 144, 0.11, 6.56),
    ("Fiorentina", 15.80, 14, -1.80, 164, 0.10, 6.46),
    ("Lecce", 15.79, 11, -4.79, 127, 0.12, 6.47),
    ("Venezia", 15.66, 6, -9.66, 135, 0.12, 6.42),
    ("Sassuolo", 15.65, 15, -0.65, 133, 0.12, 6.43),
    ("Monza", 15.44, 14, -1.44, 123, 0.13, 6.47),
    ("Bologna", 15.08, 11, -4.08, 114, 0.13, 6.55),
    ("Juventus", 14.68, 13, -1.68, 162, 0.09, 6.68),
    ("Torino", 13.24, 14, 0.76, 108, 0.12, 6.51),
    ("Udinese", 12.53, 11, -1.53, 147, 0.09, 6.43),
    ("Cagliari", 11.27, 7, -4.27, 104, 0.11, 6.52),
    ("Genoa", 9.81, 10, 0.19, 111, 0.09, 6.53),
    ("Parma Calcio 1913", 8.85, 7, -1.85, 98, 0.09, 6.44)
]

def build_whoscored_teams_db():
    teams_db = {}
    
    # 1. Attack Sides
    for t_raw, l, m, r in attack_sides_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['attack_sides'] = {
            'left_pct': l,
            'middle_pct': m,
            'right_pct': r
        }

    # 2. Action Zones %
    for t_raw, o, m, opp in action_zones_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['action_zones'] = {
            'own_third_pct': o,
            'middle_third_pct': m,
            'opposition_third_pct': opp
        }

    # 3. Shot Zones %
    for t_raw, six_pct, pen_pct, out_pct in shot_zones_pct_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['shot_zones_pct'] = {
            'six_yard_box_pct': six_pct,
            'penalty_area_pct': pen_pct,
            'outside_box_pct': out_pct
        }

    # 4. Offensive Stats
    for t_raw, sh, sot, drb, fld, rat in offensive_stats_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['offensive_stats'] = {
            'shots_pg': sh,
            'shots_on_target_pg': sot,
            'dribbles_pg': drb,
            'fouled_pg': fld,
            'rating': rat
        }
        # Backward compatibility for shots_zones_pg
        if 'shots_zones_pg' not in teams_db[t]:
            teams_db[t]['shots_zones_pg'] = {}
        teams_db[t]['shots_zones_pg']['total'] = sh
        teams_db[t]['shots_zones_pg']['rating'] = rat

    # 5. Defensive Stats
    for t_raw, sh_c, tkl, intc, fls, off, rat in defensive_stats_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['defensive_stats'] = {
            'shots_conceded_pg': sh_c,
            'tackles_pg': tkl,
            'interceptions_pg': intc,
            'fouls_committed_pg': fls,
            'offsides_won_pg': off,
            'rating': rat
        }

    # 6. Goal Types Situations
    for t_raw, op, ca, sp, pen, og in goal_types_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['goal_situations_pg'] = {
            'open_play': op,
            'counter_attack': ca,
            'set_piece': sp,
            'penalty': pen,
            'own_goal': og
        }

    # 7. xG Non Penalty Stats
    for t_raw, xg, gls, xg_d, shots, xg_sh, rat in xg_stats_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['xg_non_penalty'] = {
            'xg': xg,
            'goals': gls,
            'xg_diff': xg_d,
            'shots': shots,
            'xg_per_shot': xg_sh,
            'rating': rat
        }

    out_file = os.path.join(CONFIG_DIR, "whoscored_teams_2627.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(teams_db, f, indent=2, ensure_ascii=False)
        
    pos_file = os.path.join(CONFIG_DIR, "team_positional_stats.json")
    with open(pos_file, 'w', encoding='utf-8') as f:
        json.dump(teams_db, f, indent=2, ensure_ascii=False)

    print(f"✓ Salvati {out_file} e {pos_file} con dati Giornata 10 per tutte le 20 squadre:")
    print("  • Attack Sides (% Corsie)")
    print("  • Action Zones (% Terzi di Campo)")
    print("  • Shot Zones (% Aree di Tiro)")
    print("  • Offensive Team Stats (Tiri, Dribbling, Falli Subiti)")
    print("  • Defensive Team Stats (Tiri Concessi, Tackle, Intercetti, Fuorigioco)")
    print("  • Situational Goal Types (Azione, Contropiede, Palle Inattive, Rigori)")
    print("  • Non-Penalty xG & xG/Shot Efficiency")

    # Aggiorna anche tactical_db.json
    tac_path = os.path.join(CONFIG_DIR, "tactical_db.json")
    if os.path.exists(tac_path):
        with open(tac_path, 'r', encoding='utf-8') as f:
            tactical_db = json.load(f)
        for t, data in teams_db.items():
            if t in tactical_db:
                tactical_db[t]['whoscored_attack_sides'] = data.get('attack_sides', {})
                tactical_db[t]['whoscored_action_zones'] = data.get('action_zones', {})
                tactical_db[t]['whoscored_shot_zones_pct'] = data.get('shot_zones_pct', {})
                tactical_db[t]['whoscored_offensive_stats'] = data.get('offensive_stats', {})
                tactical_db[t]['whoscored_defensive_stats'] = data.get('defensive_stats', {})
                tactical_db[t]['whoscored_goal_situations'] = data.get('goal_situations_pg', {})
                tactical_db[t]['whoscored_xg'] = data.get('xg_non_penalty', {})
        with open(tac_path, 'w', encoding='utf-8') as f:
            json.dump(tactical_db, f, indent=2, ensure_ascii=False)
        print("✓ tactical_db.json arricchito con tutte le 7 dimensioni tattiche WhoScored G10!")

    return teams_db

if __name__ == "__main__":
    build_whoscored_teams_db()
