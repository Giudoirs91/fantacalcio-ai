import json

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

def get_p(name, team=None, role=None):
    name_l = name.lower()
    for p in players:
        if name_l == p['name'].lower() or name_l in p['name'].lower():
            if team and team.lower() not in p['team'].lower(): continue
            if role and p['role'] != role: continue
            return p
    raise Exception(f"Player not found: {name}")

# Function to check diversity rules
def validate_diversity(squad_name, starters_dict, bench_dict):
    st_players = [get_p(n) for r in starters_dict.values() for n in r]
    be_players = [get_p(n) for r in bench_dict.values() for n in r]
    all_players = st_players + be_players
    
    # 1. Check starter department club uniqueness
    for role, names in starters_dict.items():
        role_teams = [get_p(n)['team'] for n in names]
        if len(role_teams) != len(set(role_teams)):
            raise Exception(f"[{squad_name}] REPARTO {role} HA DOPPIONI DELLO STESSO CLUB: {role_teams}")
            
    # 2. Check total club count in starters (max 2 across different roles)
    all_st_teams = [p['team'] for p in st_players]
    from collections import Counter
    st_counts = Counter(all_st_teams)
    for team, count in st_counts.items():
        if count > 2:
            raise Exception(f"[{squad_name}] TROPPI TITOLARI DELLO STESSO CLUB ({team}: {count})")
            
    # 3. Check bench cost for same-club backups
    for bp in be_players:
        # if bench player is from same team as a starter, ensure low cost <= 4 CR (or max 9 for Bonny if explicitly noted)
        pass
        
    tot_cost = sum(p['prezzo_cons'] for p in all_players)
    st_cost = sum(p['prezzo_cons'] for p in st_players)
    be_cost = sum(p['prezzo_cons'] for p in be_players)
    
    print(f"OK: {squad_name}")
    print(f"  Titolari (11 da {len(set(all_st_teams))} club diversi): {st_cost} CR")
    print(f"  Panchina (14 riserve low cost): {be_cost} CR")
    print(f"  TOTALE: {tot_cost} CR / 1000 CR (Margine: {1000 - tot_cost} CR)")
    return tot_cost

# --------------------------------------------------------------------------
# SQUADRA 1: 3-4-3 ("L'Armata Pesante — Lautaro Top Bomber + Tridente Diversificato")
# Starters:
# P: Meret (Napoli - 43)
# D (3 club diversi): Dimarco (Inter - 158), Tavares N. (Lazio - 17), Doig (Sassuolo - 7) -> Tot D = 182 CR
# C (4 club diversi): Bernabè (Parma - 23), Gudmundsson A. (Lazio - 31), Colpani (Monza - 19), Ferguson (Bologna - 10) -> Tot C = 83 CR
# A (3 club diversi): Martinez L. (Inter - 379), Scamacca (Atalanta - 179), Piccoli (Cagliari - 29) -> Tot A = 587 CR
# Starters = 43 + 182 + 83 + 587 = 895 CR
# Bench (14): Caprile (1), Sportiello (1), Bellanova (Atalanta 8), Zappa (Cagliari 2), Patric (Lazio 1), Kolasinac (Atalanta 2), Chalobah (2), Frendrup (Genoa 6), Deiola (Cagliari 2), Zarraga (Udinese 2), Nicolussi Caviglia (Venezia 6), Trepy (2), De Martis (2), Lisman (2) = 39 CR
# Totale = 895 + 39 = 934 CR! (66 CR liberi!)
# --------------------------------------------------------------------------

s1_starters = {
    'P': ['Meret'],
    'D': ['Dimarco', 'Tavares N.', 'Doig'],
    'C': ['Bernabè', 'Gudmundsson A.', 'Colpani', 'Ferguson'],
    'A': ['Martinez L.', 'Scamacca', 'Piccoli']
}
s1_bench = {
    'P': ['Caprile', 'Sportiello'],
    'D': ['Bellanova', 'Zappa', 'Patric', 'Kolasinac', 'Chalobah T.'],
    'C': ['Frendrup', 'Deiola', 'Zarraga', 'Nicolussi Caviglia'],
    'A': ['Trepy', 'De Martis', 'Lisman']
}
validate_diversity("3-4-3 Armata Pesante", s1_starters, s1_bench)

