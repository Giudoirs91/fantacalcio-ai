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

# 1. Attack Sides (% Left, Middle, Right) - Giornata 11 (Attack_side.png)
attack_sides_raw = [
    ("Lazio", 47, 24, 28),
    ("Genoa", 44, 24, 32),
    ("Sassuolo", 44, 24, 32),
    ("Bologna", 43, 23, 34),
    ("Inter", 40, 27, 33),
    ("AC Milan", 39, 27, 34),
    ("Monza", 38, 26, 36),
    ("Torino", 37, 30, 34),
    ("Napoli", 37, 28, 35),
    ("Cagliari", 36, 33, 32),
    ("Roma", 36, 25, 38),
    ("Udinese", 36, 27, 38),
    ("Lecce", 35, 26, 38),
    ("Venezia", 35, 25, 40),
    ("Fiorentina", 34, 28, 38),
    ("Frosinone", 34, 23, 43),
    ("Juventus", 33, 31, 37),
    ("Parma Calcio 1913", 32, 28, 40),
    ("Atalanta", 30, 31, 39),
    ("Como", 28, 31, 41)
]

# 2. Action Zones (% Own Third, Middle Third, Opposition Third) - Giornata 11 (Action_zones.png)
action_zones_raw = [
    ("Parma Calcio 1913", 36, 42, 22),
    ("Cagliari", 35, 45, 20),
    ("Torino", 33, 44, 23),
    ("AC Milan", 31, 47, 23),
    ("Genoa", 31, 41, 27),
    ("Sassuolo", 31, 45, 25),
    ("Venezia", 31, 43, 26),
    ("Napoli", 30, 43, 27),
    ("Atalanta", 30, 42, 29),
    ("Bologna", 28, 45, 28),
    ("Fiorentina", 28, 42, 31),
    ("Frosinone", 27, 38, 34),
    ("Lecce", 26, 45, 29),
    ("Monza", 26, 46, 28),
    ("Como", 25, 43, 31),
    ("Udinese", 25, 46, 30),
    ("Juventus", 24, 42, 35),
    ("Inter", 23, 44, 33),
    ("Roma", 23, 44, 33),
    ("Lazio", 23, 47, 30)
]

# 3. Shot Zones % (% in 6 Yards Box, in 18 Yards Box, Outside of Box) - Giornata 11 (Shot_zones.png)
shot_zones_pct_raw = [
    ("AC Milan", 14, 63, 23),
    ("Inter", 12, 60, 28),
    ("Lecce", 11, 50, 39),
    ("Napoli", 11, 59, 29),
    ("Roma", 10, 62, 28),
    ("Venezia", 10, 50, 40),
    ("Lazio", 9, 50, 41),
    ("Juventus", 9, 47, 44),
    ("Bologna", 8, 58, 34),
    ("Fiorentina", 8, 51, 41),
    ("Cagliari", 8, 58, 34),
    ("Parma Calcio 1913", 8, 60, 32),
    ("Frosinone", 7, 58, 35),
    ("Monza", 7, 58, 34),
    ("Torino", 6, 57, 37),
    ("Atalanta", 6, 65, 30),
    ("Como", 5, 60, 35),
    ("Sassuolo", 4, 54, 42),
    ("Udinese", 4, 57, 39),
    ("Genoa", 0, 62, 38)
]

