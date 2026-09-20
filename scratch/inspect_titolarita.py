import json

ps = json.load(open('processed_players_master.json', encoding='utf-8'))

surprises = []
benched = []

for p in ps:
    st = p.get('starts_2627', 0)
    pres = p.get('presenze_2627', 0)
    in_11 = p.get('is_in_11', False)
    tit = p.get('titolarita', 0)
    inj = p.get('is_injured', False)
    
    if st >= 2 and tit < 70:
        surprises.append(f"SURPRISE STARTER: {p['name']} ({p['team']}) - starts: {st}/{pres}, tactical_tit: {tit}%, in_11: {in_11}")
    if in_11 and st == 0 and not inj and pres < 2:
        benched.append(f"BENCHED TOP: {p['name']} ({p['team']}) - starts: {st}/{pres}, tactical_tit: {tit}%, in_11: {in_11}")

print("--- SORPRESE TITOLARI (Giocano sempre ma avevano titolarità teorica bassa) ---")
for s in surprises[:15]:
    print(s)

print("\n--- ATTESI TITOLARI MA FINITI IN PANCHINA (in_11 teorico ma 0 presenze da titolare) ---")
for b in benched[:15]:
    print(b)
