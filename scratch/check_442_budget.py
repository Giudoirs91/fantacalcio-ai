import json
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
players_path = os.path.join(root_dir, 'data', 'processed', 'processed_players_master.json')

with open(players_path, 'r', encoding='utf-8') as f:
    players = json.load(f)

real_prices = {
    'meret': 101, 'milinkovic-savic v.': 1, 'contini': 1,
    'svilar': 136, 'gollini': 1, 'de marzi': 1, 'bijlow': 5,
    'de gea': 56, 'christensen o.': 1, 'lezzerini': 1,
    'perri': 41, 'caprile': 39, 'corvi': 6,
    'vicario': 77, 'grabara': 1, 'falcone': 1,
    'martinez jo.': 120, 'provedel': 9, 'maignan': 93, 'carnesecchi': 96,
    'kalulu': 55, 'mancini': 50, 'bellanova': 15, 'tavares n.': 33, 'gila': 45,
    'bremer': 63, 'hermoso': 12, 'wesley': 67, 'rrahmani': 41, 'molina n.': 77, 'akanji': 57,
    'valeri': 1, 'gallo': 1, 'kabasele': 1, 'marcandalli': 1, 'ostigard': 1,
    'vasquez': 2, 'obert': 1, 'mina': 2, 'pedraza': 1, 'zappacosta': 13, 'lucumì': 26,
    'kelly l.': 1, 'obrador': 5, 'doig': 1, 'dimarco': 85, 'carlos augusto': 17, 'rensch': 1, 'lulli': 1, 'gatti': 1, 'ghilardi': 1, 'buongiorno': 1, 'pavard': 1, 'rugani': 1,
    'mctominay': 135, 'baturina': 136, 'calò': 10, 'bernabè': 2, 'vergara': 45, 'da cunha': 45, 'mckennie': 44,
    'frattesi': 69, 'koné m.': 33, 'calhanoglu': 137, 'mastantuono': 80, 'barella': 68, 'paz n.': 190,
    'bernardeschi': 46, 'odgaard': 1, 'grillitsch': 1, 'caqueret': 1, 'jones c.': 19, 'el azzouzi o.': 1, 'saelemaekers': 15, 'musah': 1, 'rodriguez je.': 12, 'pellegrini lo.': 1, 'przyborek': 1, 'zarraga': 1, 'mkhitaryan': 1, 'brescianini': 1, 'oristanio': 1,
    'zaniolo': 63, 'busio': 1, 'fazzini': 1, 'thorstvedt': 1, 'perrone': 1, 'adzic': 1, 'douglas luiz': 2,
    'martinez l.': 415, 'scamacca': 137, 'krstovic': 61, 'esposito se.': 36, 'raimondo': 30, 'bowie': 3, 'kevin carlos': 1, 'vitinha o.': 1,
    'malen': 442, 'kean': 79, 'bonny': 1, 'douvikas': 205, 'piccoli': 51, 'thuram': 255, 'soulé': 110,
    'kolo muani': 264, 'esposito f.p.': 83, 'camarda': 1, 'ramos g.': 237, 'hojlund': 260, 'lucca': 1
}

def get_cost(p):
    if not p: return 1
    clean = p['name'].lower().strip()
    if clean in real_prices:
        return real_prices[clean]
    return p.get('prezzo_cons', 1)

def get_p(name):
    return next((p for p in players if p['name'].lower() == name.lower()), None)

# Esploriamo configurazioni con budget < 960 CR:
# PORTA:
# Meret (101) + Milinkovic-Savic V. (1) + Contini (1) = 103 CR
# Vicario (77) + Grabara (1) + Falcone/3° = 79 CR

# In attacco:
# Coppia 1: Thuram (255) + Bonny (1) = 256 CR
# Oppure Ramos G. (237) + Camarda (1) = 238 CR
# Coppia 2: Scamacca (137) + Krstovic (61) = 198 CR
# Coppia 3 (panchina fanta 6 slot): Bowie (3) + Esposito Se. (36) = 39 CR
# Totale attacco: 256 + 198 + 39 = 493 CR

# Centrocampo (4 coppie = 8 giocatori):
# C1: Baturina (136) + Da Cunha (45) [oppure Rodriguez Je. 12] = 181 CR (o 148 CR)
# C2: Bernardeschi (46) + Odgaard (1) = 47 CR (Bologna ala/trequarti)
# C3: Calò (10) + Grillitsch (1) = 11 CR (Frosinone rigorista + mediano)
# C4: Adzic (1) + Thorstvedt (1) = 2 CR (Sassuolo) oppure Busio (1) + Doumbia (1)
# O magari Mastantuono (80) + Frattesi (69)?
# Calcoliamo:
# Se Porta = 103
# Se Attacco = 493
# Rimangono 404 per Difesa (8 giocatori) e Centrocampo (8 giocatori)!

# Difesa (4 coppie = 8 giocatori):
# D1: Tavares N. (33) + Pedraza (1) = 34 CR (Lazio terzini sx)
# D2: Bellanova (15) + Zappacosta (13) = 28 CR (Atalanta quinti dx)
# D3: Bremer (63) + Gatti (1) = 64 CR (Juve centrali)
# D4: Lucumì (26) + Kelly L. (1) = 27 CR (Bologna/Juve) oppure Hermoso (12) + Hummels (1)
# Totale Difesa = 34 + 28 + 64 + 27 = 153 CR!

# Se Difesa = 153, Porta = 103, Attacco = 493:
# Spesa parziale: 103 + 153 + 493 = 749 CR!
# Abbiamo ben 251 CR liberi per il centrocampo!

# Centrocampo con 200-220 CR:
# C1: Baturina (136) + Rodriguez Je. (12) = 148 CR (Como)
# C2: Bernardeschi (46) + Odgaard (1) = 47 CR (Bologna)
# C3: Calò (10) + Grillitsch (1) = 11 CR (Frosinone rigorista)
# C4: Adzic (1) + Thorstvedt (1) = 2 CR (Sassuolo)
# Totale C = 148 + 47 + 11 + 2 = 208 CR!
# Totale Rosa = 749 + 208 = 957 CR! (Tesoretto rimanente: 43 CR!)

print("Configurazione calcolata: 957 CR!")
