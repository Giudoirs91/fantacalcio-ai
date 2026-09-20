import sys
import json
import os
import re
from collections import defaultdict
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
from src.player_matcher import clean_text, match_player_name

with open(os.path.join(ROOT_DIR, 'data', 'processed', 'processed_players_master.json'), 'r', encoding='utf-8') as f:
    players = json.load(f)

with open(os.path.join(ROOT_DIR, 'config', 'tactical_db.json'), 'r', encoding='utf-8') as f:
    tac = json.load(f)

# Raggruppa giocatori per squadra
team_players = defaultdict(list)
for p in players:
    team_players[p['team']].append(p)

# Analisi Match Reports per cambi
reports_csv = os.path.join(ROOT_DIR, 'data', 'raw', 'match_reports_players_g1_g2.csv')
sub_pairs_count = defaultdict(int)
if os.path.exists(reports_csv):
    df_rep = pd.read_csv(reports_csv)
    for (g, m, t), grp in df_rep.groupby(['giornata', 'match_name', 'team']):
        starters_off = grp[(grp['is_starter'] == True) & (grp['minutes'] < grp['minutes'].max())]
        subs_on = grp[(grp['is_starter'] == False) & (grp['minutes'] > 0)]
        max_m = grp['minutes'].max()
        matched = set()
        for _, sub in subs_on.iterrows():
            sub_m = sub['minutes']
            for _, starter in starters_off.iterrows():
                if starter['player_name'] in matched:
                    continue
                if abs((starter['minutes'] + sub_m) - max_m) <= 1:
                    sub_pairs_count[(t.upper(), starter['player_name'].upper(), sub['player_name'].upper())] += 1
                    matched.add(starter['player_name'])
                    break

print(f"Coppie di sostituzioni distinte estratte dai report: {len(sub_pairs_count)}")

# Test mapping completo per tutte le 20 squadre
pairings = {}