# 4. Offensive Stats per game (Shots pg, Shots OT pg, Dribbles pg, Fouled pg, Rating) - Giornata 11 (stats_offensive.png)
offensive_stats_raw = [
    ("Inter", 21.3, 6.9, 6.3, 8.3, 6.86),
    ("Frosinone", 20.1, 6.8, 8.2, 12.0, 6.85),
    ("Roma", 19.4, 6.5, 9.3, 8.5, 6.97),
    ("Como", 18.9, 5.8, 8.1, 10.2, 6.74),
    ("Fiorentina", 16.9, 5.1, 8.4, 12.3, 6.47),
    ("Juventus", 16.4, 5.2, 7.8, 9.8, 6.68),
    ("Napoli", 15.5, 5.6, 4.7, 9.1, 6.64),
    ("Udinese", 14.5, 4.5, 6.5, 9.5, 6.41),
    ("Atalanta", 14.4, 5.4, 6.5, 8.5, 6.61),
    ("Lazio", 13.9, 4.7, 6.8, 11.3, 6.82),
    ("Venezia", 13.7, 4.0, 6.7, 8.3, 6.46),
    ("Bologna", 13.5, 4.5, 6.2, 13.7, 6.58),
    ("Monza", 13.5, 5.6, 7.0, 9.8, 6.47),
    ("Sassuolo", 12.6, 4.5, 7.1, 11.6, 6.41),
    ("Lecce", 12.1, 4.6, 6.9, 9.0, 6.47),
    ("Genoa", 11.7, 3.1, 6.3, 11.1, 6.51),
    ("AC Milan", 11.5, 4.5, 6.9, 11.4, 6.73),
    ("Cagliari", 10.9, 4.0, 5.8, 8.4, 6.55),
    ("Torino", 10.6, 3.5, 7.0, 10.8, 6.51),
    ("Parma Calcio 1913", 10.0, 3.2, 5.3, 12.5, 6.45)
]

# 5. Defensive Stats per game (Shots conceded pg, Tackles pg, Interceptions pg, Fouls pg, Offsides pg, Rating) - Giornata 11 (stats_defensive.png)
defensive_stats_raw = [
    ("Frosinone", 18.2, 20.3, 11.7, 14.6, 2.8, 6.85),
    ("Lecce", 14.7, 19.5, 8.6, 13.9, 1.5, 6.47),
    ("Genoa", 15.2, 17.9, 9.5, 9.8, 2.3, 6.51),
    ("Roma", 11.7, 17.1, 10.1, 10.9, 2.6, 6.97),
    ("Monza", 13.5, 16.9, 11.9, 12.1, 2.6, 6.47),
    ("Sassuolo", 16.7, 16.8, 7.7, 10.0, 2.6, 6.41),
    ("Como", 12.9, 16.6, 8.5, 8.0, 1.5, 6.74),
    ("Fiorentina", 13.9, 16.5, 7.8, 12.0, 1.3, 6.47),
    ("Bologna", 11.3, 16.3, 9.0, 13.1, 2.3, 6.58),
    ("Inter", 9.8, 16.3, 8.9, 9.6, 2.9, 6.86),
    ("AC Milan", 11.3, 16.0, 8.7, 9.9, 1.0, 6.73),
    ("Cagliari", 18.9, 15.9, 10.9, 12.5, 2.5, 6.55),
    ("Venezia", 16.2, 15.7, 7.5, 9.7, 2.6, 6.46),
    ("Atalanta", 18.5, 15.6, 9.5, 9.6, 1.2, 6.61),
    ("Torino", 15.3, 15.5, 8.6, 9.9, 1.8, 6.51),
    ("Juventus", 10.2, 15.5, 7.6, 12.5, 2.8, 6.68),
    ("Napoli", 16.3, 15.1, 6.5, 8.9, 2.6, 6.64),
    ("Parma Calcio 1913", 19.5, 15.0, 8.9, 10.5, 1.3, 6.45),
    ("Udinese", 15.5, 13.5, 7.6, 10.8, 1.2, 6.41),
    ("Lazio", 11.9, 13.4, 8.5, 11.1, 1.3, 6.82)
]

