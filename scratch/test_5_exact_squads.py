import json

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

def p(name):
    name_l = name.lower()
    for x in players:
        if name_l == x['name'].lower() or name_l in x['name'].lower():
            return x
    raise Exception(f'Not found: {name}')

# --------------------------------------------------------------------------
# SQUADRA 1: 3-4-3 ("L'Armata Pesante — Lautaro Top Bomber & Tridente")
# --------------------------------------------------------------------------
sq1_starters = ['Meret', 'Spence', 'Akanji', 'Tavares N.', 'McTominay', 'Gudmundsson A.', 'Bernabè', 'Colpani', 'Martinez L.', 'Scamacca', 'Pellegrino M.']
sq1_bench = ['Caprile', 'Contini', 'Doig', 'Bellanova', 'Zappa', 'Gila', 'Patric', 'Frendrup', 'Ferguson', 'Payero', 'Gaetano', 'Bonny', 'Neres', 'Esposito Se.']
sq1_all = sq1_starters + sq1_bench
cost1 = sum(p(n)['prezzo_cons'] for n in sq1_all)
print(f"SQUAD 1 (3-4-3): {cost1} CR (Starters: {sum(p(n)['prezzo_cons'] for n in sq1_starters)} CR, Bench: {sum(p(n)['prezzo_cons'] for n in sq1_bench)} CR)")

# --------------------------------------------------------------------------
# SQUADRA 2: 4-3-3 ("Il Dominio Modificatore — Svilar & Fortezza 6.5 + Malen Bomber")
# --------------------------------------------------------------------------
sq2_starters = ['Svilar', 'Dimarco', 'Akanji', 'Bastoni', 'Rrahmani', 'Barella', 'Bernabè', 'Colpani', 'Malen', 'Pellegrino M.', 'Pinamonti']
# Let's check Pinamonti or Colombo or Kean
# Malen = 440, Dimarco = 158, Svilar = 73, Barella = 63, Bastoni = 24, Akanji = 29, Rrahmani = 29 -> Starters ~ 850
# Bench = 14 players with low cost
sq2_bench = ['Ryan', 'Marin', 'Doig', 'Bellanova', 'Zappa', 'Gila', 'Patric', 'Frendrup', 'Ferguson', 'Payero', 'Gaetano', 'Bonny', 'Neres', 'Esposito Se.']
# Let's check Pinamonti in players
p_pin = None
for x in players:
    if 'pinamonti' in x['name'].lower(): p_pin = x
print("Pinamonti cost:", p_pin['prezzo_cons'] if p_pin else 'Not found')

sq2_all = ['Svilar', 'Dimarco', 'Akanji', 'Bastoni', 'Rrahmani', 'Barella', 'Colpani', 'Bernabè', 'Malen', 'Pellegrino M.', p_pin['name'] if p_pin else 'Neres'] + sq2_bench
cost2 = sum(p(n)['prezzo_cons'] for n in sq2_all)
print(f"SQUAD 2 (4-3-3): {cost2} CR")

# --------------------------------------------------------------------------
# SQUADRA 3: 4-2-3-1 ("La Ragnatela dei Trequartisti — Pulisic + Nico Paz + Kean")
# --------------------------------------------------------------------------
sq3_starters = ['Maignan', 'Doig', 'Bastoni', 'Bisseck', 'Tavares N.', 'Frattesi', 'Bernabè', 'Paz N.', 'Pulisic', 'Colpani', 'Kean']
sq3_bench = ['Torriani', 'Sportiello', 'Bellanova', 'Zappa', 'Gila', 'Patric', 'Pellegrini Lu.', 'Frendrup', 'Ferguson', 'Payero', 'Gaetano', 'Bonny', 'Neres', 'Esposito Se.']
sq3_all = sq3_starters + sq3_bench
cost3 = sum(p(n)['prezzo_cons'] for n in sq3_all)
print(f"SQUAD 3 (4-2-3-1): {cost3} CR (Starters: {sum(p(n)['prezzo_cons'] for n in sq3_starters)} CR, Bench: {sum(p(n)['prezzo_cons'] for n in sq3_bench)} CR)")

# --------------------------------------------------------------------------
# SQUADRA 4: 3-5-2 ("L'Equilibrio Rigoristi — Calhanoglu + Thuram + Kean")
# --------------------------------------------------------------------------
# Calhanoglu (260) + Thuram (270) + Kean (230) + Spence (28) + Akanji (29) + Tavares (17) + De Gea (51) + Gudmundsson (31) + Bernabè (23) + Colpani (19) + Frendrup (6) = 964 CR + bench (35 CR) = 999 CR!
sq4_starters = ['De Gea', 'Spence', 'Akanji', 'Tavares N.', 'Calhanoglu', 'Gudmundsson A.', 'Bernabè', 'Colpani', 'Frendrup', 'Thuram', 'Kean']
sq4_bench = ['Terracciano F.', 'Martinelli', 'Doig', 'Bellanova', 'Zappa', 'Gila', 'Patric', 'Ferguson', 'Payero', 'Gaetano', 'Nicolussi Caviglia', 'Bonny', 'Neres', 'Esposito Se.']
# check Martinelli
p_mart = None
for x in players:
    if 'martinelli' in x['name'].lower() and x['role'] == 'P': p_mart = x
if not p_mart:
    sq4_bench[1] = 'Caprile'
sq4_all = sq4_starters + sq4_bench
cost4 = sum(p(n)['prezzo_cons'] for n in sq4_all)
print(f"SQUAD 4 (3-5-2): {cost4} CR (Starters: {sum(p(n)['prezzo_cons'] for n in sq4_starters)} CR, Bench: {sum(p(n)['prezzo_cons'] for n in sq4_bench)} CR)")

# --------------------------------------------------------------------------
# SQUADRA 5: 3-4-1-2 ("Moneyball Scientifico — McTominay + Rabiot + Scamacca + Douvikas")
# --------------------------------------------------------------------------
# Rabiot (157) + McTominay (179) + Frattesi (73) + Colpani (19) + Paz N. (260) + Scamacca (179) + Pellegrino M. (51) + Meret (43) + Spence (28) + Tavares (17) + Doig (7) = 1013 -> let's adjust!
# If C_T: Bernabè (23) or Gudmundsson (31) or Nico Paz with cheaper A:
# Rabiot (157) + McTominay (179) + Frattesi (73) + Gudmundsson (31) + Colpani (19) + Douvikas (232) + Scamacca (179) + Meret (43) + Doig (7) + Tavares (17) + Bellanova (8) = 945 CR! + Bench (50 CR) = 995 CR!
sq5_starters = ['Meret', 'Doig', 'Tavares N.', 'Bellanova', 'Rabiot', 'McTominay', 'Frattesi', 'Gudmundsson A.', 'Colpani', 'Douvikas', 'Scamacca']
sq5_bench = ['Caprile', 'Contini', 'Spence', 'Zappa', 'Gila', 'Patric', 'Pellegrini Lu.', 'Bernabè', 'Ferguson', 'Frendrup', 'Payero', 'Bonny', 'Neres', 'Esposito Se.']
sq5_all = sq5_starters + sq5_bench
cost5 = sum(p(n)['prezzo_cons'] for n in sq5_all)
print(f"SQUAD 5 (3-4-1-2): {cost5} CR (Starters: {sum(p(n)['prezzo_cons'] for n in sq5_starters)} CR, Bench: {sum(p(n)['prezzo_cons'] for n in sq5_bench)} CR)")
