import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(ROOT_DIR, "config")

# Standardize team names
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

# 1. Attack Sides (% Left, Middle, Right)
attack_sides_raw = [
    ("Lazio", 45, 25, 30),
    ("Bologna", 42, 23, 35),
    ("Sassuolo", 42, 25, 34),
    ("Genoa", 41, 26, 34),
    ("Monza", 40, 26, 33),
    ("AC Milan", 39, 27, 34),
    ("Inter", 38, 29, 33),
    ("Lecce", 37, 27, 36),
    ("Napoli", 37, 28, 35),
    ("Roma", 36, 24, 39),
    ("Fiorentina", 35, 28, 38),
    ("Venezia", 35, 25, 40),
    ("Torino", 34, 32, 34),
    ("Udinese", 34, 28, 39),
    ("Cagliari", 33, 34, 33),
    ("Frosinone", 33, 24, 42),
    ("Juventus", 31, 31, 38),
    ("Parma Calcio 1913", 30, 29, 42),
    ("Atalanta", 29, 32, 39),
    ("Como", 26, 34, 40)
]

# 2. Action Zones (% Own Third, Middle Third, Opposition Third)
action_zones_raw = [
    ("Cagliari", 37, 44, 19),
    ("Parma Calcio 1913", 36, 43, 21),
    ("Genoa", 32, 41, 27),
    ("Bologna", 31, 43, 25),
    ("Torino", 31, 45, 23),
    ("Frosinone", 31, 37, 31),
    ("Venezia", 29, 42, 30),
    ("Napoli", 29, 41, 29),
    ("AC Milan", 29, 46, 24),
    ("Sassuolo", 29, 43, 28),
    ("Atalanta", 28, 42, 30),
    ("Monza", 27, 44, 29),
    ("Fiorentina", 26, 42, 32),
    ("Lecce", 26, 47, 27),
    ("Inter", 25, 44, 32),
    ("Lazio", 25, 45, 30),
    ("Udinese", 25, 45, 30),
    ("Como", 25, 43, 32),
    ("Roma", 24, 43, 32),
    ("Juventus", 21, 42, 36)
]

# 3. Goal Situations Per Game
goal_situations_raw = [
    ("Roma", 2.3, 2.0, 0.2, 0.2, 0.0, 0.0, 2.3, 6.96),
    ("Inter", 3.0, 2.0, 0.2, 0.7, 0.2, 0.0, 2.8, 6.94),
    ("Lazio", 1.8, 1.3, 0.2, 0.2, 0.2, 0.0, 1.7, 6.80),
    ("Frosinone", 1.5, 1.0, 0.2, 0.3, 0.0, 0.0, 1.5, 6.77),
    ("AC Milan", 1.8, 1.3, 0.3, 0.0, 0.0, 0.2, 1.7, 6.75),
    ("Como", 1.5, 1.0, 0.2, 0.3, 0.0, 0.0, 1.5, 6.74),
    ("Juventus", 1.5, 1.0, 0.0, 0.5, 0.0, 0.0, 1.5, 6.73),
    ("Cagliari", 1.0, 0.5, 0.2, 0.2, 0.2, 0.0, 0.8, 6.69),
    ("Napoli", 1.7, 1.0, 0.2, 0.3, 0.2, 0.0, 1.5, 6.67),
    ("Sassuolo", 1.7, 0.7, 0.3, 0.7, 0.0, 0.0, 1.7, 6.61),
    ("Atalanta", 1.3, 1.0, 0.0, 0.3, 0.0, 0.0, 1.3, 6.53),
    ("Bologna", 0.8, 0.7, 0.0, 0.2, 0.0, 0.0, 0.8, 6.50),
    ("Udinese", 1.5, 0.8, 0.2, 0.5, 0.0, 0.0, 1.5, 6.48),
    ("Lecce", 1.0, 0.3, 0.0, 0.7, 0.0, 0.0, 1.0, 6.45),
    ("Torino", 1.2, 0.8, 0.0, 0.3, 0.0, 0.0, 1.2, 6.44),
    ("Monza", 1.5, 0.8, 0.0, 0.5, 0.2, 0.0, 1.3, 6.43),
    ("Genoa", 0.8, 0.5, 0.2, 0.2, 0.0, 0.0, 0.8, 6.40),
    ("Fiorentina", 1.2, 0.7, 0.3, 0.0, 0.0, 0.2, 1.0, 6.40),
    ("Venezia", 0.8, 0.5, 0.3, 0.0, 0.0, 0.0, 0.8, 6.35),
    ("Parma Calcio 1913", 0.7, 0.5, 0.2, 0.0, 0.0, 0.0, 0.7, 6.33)
]

