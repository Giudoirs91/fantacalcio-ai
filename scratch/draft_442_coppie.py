import json
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
players_path = os.path.join(root_dir, 'data', 'processed', 'processed_players_master.json')

with open(players_path, 'r', encoding='utf-8') as f:
    players = json.load(f)

# Carica REAL_AUCTION_PRICES
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

# Selezioniamo un ventaglio di candidati top per 4-4-2 a coppie:
# PORTA:
# Opzione A: Meret (101) + Milinkovic-Savic V. (1) + Contini (1) = 103 CR (Napoli di Allegri)
# Opzione B: Vicario (77) + Grabara (1) + Falcone/3° = 79 CR (Juve di Spalletti)
# Opzione C: Svilar (136) + Gollini (1) + De Marzi (1) = 138 CR (Roma di Gasp)

# DIFESA (4 titolari + 4 rispettivi sostituti naturali):
# 1. Dimarco (85) <-> Carlos Augusto (17) -> Inter fascia sx (staffetta certa!)
# 2. Bremer (63) <-> Gatti (1) -> Juve centro difesa
# 3. Bellanova (15) <-> Zappacosta (13) -> Atalanta fascia dx (staffetta letale!)
# 4. Tavares N. (33) <-> Pedraza (1) -> Lazio fascia sx (oppure Mancini 50 <-> Ghilardi 1, o Rrahmani 41 <-> Buongiorno 1)

# CENTROCAMPO (4 titolari + 4 rispettivi sostituti naturali):
# 1. Calhanoglu (137) <-> Jones C. (19) -> Rigorista e faro Inter
# 2. Baturina (136) <-> Da Cunha (45) o Rodriguez Je. (12) -> Stella Como
# 3. Bernardeschi (46) <-> Odgaard (1) o Mastantuono (80)
# 4. Calò (10) <-> Grillitsch (1) -> Rigorista Frosinone
# (Oppure Zaccagni 78 <-> Przyborek 1, Orsolini 199 <-> El Azzouzi 1, Rabiot 128 <-> Musah 1)

# ATTACCO (2 titolari + 2 sostituti diretti + 3a coppia per completare i 6 attaccanti):
# 1. Thuram (255) <-> Bonny (1) -> Attacco Inter
# 2. Scamacca (137) <-> Krstovic (61) -> Attacco Atalanta
# 3. Bowie (3) <-> Esposito Se. (36) -> Sassuolo (oppure Ramos G. 237 + Camarda 1)

print("Verifica combinazioni...")
