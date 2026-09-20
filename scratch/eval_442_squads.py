import json

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

real_prices = {
    'meret': 101, 'milinkovic-savic v.': 1, 'contini': 1,
    'svilar': 136, 'gollini': 1, 'de marzi': 1,
    'vicario': 77, 'grabara': 1, 'falcone': 1,
    'dimarco': 85, 'carlos augusto': 17,
    'bremer': 63, 'gatti': 1,
    'bellanova': 15, 'zappacosta': 13,
    'tavares n.': 33, 'pedraza': 1,
    'mancini': 50, 'ghilardi': 1,
    'lucumì': 26, 'kelly l.': 1,
    'calhanoglu': 137, 'jones c.': 19,
    'baturina': 136, 'rodriguez je.': 12, 'da cunha': 45,
    'bernardeschi': 46, 'odgaard': 1,
    'calò': 10, 'grillitsch': 1,
    'zaccagni': 78, 'przyborek': 1,
    'adzic': 1, 'thorstvedt': 1,
    'frattesi': 69, 'dele-bashiru': 1,
    'ramos g.': 237, 'camarda': 1,
    'thuram': 255, 'bonny': 1,
    'scamacca': 137, 'krstovic': 61,
    'bowie': 3, 'esposito se.': 36,
    'martinez l.': 415, 'esposito f.p.': 83
}

def get_cost(name):
    c = real_prices.get(name.lower())
    if c is not None:
        return c
    p = next((x for x in players if x['name'].lower() == name.lower()), None)
    return p.get('prezzo_cons', 1) if p else 1

def eval_squad(name, p_s, p_b, d_s, d_b, c_s, c_b, a_s, a_b):
    print(f"\n==========================================")
    print(f"VALUTAZIONE SQUADRA: {name}")
    all_s = p_s + d_s + c_s + a_s
    all_b = p_b + d_b + c_b + a_b
    cost_s = sum(get_cost(x) for x in all_s)
    cost_b = sum(get_cost(x) for x in all_b)
    total = cost_s + cost_b
    
    starter_objs = [next(x for x in players if x['name'].lower() == n.lower()) for n in all_s]
    avg_ovr = sum(p['ovr'] for p in starter_objs) / 11
    
    print(f"Costo Titolari (11): {cost_s} CR")
    print(f"Costo Riserve  (14): {cost_b} CR")
    print(f"TOTALE ROSA (25):    {total} CR (Tesoretto: {1000 - total} CR)")
    print(f"Media OVR Titolari:  {avg_ovr:.1f}")
    
    print("\n--- DETTAGLIO COPPIE 4-4-2 ---")
    print(f"🧤 P: {p_s[0]} ({get_cost(p_s[0])} CR) <---> {p_b[0]} ({get_cost(p_b[0])} CR) + {p_b[1]} ({get_cost(p_b[1])} CR)")
    for i in range(4):
        print(f"🛡️ D{i+1}: {d_s[i]} ({get_cost(d_s[i])} CR) <---> {d_b[i]} ({get_cost(d_b[i])} CR)")
    for i in range(4):
        print(f"⚙️ C{i+1}: {c_s[i]} ({get_cost(c_s[i])} CR) <---> {c_b[i]} ({get_cost(c_b[i])} CR)")
    for i in range(2):
        print(f"⚽ A{i+1}: {a_s[i]} ({get_cost(a_s[i])} CR) <---> {a_b[i]} ({get_cost(a_b[i])} CR)")
    print(f"⚽ A-Panchina Extra: {a_b[2]} ({get_cost(a_b[2])} CR) <---> {a_b[3]} ({get_cost(a_b[3])} CR)")

# OPZIONE 1: Ramos G. + Camarda & Scamacca + Krstovic + Baturina & Calhanoglu/Bernardeschi
eval_squad(
    "Opzione A: Ramos G. & Camarda + Scamacca & Krstovic (Baturina + Bernardeschi)",
    p_s=['Meret'],
    p_b=['Milinkovic-Savic V.', 'Contini'],
    d_s=['Tavares N.', 'Bellanova', 'Bremer', 'Lucumì'],
    d_b=['Pedraza', 'Zappacosta', 'Gatti', 'Kelly L.'],
    c_s=['Baturina', 'Bernardeschi', 'Calò', 'Adzic'],
    c_b=['Rodriguez Je.', 'Odgaard', 'Grillitsch', 'Thorstvedt'],
    a_s=['Ramos G.', 'Scamacca'],
    a_b=['Camarda', 'Krstovic', 'Bowie', 'Esposito Se.']
)

# OPZIONE 2: Ramos G. & Camarda + Thuram & Bonny (attacco atomico Milan-Inter)
eval_squad(
    "Opzione B: Doppio Top Ramos G. + Thuram (Derby di Milano)",
    p_s=['Meret'],
    p_b=['Milinkovic-Savic V.', 'Contini'],
    d_s=['Tavares N.', 'Bellanova', 'Bremer', 'Lucumì'],
    d_b=['Pedraza', 'Zappacosta', 'Gatti', 'Kelly L.'],
    c_s=['Baturina', 'Bernardeschi', 'Calò', 'Adzic'],
    c_b=['Rodriguez Je.', 'Odgaard', 'Grillitsch', 'Thorstvedt'],
    a_s=['Ramos G.', 'Thuram'],
    a_b=['Camarda', 'Bonny', 'Bowie', 'Esposito Se.']
)

# OPZIONE 3: Con Calhanoglu + Jones C. invece di Baturina
eval_squad(
    "Opzione C: Calhanoglu + Ramos G. + Scamacca",
    p_s=['Meret'],
    p_b=['Milinkovic-Savic V.', 'Contini'],
    d_s=['Tavares N.', 'Bellanova', 'Bremer', 'Lucumì'],
    d_b=['Pedraza', 'Zappacosta', 'Gatti', 'Kelly L.'],
    c_s=['Calhanoglu', 'Bernardeschi', 'Calò', 'Adzic'],
    c_b=['Jones C.', 'Odgaard', 'Grillitsch', 'Thorstvedt'],
    a_s=['Ramos G.', 'Scamacca'],
    a_b=['Camarda', 'Krstovic', 'Bowie', 'Esposito Se.']
)
