import json

with open('data/processed/processed_players_master.json', encoding='utf-8') as f:
    players = json.load(f)

check = ['Malen', 'Raimondo', 'Frattesi', 'Kamara H.', 'Cisse', 'Kolo Muani', 'Yildiz', 'Varela G.', 'De Gea', 'McTominay', 'Adorante', 'Zaniolo']

for c in check:
    for p in players:
        if c.lower() in p['name'].lower():
            name = p['name']
            sf = p.get('slot_fascia', '-')
            ovr = p.get('ovr', 0)
            cons = p.get('prezzo_cons', 0)
            inj = "SI" if p.get('is_injured') else "NO"
            g = p.get('gol_2627', 0)
            a = p.get('assist_2627', 0)
            pz = p.get('presenze_2627', 0)
            adv = p.get('ai_advice_type', '-')
            print(f"{name:<15} | Slot: {sf:<12} | OVR: {ovr:<3} | Cons: {cons:<3} CR | Inj: {inj:<2} | 26-27: {g}G {a}A in {pz}p | Advice: {adv}")
            break