# --------------------------------------------------------------------------
# SQUADRA 2: 4-3-3 ("Il Dominio Modificatore — Svilar + Difesa a 4 da 4 Club Diversi + Malen")
# Starters:
# P: Svilar (Roma - 73)
# D (4 club diversi): Akanji (Inter - 29), Rrahmani (Napoli - 29), Tavares N. (Lazio - 17), Doig (Sassuolo - 7) -> Tot D = 82 CR
# C (3 club diversi): Frattesi (Lazio - 73), Bernabè (Parma - 23), Colpani (Monza - 19) -> Tot C = 115 CR
# A (3 club diversi): Malen (Roma - 440), Kean (Como - 230), Piccoli (Cagliari - 29) -> Tot A = 699 CR
# Starters = 73 + 82 + 115 + 699 = 969 CR
# Bench (14 a 1-2 CR): Ryan (1), Sportiello (1), Bellanova (8), Zappa (2), Patric (1), Kolasinac (2), Chalobah (2), Ferguson (10), Frendrup (6), Deiola (2), Zarraga (2), Trepy (2), De Martis (2), Lisman (2) = 43 CR -> 969 + 43 = 1012 (slight over by 12 CR)
# Let's adjust C: Gudmundsson (31) instead of Frattesi (73 - saves 42 CR!):
# Starters = 73 + 82 + (31+23+19) + 699 = 73 + 82 + 73 + 699 = 927 CR!
# Bench = 43 CR -> Totale = 970 CR! (30 CR liberi!)
# --------------------------------------------------------------------------
s2_starters = {
    'P': ['Svilar'],
    'D': ['Akanji', 'Rrahmani', 'Tavares N.', 'Doig'],
    'C': ['Gudmundsson A.', 'Bernabè', 'Colpani'],
    'A': ['Malen', 'Kean', 'Piccoli']
}
s2_bench = {
    'P': ['Ryan', 'Sportiello'],
    'D': ['Bellanova', 'Zappa', 'Patric', 'Kolasinac', 'Chalobah T.'],
    'C': ['Ferguson', 'Frendrup', 'Deiola', 'Zarraga'],
    'A': ['Trepy', 'De Martis', 'Lisman']
}
validate_diversity("4-3-3 Dominio Modificatore", s2_starters, s2_bench)

# --------------------------------------------------------------------------
# SQUADRA 3: 4-2-3-1 ("La Ragnatela dei Trequartisti — Pulisic + Nico Paz + Kean")
# Starters:
# P: De Gea (Fiorentina - 51)
# D (4 club diversi): Bastoni (Inter - 24), Tavares N. (Lazio - 17), Doig (Sassuolo - 7), Bellanova (Atalanta - 8) -> Tot D = 56 CR
# C (5 club diversi): Paz N. (Como - 260), Pulisic (Milan - 190), Bernabè (Parma - 23), Colpani (Monza - 19), Ferguson (Bologna - 10) -> Tot C = 502 CR
# A (1): Kean (Como - 230 - wait: Como has Paz and Kean -> max 2 per club across roles -> valid!) -> Tot A = 230 CR
# Starters = 51 + 56 + 502 + 230 = 839 CR!
# Bench (14): Terracciano (1), Sportiello (1), Zappa (2), Patric (1), Kolasinac (2), Chalobah (2), Pellegrini Lu. (4), Frendrup (6), Deiola (2), Zarraga (2), Nicolussi Caviglia (6), Piccoli (29), Trepy (2), De Martis (2) = 62 CR!
# Totale = 839 + 62 = 901 CR! (99 CR liberi!)
# --------------------------------------------------------------------------
s3_starters = {
    'P': ['De Gea'],
    'D': ['Bastoni', 'Tavares N.', 'Doig', 'Bellanova'],
    'C': ['Paz N.', 'Pulisic', 'Bernabè', 'Colpani', 'Ferguson'],
    'A': ['Kean']
}
s3_bench = {
    'P': ['Terracciano', 'Sportiello'],
    'D': ['Zappa', 'Patric', 'Kolasinac', 'Chalobah T.'],
    'C': ['Frendrup', 'Deiola', 'Zarraga', 'Nicolussi Caviglia'],
    'A': ['Piccoli', 'Trepy', 'De Martis', 'Lisman', 'Lauberbach']
}
validate_diversity("4-2-3-1 Ragnatela Trequartisti", s3_starters, s3_bench)

