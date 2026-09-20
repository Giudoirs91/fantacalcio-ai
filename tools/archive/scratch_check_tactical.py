import json
import pandas as pd
from src.player_matcher import clean_text

df_new = pd.read_excel('Listone_definitivo_Fantacalcio_Stagione_2026_27.xlsx', skiprows=1).dropna(subset=['Id', 'Nome', 'Squadra'])
with open('config/tactical_db.json', 'r', encoding='utf-8') as f:
    tac = json.load(f)

print('--- CHECKING TACTICAL DB VS DEFINITIVE LISTONE ---')
for team, info in tac.items():
    team_df = df_new[df_new['Squadra'].str.lower() == team.lower()]
    team_names = [clean_text(n) for n in team_df['Nome']]
    
    for p in info.get('lineup', []):
        pname = clean_text(p['name'])
        matched = any(pname in tn or tn in pname for tn in team_names)
        if not matched:
            other = df_new[df_new['Nome'].apply(lambda x: clean_text(x) in pname or pname in clean_text(x))]
            if len(other) > 0:
                print(f"[{team}] Lineup: '{p['name']}' NOT in {team}! Present in: {other.iloc[0]['Squadra']} ({other.iloc[0]['Nome']})")
            else:
                print(f"[{team}] Lineup: '{p['name']}' NOT found anywhere in listone!")

    for r in info.get('rigoristi', []):
        rname = clean_text(r)
        matched = any(rname in tn or tn in rname for tn in team_names)
        if not matched:
            other = df_new[df_new['Nome'].apply(lambda x: clean_text(x) in rname or rname in clean_text(x))]
            if len(other) > 0:
                print(f"[{team}] Rigorista: '{r}' NOT in {team}! Present in: {other.iloc[0]['Squadra']} ({other.iloc[0]['Nome']})")
            else:
                print(f"[{team}] Rigorista: '{r}' NOT found anywhere in listone!")

    for fld in ['top', 'sleeper', 'flop', 'punizioni', 'corner']:
        for item in info.get(fld, []):
            iname = clean_text(item)
            matched = any(iname in tn or tn in iname for tn in team_names)
            if not matched:
                other = df_new[df_new['Nome'].apply(lambda x: clean_text(x) in iname or iname in clean_text(x))]
                if len(other) > 0:
                    print(f"[{team}] {fld}: '{item}' NOT in {team}! Present in: {other.iloc[0]['Squadra']}")
                else:
                    print(f"[{team}] {fld}: '{item}' NOT found in listone!")
