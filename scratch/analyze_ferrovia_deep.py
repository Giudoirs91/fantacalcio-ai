import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

excel_path = 'data/raw/lega-ferrovia-rosters-1788691861822.xlsx'
df = pd.read_excel(excel_path, sheet_name='ROSE')

teams = {}
col_idx = 0
while col_idx < len(df.columns):
    team_col = df.columns[col_idx]
    if 'Unnamed' not in str(team_col) and str(team_col).strip():
        team_name = str(team_col).strip()
        p_names = df.iloc[0:25, col_idx].tolist()
        p_costs = df.iloc[0:25, col_idx + 1].tolist()
        
        # 3 POR, 8 DIF, 8 CEN, 6 ATT
        team_dict = {
            'POR': [{'name': str(n).strip(), 'cost': int(c) if pd.notna(c) else 1} for n, c in zip(p_names[0:3], p_costs[0:3])],
            'DIF': [{'name': str(n).strip(), 'cost': int(c) if pd.notna(c) else 1} for n, c in zip(p_names[3:11], p_costs[3:11])],
            'CEN': [{'name': str(n).strip(), 'cost': int(c) if pd.notna(c) else 1} for n, c in zip(p_names[11:19], p_costs[11:19])],
            'ATT': [{'name': str(n).strip(), 'cost': int(c) if pd.notna(c) else 1} for n, c in zip(p_names[19:25], p_costs[19:25])]
        }
        teams[team_name] = team_dict
        col_idx += 2
    else:
        col_idx += 1

print(f"=== ANALISI DETTAGLIATA LEGA FERROVIA (10 SQUADRE - 1000 CREDITI) ===\n")

stats_summary = []

for tname, roles in teams.items():
    p_tot = sum(p['cost'] for p in roles['POR'])
    d_tot = sum(p['cost'] for p in roles['DIF'])
    c_tot = sum(p['cost'] for p in roles['CEN'])
    a_tot = sum(p['cost'] for p in roles['ATT'])
    total = p_tot + d_tot + c_tot + a_tot
    
    # Top player per role
    top_p = max(roles['POR'], key=lambda x: x['cost'])
    top_d = max(roles['DIF'], key=lambda x: x['cost'])
    top_c = max(roles['CEN'], key=lambda x: x['cost'])
    top_a = max(roles['ATT'], key=lambda x: x['cost'])
    
    # 1 cr count
    all_p = roles['POR'] + roles['DIF'] + roles['CEN'] + roles['ATT']
    count_1cr = sum(1 for p in all_p if p['cost'] == 1)
    
    stats_summary.append({
        'squadra': tname,
        'P_tot': p_tot, 'P_pct': round(p_tot/total*100, 1),
        'D_tot': d_tot, 'D_pct': round(d_tot/total*100, 1),
        'C_tot': c_tot, 'C_pct': round(c_tot/total*100, 1),
        'A_tot': a_tot, 'A_pct': round(a_tot/total*100, 1),
        'Total': total,
        'Top_A': f"{top_a['name']} ({top_a['cost']} cr)",
        'Top_C': f"{top_c['name']} ({top_c['cost']} cr)",
        'Top_D': f"{top_d['name']} ({top_d['cost']} cr)",
        'Top_P': f"{top_p['name']} ({top_p['cost']} cr)",
        'Count_1cr': count_1cr
    })

df_summary = pd.DataFrame(stats_summary)
print(df_summary[['squadra', 'P_tot', 'D_tot', 'C_tot', 'A_tot', 'Total', 'Count_1cr']].to_string(index=False))

print("\n--- PERCENTUALI MEDIE SPESA REPARTO (LEGA A 10) ---")
print(f"• Portieri: media {df_summary['P_tot'].mean():.1f} cr ({df_summary['P_pct'].mean():.1f}%) | range: {df_summary['P_tot'].min()} - {df_summary['P_tot'].max()} cr")
print(f"• Difensori: media {df_summary['D_tot'].mean():.1f} cr ({df_summary['D_pct'].mean():.1f}%) | range: {df_summary['D_tot'].min()} - {df_summary['D_tot'].max()} cr")
print(f"• Centrocampisti: media {df_summary['C_tot'].mean():.1f} cr ({df_summary['C_pct'].mean():.1f}%) | range: {df_summary['C_tot'].min()} - {df_summary['C_tot'].max()} cr")
print(f"• Attaccanti: media {df_summary['A_tot'].mean():.1f} cr ({df_summary['A_pct'].mean():.1f}%) | range: {df_summary['A_tot'].min()} - {df_summary['A_tot'].max()} cr")
print(f"• Giocatori a 1 credito: media {df_summary['Count_1cr'].mean():.1f} per rosa | range: {df_summary['Count_1cr'].min()} - {df_summary['Count_1cr'].max()}")

print("\n--- I TOP PLAYER ACQUISTATI (CHI HA PRESO CHI E A QUANTO) ---")
for _, r in df_summary.iterrows():
    print(f"• {r['squadra']:18}: ATT: {r['Top_A']} | CEN: {r['Top_C']} | DIF: {r['Top_D']} | POR: {r['Top_P']}")