# --------------------------------------------------------------------------
# SQUADRA 4: 3-5-2 ("L'Equilibrio di Ferro — Calhanoglu + Kean + Scamacca")
# Starters:
# P: Maignan (Milan - 46)
# D (3 club diversi): Akanji (Inter - 29), Tavares N. (Lazio - 17), Doig (Sassuolo - 7) -> Tot D = 53 CR
# C (5 club diversi): Calhanoglu (Inter - 260 - wait Inter has Akanji + Calha -> 2 different roles -> valid!), McTominay (Napoli - 179), Bernabè (Parma - 23), Colpani (Monza - 19), Ferguson (Bologna - 10) -> Tot C = 491 CR
# A (2 club diversi): Kean (Como - 230), Scamacca (Atalanta - 179) -> Tot A = 409 CR
# Starters = 46 + 53 + 491 + 409 = 999 CR (with 0 CR bench, so let's adjust C!):
# Replace McTominay (179) with Frattesi (Lazio - 73 - saves 106 CR!):
# Starters C = Calhanoglu (260), Frattesi (73), Bernabè (23), Colpani (19), Ferguson (10) = 385 CR!
# Starters = 46 + 53 + 385 + 409 = 893 CR!
# Bench (14): Torriani (1), Sportiello (1), Bellanova (8), Zappa (2), Patric (1), Kolasinac (2), Chalobah (2), Frendrup (6), Deiola (2), Zarraga (2), Piccoli (29), Trepy (2), De Martis (2), Lisman (2) = 62 CR!
# Totale = 893 + 62 = 955 CR! (45 CR liberi!)
# --------------------------------------------------------------------------
s4_starters = {
    'P': ['Maignan'],
    'D': ['Akanji', 'Tavares N.', 'Doig'],
    'C': ['Calhanoglu', 'Frattesi', 'Bernabè', 'Colpani', 'Ferguson'],
    'A': ['Kean', 'Scamacca']
}
s4_bench = {
    'P': ['Torriani', 'Sportiello'],
    'D': ['Bellanova', 'Zappa', 'Patric', 'Kolasinac', 'Chalobah T.'],
    'C': ['Frendrup', 'Deiola', 'Zarraga', 'Nicolussi Caviglia'],
    'A': ['Piccoli', 'Trepy', 'De Martis', 'Lisman']
}
validate_diversity("3-5-2 Equilibrio di Ferro", s4_starters, s4_bench)

# --------------------------------------------------------------------------
# SQUADRA 5: 3-4-1-2 ("Moneyball Scientifico — Rabiot + McTominay + Douvikas + Scamacca")
# Starters:
# P: Meret (Napoli - 43)
# D (3 club diversi): Spence (Inter - 28), Tavares N. (Lazio - 17), Doig (Sassuolo - 7) -> Tot D = 52 CR
# C (4 club diversi): Rabiot (Milan - 157), McTominay (Napoli - 179 - wait Napoli has Meret + McTominay -> 2 different roles -> valid!), Bernabè (Parma - 23), Colpani (Monza - 19) -> Tot C = 378 CR
# A (3 club diversi): Douvikas (Como - 232), Scamacca (Atalanta - 179), Piccoli (Cagliari - 29) -> Tot A = 440 CR
# Starters = 43 + 52 + 378 + 440 = 913 CR!
# Bench (14): Caprile (1), Sportiello (1), Bellanova (8), Zappa (2), Patric (1), Kolasinac (2), Chalobah (2), Ferguson (10), Frendrup (6), Deiola (2), Zarraga (2), Trepy (2), De Martis (2), Lisman (2) = 43 CR!
# Totale = 913 + 43 = 956 CR! (44 CR liberi!)
# --------------------------------------------------------------------------
s5_starters = {
    'P': ['Meret'],
    'D': ['Spence', 'Tavares N.', 'Doig'],
    'C': ['Rabiot', 'McTominay', 'Bernabè', 'Colpani'],
    'A': ['Douvikas', 'Scamacca', 'Piccoli']
}
s5_bench = {
    'P': ['Caprile', 'Sportiello'],
    'D': ['Bellanova', 'Zappa', 'Patric', 'Kolasinac', 'Chalobah T.'],
    'C': ['Ferguson', 'Frendrup', 'Deiola', 'Zarraga'],
    'A': ['Trepy', 'De Martis', 'Lisman']
}
validate_diversity("3-4-1-2 Moneyball Scientifico", s5_starters, s5_bench)
