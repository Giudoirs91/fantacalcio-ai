import json
import pandas as pd
from src.player_matcher import clean_text, match_player_name

df = pd.read_excel('Listone_definitivo_Fantacalcio_Stagione_2026_27.xlsx', skiprows=1).dropna(subset=['Id', 'Nome', 'Squadra'])
teams = sorted(df['Squadra'].unique())

with open('config/tactical_db.json', 'r', encoding='utf-8') as f:
    tac = json.load(f)

print('=== SYNCING TACTICAL DB WITH DEFINITIVE LISTONE ===')

for t in teams:
    team_df = df[df['Squadra'].str.lower() == t.lower()]
    team_player_names = list(team_df['Nome'])
    
    if t not in tac:
        print(f"Warning: Team {t} not in tactical_db!")
        continue
    
    info = tac[t]
    
    # Check lineup
    for lp in info.get('lineup', []):
        pname = lp.get('name', '')
        # Check if in current team
        matched = False
        matched_name = None
        for tp in team_player_names:
            if match_player_name(pname, tp):
                matched = True
                matched_name = tp
                break
        if matched:
            lp['name'] = matched_name
        else:
            # Look for highest FVM player of same role not yet in lineup
            role = lp.get('role', 'D')
            role_df = team_df[team_df['R'] == role].sort_values(by='FVM', ascending=False)
            current_lineup_names = [x['name'] for x in info.get('lineup', [])]
            for _, r_cand in role_df.iterrows():
                if r_cand['Nome'] not in current_lineup_names:
                    print(f"[{t}] Replacing missing lineup '{pname}' ({role}) with '{r_cand['Nome']}' (FVM {r_cand['FVM']})")
                    lp['name'] = r_cand['Nome']
                    lp['status'] = 'Titolare'
                    break

    # Clean rigoristi
    valid_rig = []
    for r in info.get('rigoristi', []):
        for tp in team_player_names:
            if match_player_name(r, tp):
                valid_rig.append(tp)
                break
    # If less than 2, fill from top FVM attackers/midfielders
    if len(valid_rig) < 2:
        top_cands = team_df[team_df['R'].isin(['A', 'C'])].sort_values(by='FVM', ascending=False)
        for _, tc in top_cands.iterrows():
            if tc['Nome'] not in valid_rig:
                valid_rig.append(tc['Nome'])
            if len(valid_rig) >= 3:
                break
    info['rigoristi'] = valid_rig[:3]

    # Clean top
    valid_top = []
    for tp_item in info.get('top', []):
        for tp in team_player_names:
            if match_player_name(tp_item, tp):
                valid_top.append(tp)
                break
    if len(valid_top) < 2:
        top_cands = team_df.sort_values(by='FVM', ascending=False)
        for _, tc in top_cands.iterrows():
            if tc['Nome'] not in valid_top:
                valid_top.append(tc['Nome'])
            if len(valid_top) >= 3:
                break
    info['top'] = valid_top[:3]

    # Clean sleeper
    valid_sleeper = []
    for sp_item in info.get('sleeper', []):
        for tp in team_player_names:
            if match_player_name(sp_item, tp):
                valid_sleeper.append(tp)
                break
    info['sleeper'] = valid_sleeper

    # Clean flop
    valid_flop = []
    for fl_item in info.get('flop', []):
        for tp in team_player_names:
            if match_player_name(fl_item, tp):
                valid_flop.append(tp)
                break
    info['flop'] = valid_flop

    # Clean punizioni & corner
    for set_piece in ['punizioni', 'corner']:
        valid_sp = []
        for sp_name in info.get(set_piece, []):
            for tp in team_player_names:
                if match_player_name(sp_name, tp):
                    valid_sp.append(tp)
                    break
        info[set_piece] = valid_sp

with open('config/tactical_db.json', 'w', encoding='utf-8') as f:
    json.dump(tac, f, ensure_ascii=False, indent=2)

print('Tactical DB 100% synchronized with Definitive Listone!')