for team_name, t_players in team_players.items():
    t_tac = tac.get(team_name, {})
    ballottaggi = t_tac.get('ballottaggi', [])
    lineup = t_tac.get('lineup', [])
    
    # 1. Portieri: 1° Portiere <-> 2° Portiere
    gks = [p for p in t_players if p['role'] == 'P']
    gks.sort(key=lambda x: (x.get('titolarita', 0), x.get('fvm', 0), x.get('ovr', 0)), reverse=True)
    if len(gks) >= 2:
        p1, p2 = gks[0], gks[1]
        pairings[p1['id']] = {
            'coppia_nome': p2['name'],
            'coppia_id': p2['id'],
            'coppia_ruolo': 'P',
            'coppia_tipo': 'RISERVA',
            'coppia_dettaglio': f"2° Portiere ({p2['name']})"
        }
        pairings[p2['id']] = {
            'coppia_nome': p1['name'],
            'coppia_id': p1['id'],
            'coppia_ruolo': 'P',
            'coppia_tipo': 'TITOLARE',
            'coppia_dettaglio': f"Vice di {p1['name']}"
        }
        if len(gks) >= 3:
            p3 = gks[2]
            pairings[p3['id']] = {
                'coppia_nome': p1['name'],
                'coppia_id': p1['id'],
                'coppia_ruolo': 'P',
                'coppia_tipo': 'TITOLARE',
                'coppia_dettaglio': f"3° Portiere ({p1['name']})"
            }

    # 2. Ballottaggi espliciti da Tactical DB (SOLO SE STESSO RUOLO FANTACALCIO)
    for b in ballottaggi:
        p_name = b.get('player', '')
        p_pct = b.get('pct', 50)
        vs_str = b.get('vs', '')
        
        p_obj = next((p for p in t_players if match_player_name(p['name'], p_name)), None)
        if not p_obj:
            continue
            
        vs_matches = re.findall(r'([A-Za-z\s\.\'\-]+?)\s*\((\d+)%\)', vs_str)
        if vs_matches:
            for rival_name, rival_pct in vs_matches:
                rival_name = rival_name.strip()
                rival_pct = int(rival_pct)
                
                r_obj = next((p for p in t_players if match_player_name(p['name'], rival_name)), None)
                # RIGOROSO: Devono avere lo stesso ruolo Fantacalcio (P-P, D-D, C-C, A-A)
                if r_obj and r_obj['role'] == p_obj['role']:
                    tipo = 'BALLOTTAGGIO'
                    if p_pct >= 65:
                        tipo = 'RISERVA'
                    elif p_pct <= 35:
                        tipo = 'TITOLARE'
                    
                    det = f"{p_pct}% vs {rival_pct}% ({r_obj['name']})"
                    if p_obj['id'] not in pairings:
                        pairings[p_obj['id']] = {
                            'coppia_nome': r_obj['name'],
                            'coppia_id': r_obj['id'],
                            'coppia_ruolo': r_obj['role'],
                            'coppia_tipo': tipo,
                            'coppia_dettaglio': det
                        }
                    
                    if r_obj['id'] not in pairings:
                        r_tipo = 'TITOLARE' if tipo == 'RISERVA' else ('RISERVA' if tipo == 'TITOLARE' else 'BALLOTTAGGIO')
                        r_det = f"{rival_pct}% vs {p_pct}% ({p_obj['name']})"
                        pairings[r_obj['id']] = {
                            'coppia_nome': p_obj['name'],
                            'coppia_id': p_obj['id'],
                            'coppia_ruolo': p_obj['role'],
                            'coppia_tipo': r_tipo,
                            'coppia_dettaglio': r_det
                        }
                    break

    # 3. Match Reports: Staffette reali (SOLO SE STESSO RUOLO FANTACALCIO)
    team_upper = team_name.upper()
    for (t_up, st_name, sb_name), count in sorted(sub_pairs_count.items(), key=lambda x: x[1], reverse=True):
        if t_up != team_upper and team_upper not in t_up and t_up not in team_upper:
            continue
        st_obj = next((p for p in t_players if match_player_name(p['name'], st_name)), None)
        sb_obj = next((p for p in t_players if match_player_name(p['name'], sb_name)), None)
        
        # RIGOROSO: Lo stesso ruolo è obbligatorio! (Un attaccante NON può essere sostituito da un centrocampista)
        if st_obj and sb_obj and st_obj['role'] == sb_obj['role']:
            if st_obj['id'] not in pairings and sb_obj['id'] not in pairings:
                pairings[st_obj['id']] = {
                    'coppia_nome': sb_obj['name'],
                    'coppia_id': sb_obj['id'],
                    'coppia_ruolo': sb_obj['role'],
                    'coppia_tipo': 'STAFFETTA',
                    'coppia_dettaglio': f"Staffetta ({count} cambi)"
                }
                pairings[sb_obj['id']] = {
                    'coppia_nome': st_obj['name'],
                    'coppia_id': st_obj['id'],
                    'coppia_ruolo': st_obj['role'],
                    'coppia_tipo': 'TITOLARE',
                    'coppia_dettaglio': f"Subentra a {st_obj['name']}"
                }

    # 4. Fallback per titolari dell'11 ancora senza sostituto: assegna il miglior panchinaro dello STESSO ruolo e Mantra affine
    starters_unmapped = [p for p in t_players if p.get('is_in_11') and p['id'] not in pairings and p['role'] != 'P']
    bench_unmapped = [p for p in t_players if not p.get('is_in_11') and p['id'] not in pairings and p['role'] != 'P']
    bench_unmapped.sort(key=lambda x: (x.get('fvm', 0), x.get('ovr', 0)), reverse=True)
    
    used_bench = set()
    for st in starters_unmapped:
        # Cerca panchinaro con stesso ruolo e preferenza per posizione Mantra simile (es. Pc con Pc, Dc con Dc, etc.)
        st_mantra = set((st.get('mantra') or '').split(';'))
        
        best_candidate = None
        # Primo tentativo: stesso ruolo + Mantra compatibile
        for b in bench_unmapped:
            if b['role'] == st['role'] and b['id'] not in used_bench:
                b_mantra = set((b.get('mantra') or '').split(';'))
                if st_mantra.intersection(b_mantra):
                    best_candidate = b
                    break
        
        # Secondo tentativo: stesso ruolo generale
        if not best_candidate:
            for b in bench_unmapped:
                if b['role'] == st['role'] and b['id'] not in used_bench:
                    best_candidate = b
                    break
                    
        if best_candidate:
            used_bench.add(best_candidate['id'])
            pairings[st['id']] = {
                'coppia_nome': best_candidate['name'],
                'coppia_id': best_candidate['id'],
                'coppia_ruolo': best_candidate['role'],
                'coppia_tipo': 'RISERVA',
                'coppia_dettaglio': f"Alternativa ({best_candidate['name']})"
            }
            pairings[best_candidate['id']] = {
                'coppia_nome': st['name'],
                'coppia_id': st['id'],
                'coppia_ruolo': st['role'],
                'coppia_tipo': 'TITOLARE',
                'coppia_dettaglio': f"Copertura di {st['name']}"
            }


print(f"\nGiocatori totali mappati con coppia/sostituto: {len(pairings)} / {len(players)}")

unmapped_starters = [p for p in players if p.get('is_in_11') and p['id'] not in pairings]
print(f"Titolari ancora senza sostituto: {len(unmapped_starters)}")