# 6. Goal Types Situations (Open Play, Counter Attack, Set Piece, Penalty, Own Goal) - Giornata 11 (Goal_types.png)
goal_types_raw = [
    ("Roma", 25, 1, 4, 0, 1),
    ("Lazio", 18, 3, 2, 1, 1),
    ("Inter", 17, 2, 5, 2, 2),
    ("AC Milan", 15, 2, 4, 1, 1),
    ("Frosinone", 15, 3, 5, 1, 0),
    ("Atalanta", 13, 1, 2, 1, 0),
    ("Torino", 12, 0, 2, 0, 1),
    ("Como", 12, 2, 3, 1, 0),
    ("Napoli", 11, 1, 4, 1, 1),
    ("Fiorentina", 10, 3, 3, 0, 1),
    ("Juventus", 9, 1, 5, 0, 0),
    ("Monza", 9, 2, 3, 2, 1),
    ("Bologna", 8, 1, 3, 3, 1),
    ("Genoa", 8, 1, 2, 0, 0),
    ("Sassuolo", 7, 4, 4, 0, 1),
    ("Udinese", 6, 1, 4, 0, 1),
    ("Parma Calcio 1913", 5, 1, 1, 1, 1),
    ("Venezia", 5, 3, 0, 0, 0),
    ("Cagliari", 4, 3, 1, 2, 0),
    ("Lecce", 2, 2, 7, 0, 1)
]

# 7. xG Statistics Exclude Penalties (xG, Goals*, xGDiff, Shots, xG/Shots, Rating) - Giornata 11 (xG_stats.png)
xg_stats_raw = [
    ("Inter", 29.44, 24, -5.44, 232, 0.13, 6.86),
    ("Roma", 28.75, 30, 1.25, 213, 0.13, 6.97),
    ("Frosinone", 22.14, 23, 0.86, 220, 0.10, 6.85),
    ("Como", 21.10, 17, -4.10, 207, 0.10, 6.74),
    ("AC Milan", 19.47, 21, 1.53, 124, 0.16, 6.73),
    ("Fiorentina", 18.16, 16, -2.16, 186, 0.10, 6.47),
    ("Napoli", 18.13, 16, -2.13, 169, 0.11, 6.64),
    ("Bologna", 17.78, 12, -5.78, 146, 0.12, 6.58),
    ("Lazio", 17.78, 23, 5.22, 150, 0.12, 6.82),
    ("Monza", 17.45, 14, -3.45, 145, 0.12, 6.47),
    ("Atalanta", 17.41, 16, -1.41, 157, 0.11, 6.61),
    ("Venezia", 17.25, 8, -9.25, 150, 0.11, 6.46),
    ("Juventus", 17.17, 15, -2.17, 180, 0.10, 6.68),
    ("Sassuolo", 16.04, 15, -1.04, 139, 0.12, 6.41),
    ("Lecce", 16.01, 11, -5.01, 133, 0.12, 6.47),
    ("Torino", 14.01, 14, -0.01, 117, 0.12, 6.51),
    ("Udinese", 13.75, 11, -2.75, 160, 0.09, 6.41),
    ("Cagliari", 12.41, 8, -4.41, 118, 0.11, 6.55),
    ("Genoa", 11.05, 11, -0.05, 128, 0.09, 6.51),
    ("Parma Calcio 1913", 9.80, 7, -2.80, 108, 0.09, 6.45)
]

# 8. Shot Directions (% Left, Middle, Right) - Giornata 11 (Shot_direction.png)
shot_directions_raw = [
    ("Genoa", 23, 64, 13),
    ("Atalanta", 23, 58, 18),
    ("Lazio", 21, 62, 17),
    ("Parma Calcio 1913", 21, 68, 11),
    ("Frosinone", 21, 62, 18),
    ("Udinese", 20, 61, 19),
    ("Napoli", 19, 73, 8),
    ("Cagliari", 18, 70, 12),
    ("Sassuolo", 18, 67, 15),
    ("Juventus", 18, 67, 16),
    ("Torino", 17, 71, 12),
    ("AC Milan", 17, 75, 8),
    ("Venezia", 17, 67, 16),
    ("Bologna", 16, 67, 17),
    ("Lecce", 16, 65, 19),
    ("Inter", 16, 71, 13),
    ("Monza", 16, 66, 18),
    ("Roma", 15, 69, 16),
    ("Como", 12, 71, 18),
    ("Fiorentina", 10, 64, 26)
]