# 4. Total Goal Types
goal_types_raw = [
    ("Inter", 12, 1, 4, 1, 0),
    ("Roma", 12, 1, 1, 0, 0),
    ("Lazio", 8, 1, 1, 1, 0),
    ("AC Milan", 8, 2, 0, 0, 1),
    ("Napoli", 6, 1, 2, 1, 0),
    ("Juventus", 6, 0, 3, 0, 0),
    ("Atalanta", 6, 0, 2, 0, 0),
    ("Como", 6, 1, 2, 0, 0),
    ("Frosinone", 6, 1, 2, 0, 0),
    ("Torino", 5, 0, 2, 0, 0),
    ("Udinese", 5, 1, 3, 0, 0),
    ("Monza", 5, 0, 3, 1, 0),
    ("Bologna", 4, 0, 1, 0, 0),
    ("Fiorentina", 4, 2, 0, 0, 1),
    ("Sassuolo", 4, 2, 4, 0, 0),
    ("Venezia", 3, 2, 0, 0, 0),
    ("Genoa", 3, 1, 1, 0, 0),
    ("Cagliari", 3, 1, 1, 1, 0),
    ("Parma Calcio 1913", 3, 1, 0, 0, 0),
    ("Lecce", 2, 0, 4, 0, 0)
]

# 5. Team xG Stats (Exclude Penalties)
xg_stats_raw = [
    ("Inter", 16.65, 17, 0.35, 134, 0.12, 6.94),
    ("Roma", 15.53, 14, -1.53, 112, 0.14, 6.96),
    ("Como", 12.43, 9, -3.43, 136, 0.09, 6.74),
    ("Monza", 11.76, 8, -3.76, 85, 0.14, 6.43),
    ("AC Milan", 11.58, 10, -1.58, 75, 0.15, 6.75),
    ("Venezia", 11.42, 5, -6.42, 88, 0.13, 6.35),
    ("Juventus", 11.37, 9, -2.37, 110, 0.10, 6.73),
    ("Sassuolo", 11.21, 10, -1.21, 96, 0.12, 6.61),
    ("Frosinone", 9.75, 9, -0.75, 101, 0.10, 6.77),
    ("Lazio", 9.65, 10, 0.35, 80, 0.12, 6.80),
    ("Napoli", 9.54, 9, -0.54, 87, 0.11, 6.67),
    ("Bologna", 9.15, 5, -4.15, 76, 0.12, 6.50),
    ("Fiorentina", 8.77, 6, -2.77, 97, 0.09, 6.40),
    ("Torino", 7.96, 7, -0.96, 59, 0.13, 6.44),
    ("Lecce", 7.66, 6, -1.66, 61, 0.13, 6.45),
    ("Udinese", 7.15, 9, 1.85, 86, 0.08, 6.48),
    ("Atalanta", 6.54, 8, 1.46, 81, 0.08, 6.53),
    ("Genoa", 5.76, 5, -0.76, 68, 0.08, 6.40),
    ("Parma Calcio 1913", 5.20, 4, -1.20, 50, 0.10, 6.33),
    ("Cagliari", 5.18, 5, -0.18, 57, 0.09, 6.69)
]

