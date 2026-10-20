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

# 1. Attack Sides (% Left, Middle, Right) - Giornata 7 (Image 1)
attack_sides_raw = [
    ("Lazio", 45, 25, 30),
    ("Bologna", 42, 23, 35),
    ("Genoa", 42, 25, 33),
    ("Sassuolo", 41, 25, 34),
    ("Monza", 39, 26, 35),
    ("Inter", 38, 28, 33),
    ("AC Milan", 38, 28, 35),
    ("Napoli", 38, 27, 35),
    ("Roma", 37, 24, 39),
    ("Torino", 36, 31, 33),
    ("Lecce", 36, 27, 37),
    ("Venezia", 36, 25, 39),
    ("Fiorentina", 34, 29, 38),
    ("Cagliari", 34, 33, 33),
    ("Udinese", 34, 27, 39),
    ("Frosinone", 33, 25, 43),
    ("Juventus", 31, 31, 38),
    ("Parma Calcio 1913", 31, 29, 41),
    ("Atalanta", 29, 32, 39),
    ("Como", 26, 33, 41)
]

# 2. Shots Zones Per Game (Total, OutOfBox, SixYardBox, PenaltyArea, Rating) - Giornata 7 (Image 2)
shots_zones_pg_raw = [
    ("Roma", 18.1, 5.1, 1.7, 11.3, 6.96),
    ("Inter", 21.7, 6.4, 2.1, 13.1, 6.92),
    ("Lazio", 12.9, 5.9, 1.1, 5.9, 6.83),
    ("Como", 21.7, 8.0, 1.0, 12.7, 6.78),
    ("Frosinone", 17.4, 6.6, 1.4, 9.4, 6.77),
    ("AC Milan", 12.3, 2.7, 1.6, 8.0, 6.73),
    ("Juventus", 17.0, 8.0, 1.7, 7.3, 6.65),
    ("Napoli", 16.7, 4.9, 1.6, 10.3, 6.64),
    ("Cagliari", 10.6, 3.9, 0.7, 6.0, 6.61),
    ("Monza", 14.3, 4.0, 1.1, 9.1, 6.56),
    ("Lecce", 11.1, 3.6, 1.4, 6.1, 6.55),
    ("Sassuolo", 15.7, 6.3, 0.7, 8.7, 6.55),
    ("Torino", 9.7, 3.7, 0.7, 5.3, 6.52),
    ("Atalanta", 13.3, 4.9, 0.7, 7.7, 6.52),
    ("Bologna", 12.4, 4.1, 1.3, 7.0, 6.47),
    ("Venezia", 14.0, 5.0, 1.9, 7.1, 6.44),
    ("Udinese", 14.3, 5.0, 0.3, 9.0, 6.42),
    ("Fiorentina", 16.6, 6.3, 1.1, 9.1, 6.39),
    ("Genoa", 11.1, 3.6, 0.0, 7.6, 6.37),
    ("Parma Calcio 1913", 10.7, 3.1, 1.0, 6.6, 6.33)
]

# 3. Shot Zones % (% in 6 Yards Box, in 18 Yards Box, Outside of Box) - Giornata 7 (Image 3)
shot_zones_pct_raw = [
    ("Venezia", 13, 51, 36),
    ("AC Milan", 13, 66, 21),
    ("Lecce", 13, 55, 32),
    ("Bologna", 10, 56, 33),
    ("Inter", 10, 61, 30),
    ("Juventus", 10, 43, 47),
    ("Lazio", 9, 46, 46),
    ("Roma", 9, 62, 28),
    ("Napoli", 9, 62, 28),
    ("Parma Calcio 1913", 9, 61, 29),
    ("Monza", 8, 64, 28),
    ("Frosinone", 8, 54, 38),
    ("Torino", 7, 54, 38),
    ("Fiorentina", 7, 55, 38),
    ("Cagliari", 7, 57, 36),
    ("Como", 5, 59, 37),
    ("Atalanta", 5, 58, 37),
    ("Sassuolo", 5, 55, 40),
    ("Udinese", 2, 63, 35),
    ("Genoa", 0, 68, 32)
]

# 4. Action Zones (% Own Third, Middle Third, Opposition Third) - Giornata 7 (Image 4)
action_zones_raw = [
    ("Cagliari", 35, 45, 20),
    ("Parma Calcio 1913", 34, 43, 23),
    ("Torino", 33, 44, 23),
    ("Bologna", 32, 44, 24),
    ("Genoa", 32, 41, 28),
    ("Venezia", 31, 42, 27),
    ("Frosinone", 30, 37, 33),
    ("Sassuolo", 30, 42, 27),
    ("AC Milan", 29, 46, 24),
    ("Napoli", 28, 42, 30),
    ("Atalanta", 28, 41, 31),
    ("Como", 28, 42, 31),
    ("Fiorentina", 26, 42, 34),
    ("Lecce", 26, 46, 27),
    ("Monza", 26, 44, 29),
    ("Udinese", 26, 45, 29),
    ("Lazio", 25, 45, 29),
    ("Inter", 24, 44, 32),
    ("Roma", 24, 44, 32),
    ("Juventus", 22, 42, 36)
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

    # 2. Shots Zones Per Game
    for t_raw, tot, out_b, six_y, pen_a, rat in shots_zones_pg_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['shots_zones_pg'] = {
            'total': tot,
            'out_of_box': out_b,
            'six_yard_box': six_y,
            'penalty_area': pen_a,
            'rating': rat
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
        
    # 4. Action Zones %
    for t_raw, o, m, opp in action_zones_raw:
        t = normalize_team(t_raw)
        if t not in teams_db: teams_db[t] = {}
        teams_db[t]['action_zones'] = {
            'own_third_pct': o,
            'middle_third_pct': m,
            'opposition_third_pct': opp
        }
        
    out_file = os.path.join(CONFIG_DIR, "whoscored_teams_2627.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(teams_db, f, indent=2, ensure_ascii=False)
        
    pos_file = os.path.join(CONFIG_DIR, "team_positional_stats.json")
    with open(pos_file, 'w', encoding='utf-8') as f:
        json.dump(teams_db, f, indent=2, ensure_ascii=False)

    print(f"✓ Salvati {out_file} e {pos_file} con dati per 20 squadre (Attack Sides, Shots Zones, Shot Zones %, Action Zones %)")

    # Aggiorna anche tactical_db.json
    tac_path = os.path.join(CONFIG_DIR, "tactical_db.json")
    if os.path.exists(tac_path):
        with open(tac_path, 'r', encoding='utf-8') as f:
            tactical_db = json.load(f)
        for t, data in teams_db.items():
            if t in tactical_db:
                tactical_db[t]['whoscored_attack_sides'] = data.get('attack_sides', {})
                tactical_db[t]['whoscored_action_zones'] = data.get('action_zones', {})
                tactical_db[t]['whoscored_shots_zones_pg'] = data.get('shots_zones_pg', {})
                tactical_db[t]['whoscored_shot_zones_pct'] = data.get('shot_zones_pct', {})
        with open(tac_path, 'w', encoding='utf-8') as f:
            json.dump(tactical_db, f, indent=2, ensure_ascii=False)
        print(f"✓ tactical_db.json arricchito con le metriche posizionali e tattiche!")

    return teams_db

if __name__ == "__main__":
    build_whoscored_teams_db()