# 9. Key Pass Types per game (Cross, Corner, Throughball, Freekick, Throwin, Other) - Giornata 11 (Keypass_type.png)
keypass_types_raw = [
    ("Roma", 4.3, 1.3, 0.5, 0.2, 0.0, 11.1),
    ("Inter", 4.5, 1.5, 0.3, 0.6, 0.2, 11.2),
    ("Frosinone", 4.0, 2.4, 0.5, 0.3, 0.0, 11.2),
    ("Lazio", 2.4, 0.6, 0.2, 0.2, 0.0, 8.1),
    ("Como", 3.9, 1.3, 0.4, 0.2, 0.0, 9.5),
    ("AC Milan", 2.9, 0.6, 0.5, 0.4, 0.0, 5.2),
    ("Juventus", 3.6, 1.1, 0.4, 0.3, 0.0, 8.5),
    ("Napoli", 3.7, 1.5, 0.5, 0.1, 0.0, 7.6),
    ("Atalanta", 2.5, 0.9, 0.2, 0.2, 0.0, 8.2),
    ("Bologna", 3.1, 1.5, 0.1, 0.3, 0.1, 6.2),
    ("Cagliari", 2.5, 1.3, 0.3, 0.5, 0.0, 5.8),
    ("Torino", 2.0, 0.5, 0.4, 0.5, 0.0, 4.9),
    ("Genoa", 2.0, 0.8, 0.1, 0.4, 0.2, 6.0),
    ("Lecce", 2.4, 1.0, 0.3, 0.2, 0.2, 5.5),
    ("Fiorentina", 2.4, 0.6, 0.5, 0.2, 0.1, 9.5),
    ("Monza", 2.6, 1.0, 0.3, 0.4, 0.0, 7.0),
    ("Venezia", 3.0, 1.2, 0.5, 0.1, 0.1, 6.5),
    ("Parma Calcio 1913", 2.9, 0.7, 0.3, 1.0, 0.1, 4.8),
    ("Udinese", 2.8, 0.9, 0.5, 0.3, 0.1, 7.7),
    ("Sassuolo", 1.5, 0.7, 0.4, 0.2, 0.0, 8.0)
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

    # 8. Shot Directions %
    for t_raw, l, m, r in shot_directions_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['shot_directions'] = {
            'left_pct': l,
            'middle_pct': m,
            'right_pct': r
        }

    # 9. Key Pass Types per game
    for t_raw, cr, co, tb, fk, ti, ot in keypass_types_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['keypass_types_pg'] = {
            'cross': cr,
            'corner': co,
            'throughball': tb,
            'freekick': fk,
            'throwin': ti,
            'other': ot
        }

    out_file = os.path.join(CONFIG_DIR, "whoscored_teams_2627.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(teams_db, f, indent=2, ensure_ascii=False)
        
    pos_file = os.path.join(CONFIG_DIR, "team_positional_stats.json")
    with open(pos_file, 'w', encoding='utf-8') as f:
        json.dump(teams_db, f, indent=2, ensure_ascii=False)

    print(f"✓ Salvati {out_file} e {pos_file} con dati Giornata 11 per tutte le 20 squadre:")
    print("  • Attack Sides (% Corsie)")
    print("  • Action Zones (% Terzi di Campo)")
    print("  • Shot Zones (% Aree di Tiro)")
    print("  • Offensive Team Stats (Tiri, Dribbling, Falli Subiti)")
    print("  • Defensive Team Stats (Tiri Concessi, Tackle, Intercetti, Fuorigioco)")
    print("  • Situational Goal Types (Azione, Contropiede, Palle Inattive, Rigori)")
    print("  • Non-Penalty xG & xG/Shot Efficiency")
    print("  • Shot Directions (% Direzioni Tiro)")
    print("  • Key Pass Types (Cross, Corner, Filtranti, Punizioni)")

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
                tactical_db[t]['whoscored_shot_directions'] = data.get('shot_directions', {})
                tactical_db[t]['whoscored_keypass_types'] = data.get('keypass_types_pg', {})
        with open(tac_path, 'w', encoding='utf-8') as f:
            json.dump(tactical_db, f, indent=2, ensure_ascii=False)
        print("✓ tactical_db.json arricchito con tutte le 9 dimensioni tattiche WhoScored G11!")

    return teams_db

if __name__ == "__main__":
    build_whoscored_teams_db()
