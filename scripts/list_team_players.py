import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

for tm in ['Roma', 'Cagliari', 'Sassuolo', 'Lazio']:
    print(f"\n=== {tm.upper()} ===")
    p_tm = [p for p in players if p.get('team') == tm]
    for p in sorted(p_tm, key=lambda x: x.get('minuti_2627', 0), reverse=True)[:12]:
        m = p.get('minuti_2627', 0)
        t = p.get('tiri_2627', 0)
        tp = p.get('tiri_porta_2627', 0)
        tp90 = round(tp / m * 90, 2) if m > 0 else 0
        print(f"  {p['name']} ({p['role']}) | Mins: {m}' ({p.get('starts_2627', 0)}T) | Gol: {p.get('gol_2627', 0)} (xG: {p.get('xg_2627')}) | Tiri: {t} | In Porta: {tp} ({tp90}/90) | Falli: {p.get('fouls_2627')} | Subiti: {p.get('falli_subiti_2627')} | Amm: {p.get('amm_2627')}")