# 6. Referees Statistics
referees_raw = [
    ("Luca Pairetto", 3, 19.00, 0.71, 0.00, 2.67, 8, 0.00, 0),
    ("Fabio Maresca", 3, 28.33, 0.82, 0.00, 6.00, 18, 0.00, 0),
    ("Francesco Fourneau", 3, 25.33, 0.78, 0.00, 4.67, 14, 0.00, 0),
    ("Matteo Marcenaro", 3, 23.67, 0.70, 0.00, 4.00, 12, 0.00, 0),
    ("Valerio Crezzini", 3, 20.00, 0.52, 0.00, 1.00, 3, 0.00, 0),
    ("Maurizio Mariani", 2, 26.00, 0.84, 0.00, 5.00, 10, 0.00, 0),
    ("Marco Guida", 2, 22.50, 0.73, 0.00, 3.00, 6, 0.00, 0),
    ("Michael Fabbri", 2, 14.50, 0.44, 0.00, 4.00, 8, 0.50, 1),
    ("Daniele Doveri", 2, 21.50, 0.80, 0.00, 2.00, 4, 0.00, 0),
    ("Davide Massa", 2, 21.00, 0.68, 0.00, 3.00, 6, 0.00, 0),
    ("Marco Di Bello", 2, 20.00, 0.58, 0.00, 3.00, 6, 0.00, 0),
    ("Daniele Chiffi", 2, 23.00, 0.52, 0.00, 3.50, 7, 0.00, 0),
    ("Federico La Penna", 2, 28.00, 0.82, 0.00, 2.50, 5, 0.00, 0),
    ("Gianluca Manganiello", 2, 18.50, 0.58, 0.00, 3.00, 6, 0.00, 0),
    ("Juan Luca Sacchi", 2, 21.50, 0.67, 0.00, 4.00, 8, 0.00, 0),
    ("Antonio Rapuano", 2, 22.00, 0.71, 0.50, 3.50, 7, 0.50, 1),
    ("Simone Sozza", 2, 18.00, 0.55, 1.00, 4.50, 9, 0.00, 0),
    ("Luca Zufferli", 2, 19.50, 0.87, 0.00, 2.00, 4, 0.00, 0),
    ("Daniele Perenzoni", 2, 22.50, 0.54, 0.50, 3.50, 7, 0.00, 0),
    ("Ermanno Feliciani", 2, 22.00, 0.76, 0.50, 2.50, 5, 0.00, 0)
]

def build_whoscored_teams_db():
    teams_db = {}
    
    for t_raw, l, m, r in attack_sides_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['attack_sides'] = {
            'left_pct': l,
            'middle_pct': m,
            'right_pct': r
        }
        
    for t_raw, o, m, opp in action_zones_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['action_zones'] = {
            'own_third_pct': o,
            'middle_third_pct': m,
            'opposition_third_pct': opp
        }
        
    for t_raw, tot, op, cnt, sp, pen, own, norm, rat in goal_situations_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['goal_situations_pg'] = {
            'total_pg': tot,
            'open_play_pg': op,
            'counter_attack_pg': cnt,
            'set_piece_pg': sp,
            'penalty_scored_pg': pen,
            'own_goal_pg': own,
            'whoscored_rating': rat
        }
        
    for t_raw, op, cnt, sp, pen, own in goal_types_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['goal_types_total'] = {
            'open_play': op,
            'counter_attack': cnt,
            'set_piece': sp,
            'penalty': pen,
            'own_goal': own
        }
        
    for t_raw, xg, gls, xg_diff, shots, xg_per_shot, rat in xg_stats_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['xg_non_penalty'] = {
            'npxg': xg,
            'goals_excl_pen': gls,
            'npxg_diff': xg_diff,
            'shots': shots,
            'npxg_per_shot': xg_per_shot,
            'whoscored_rating': rat
        }
        
    out_file = os.path.join(CONFIG_DIR, "whoscored_teams_2627.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(teams_db, f, indent=2, ensure_ascii=False)
    print(f"✓ Salvato {out_file} con dati completi per 20 squadre!")
    return teams_db

def build_referees_db():
    referees_db = {}
    for name, apps, fouls_pg, ft_ratio, pen_pg, yel_pg, yel_tot, red_pg, red_tot in referees_raw:
        clean_key = name.strip()
        referees_db[clean_key] = {
            'name': name,
            'apps': apps,
            'fouls_per_game': fouls_pg,
            'fouls_tackles_ratio': ft_ratio,
            'penalties_per_game': pen_pg,
            'yellow_cards_per_game': yel_pg,
            'total_yellow_cards': yel_tot,
            'red_cards_per_game': red_pg,
            'total_red_cards': red_tot,
            'severity_tier': 'ALTA' if yel_pg >= 4.5 or red_tot > 0 else ('MEDIA' if yel_pg >= 3.0 else 'BASSA')
        }
    out_file = os.path.join(CONFIG_DIR, "referee_stats.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(referees_db, f, indent=2, ensure_ascii=False)
    print(f"✓ Salvato {out_file} con dati per {len(referees_db)} arbitri di Serie A!")
    return referees_db

if __name__ == "__main__":
    build_whoscored_teams_db()
    build_referees_db()
