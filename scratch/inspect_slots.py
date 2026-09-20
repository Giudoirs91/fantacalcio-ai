import json

with open('data/processed/processed_players_master.json', encoding='utf-8') as f:
    players = json.load(f)

check_names = ['Malen', 'Raimondo', 'Frattesi', 'Kamara H.', 'Cisse', 'Varela G.', 'Martinez L.', 'Kolo Muani', 'Douvikas', 'Paz N.', 'McTominay', 'Pulisic']

for cn in check_names:
    for p in players:
        if cn.lower() in p['name'].lower():
            sf = p.get('slot_fascia', '-')
            sn = p.get('slot_num', '-')
            ovr = p.get('ovr', 0)
            fvm = p.get('fvm', 0)
            cons = p.get('prezzo_cons', 0)
            g = p.get('gol_2627', 0)
            a = p.get('assist_2627', 0)
            p26 = p.get('presenze_2627', 0)
            dq = p.get('diff_q', 0)
            advice = p.get('ai_advice_type', '-')
            print(f"{p['name']:<18} | Slot: {sf:<12} (num:{sn}) | FVM:{fvm:<4} | Cons:{cons:<4} | 26/27: {g}G {a}A in {p26}p | DiffQ:{dq:+4.1f} | Advice:{advice}")
            break
