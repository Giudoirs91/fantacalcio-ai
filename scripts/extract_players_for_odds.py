import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

with open('data/raw/fotmob_team_stats_2026_27.json', 'r', encoding='utf-8') as f:
    teams_stats = json.load(f)

# Quick player stats lookup
def get_p_stats(p_name, team_sub):
    res = []
    for p in players:
        if team_sub.lower() in p['team'].lower() and p_name.lower() in p['name'].lower():
            mins = p.get('minuti_2627', 0)
            sh = p.get('tiri_2627', 0)
            sot = p.get('tiri_porta_2627', 0)
            g = p.get('gol_2627', 0)
            xg = p.get('xg_2627', 0.0)
            fouls = p.get('fouls_2627', 0)
            fouls_drawn = p.get('falli_subiti_2627', 0)
            amm = p.get('amm_2627', 0)
            starts = p.get('starts_2627', 0)
            pres = p.get('presenze_2627', 0)
            sot90 = (sot / mins * 90) if mins >= 100 else 0
            sh90 = (sh / mins * 90) if mins >= 100 else 0
            res.append({
                'name': p['name'], 'team': p['team'], 'mins': mins, 'starts': starts, 'pres': pres,
                'goals': g, 'xg': xg, 'shots': sh, 'sot': sot, 'sh90': round(sh90, 2), 'sot90': round(sot90, 2),
                'fouls': fouls, 'fouls_drawn': fouls_drawn, 'amm': amm, 'titolarita': p.get('titolarita')
            })
    return res

print("=== STATISTICHE GIOCATORI CHIAVE SASSUOLO - LAZIO ===")
for p_n, tm in [('Berardi', 'Sassuolo'), ('Lauriente', 'Sassuolo'), ('Pinamonti', 'Sassuolo'), ('Mulattieri', 'Sassuolo'), ('Boloca', 'Sassuolo'), ('Thorstvedt', 'Sassuolo'),
                ('Zaccagni', 'Lazio'), ('Castellanos', 'Lazio'), ('Dia', 'Lazio'), ('Isaksen', 'Lazio'), ('Guendouzi', 'Lazio'), ('Tavares', 'Lazio'), ('Romagnoli', 'Lazio')]:
    st = get_p_stats(p_n, tm)
    for s in st:
        print(f"{s['name']} ({s['team']}): Mins {s['mins']}' ({s['starts']} tit), Gol {s['goals']} (xG {s['xg']}), Tiri {s['shots']} ({s['sh90']}/90), In porta {s['sot']} ({s['sot90']}/90), Falli Fatti {s['fouls']}, Subiti {s['fouls_drawn']}, Amm {s['amm']}")

print("\n=== STATISTICHE GIOCATORI CHIAVE ROMA - CAGLIARI ===")
for p_n, tm in [('Dybala', 'Roma'), ('Dovbyk', 'Roma'), ('Soule', 'Roma'), ('Pellegrini', 'Roma'), ('Mancini', 'Roma'), ('Cristante', 'Roma'), ('Kone', 'Roma'), ('Ndicka', 'Roma'), ('Hermoso', 'Roma'),
                ('Piccoli', 'Cagliari'), ('Luvumbo', 'Cagliari'), ('Marin', 'Cagliari'), ('Deiola', 'Cagliari'), ('Mina', 'Cagliari'), ('Zortea', 'Cagliari'), ('Gaetano', 'Cagliari')]:
    st = get_p_stats(p_n, tm)
    for s in st:
        print(f"{s['name']} ({s['team']}): Mins {s['mins']}' ({s['starts']} tit), Gol {s['goals']} (xG {s['xg']}), Tiri {s['shots']} ({s['sh90']}/90), In porta {s['sot']} ({s['sot90']}/90), Falli Fatti {s['fouls']}, Subiti {s['fouls_drawn']}, Amm {s['amm']}")
