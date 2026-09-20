import json
import numpy as np

with open('processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

# Testiamo una formula continua senza saturazione né gradini piatti
for p in players:
    fvm = p['fvm']
    role = p['role']
    fm = p['fm'] if p['fm'] > 0 else (6.0 if role != 'P' else 5.0)
    mv = p['mv'] if p['mv'] > 0 else 6.0
    presenze = p['presenze']
    is_oop = p['is_oop']
    is_rig = p['is_rigorista_1']

    # FantaScore continuo (0 - 100) basato su FVM scalato con distribuzione sigmoide/continua
    if role == 'P':
        # FVM max ~63 (Martinez Jo.), ~58 (Vicario), ~52 (Carnesecchi), ~50 (Maignan)
        ovr = 50 + (fvm / 65.0) * 38 + (1.5 if p['is_in_11'] else 0)
        prezzo = max(1, int(round((fvm / 65.0) * 55)))
    elif role == 'D':
        # FVM max ~253 (Dimarco), ~82 (Wesley), ~80 (Molina), ~60 (Bremer), ~51 (Akanji/Rrahmani)
        if fvm >= 150: # Dimarco
            ovr = 95 + (fvm - 150) / 150.0 * 1.5
            prezzo = int(round(90 + (fvm - 150) * 0.38)) # 125-135 CR
        elif fvm >= 70: # Wesley, Molina
            ovr = 87 + (fvm - 70) / 80.0 * 6.0 # 87-93 OVR
            prezzo = int(round(45 + (fvm - 70) * 0.55)) # 45-55 CR
        elif fvm >= 30: # Bremer, Akanji, Rrahmani, Bastoni, Ostigard, Spence
            ovr = 78 + (fvm - 30) / 40.0 * 8.0 # 78-86 OVR
            prezzo = int(round(18 + (fvm - 30) * 0.65)) # 18-44 CR
        elif fvm >= 15: # Zortea, Miranda, Cambiaso, Dodò, Valeri
            ovr = 70 + (fvm - 15) / 15.0 * 7.0 # 70-77 OVR
            prezzo = int(round(6 + (fvm - 15) * 0.8)) # 6-18 CR
        else:
            ovr = max(48, int(50 + (fvm / 15.0) * 19))
            prezzo = max(1, int(round(1 + (fvm / 15.0) * 4)))
    elif role == 'C':
        # FVM max: Paz (247), Calha (236), McTominay (228), Orsolini (192), Pulisic (160), Rabiot (145), De Bruyne (107), Baturina (97), Zaccagni (88), Da Cunha (87), Atta (86), Zaniolo (85), Barella (80), Vlasic (75), Frattesi (68)
        if fvm >= 220: # Paz, Calhanoglu, McTominay
            ovr = 94 + (fvm - 220) / 30.0 * 2.0 # 94 - 96
            prezzo = int(round(210 + (fvm - 220) * 1.5)) # 210 - 250 CR
        elif fvm >= 140: # Orsolini, Pulisic, Rabiot
            ovr = 89 + (fvm - 140) / 80.0 * 4.5 # 89 - 93
            prezzo = int(round(135 + (fvm - 140) * 0.9)) # 135 - 205 CR
        elif fvm >= 80: # De Bruyne, Baturina, Zaccagni, Da Cunha, Atta, Zaniolo, Barella
            ovr = 81 + (fvm - 80) / 60.0 * 7.0 # 81 - 88
            prezzo = int(round(65 + (fvm - 80) * 1.15)) # 65 - 134 CR
        elif fvm >= 45: # Vlasic, Frattesi, Taylor, Mastantuono, Moreira, Ederson, Jones
            ovr = 73 + (fvm - 45) / 35.0 * 7.0 # 73 - 80
            prezzo = int(round(25 + (fvm - 45) * 1.1)) # 25 - 64 CR
        elif fvm >= 20: # Rowe, Samardzic, Politano, Thorstvedt, Perrone, Bernabè
            ovr = 65 + (fvm - 20) / 25.0 * 7.0 # 65 - 72
            prezzo = int(round(8 + (fvm - 20) * 0.68)) # 8 - 24 CR
        else:
            ovr = max(48, int(50 + (fvm / 20.0) * 14))
            prezzo = max(1, int(round(1 + (fvm / 20.0) * 6)))
    else: # 'A'
        # FVM max: Malen (414), Lautaro (367), Thuram (263), Hojlund (257), Ramos (228), Kolo Muani (211), Kean (187), Douvikas (170), Yildiz (150), Scamacca (123), Davis (109), Esposito (105), Berardi (101), Krstovic (100)
        if fvm >= 300: # Malen, Lautaro
            ovr = 95 + (fvm - 300) / 120.0 * 1.5 # 95 - 96
            prezzo = int(round(390 + (fvm - 300) * 0.8)) # 390 - 480 CR
        elif fvm >= 200: # Thuram, Hojlund, Ramos, Kolo Muani
            ovr = 90 + (fvm - 200) / 100.0 * 4.5 # 90 - 94
            prezzo = int(round(260 + (fvm - 200) * 1.25)) # 260 - 385 CR
        elif fvm >= 100: # Kean, Douvikas, Yildiz, Scamacca, Davis, Esposito, Berardi, Krstovic
            ovr = 82 + (fvm - 100) / 100.0 * 7.5 # 82 - 89
            prezzo = int(round(130 + (fvm - 100) * 1.25)) # 130 - 255 CR
        elif fvm >= 50: # Simeone, Castro, Raspadori, Dovbyk, Colombo, Pinamonti
            ovr = 74 + (fvm - 50) / 50.0 * 7.5 # 74 - 81
            prezzo = int(round(55 + (fvm - 50) * 1.45)) # 55 - 128 CR
        elif fvm >= 20: # Piccoli, David, Adams, Vitinha, Ghedjemis
            ovr = 66 + (fvm - 20) / 30.0 * 7.5 # 66 - 73
            prezzo = int(round(15 + (fvm - 20) * 1.3)) # 15 - 54 CR
        else:
            ovr = max(48, int(50 + (fvm / 20.0) * 15))
            prezzo = max(1, int(round(1 + (fvm / 20.0) * 13)))

    p['test_ovr'] = int(np.clip(round(ovr), 45, 96))
    p['test_prezzo'] = int(prezzo)

# Verifichiamo i centrocampisti chiave
print("=== VERIFICA NUOVA CURVA CENTROCAMPISTI ===")
targets = ['Paz N.', 'Calhanoglu', 'McTominay', 'Orsolini', 'Pulisic', 'Rabiot', 'De Bruyne', 'Baturina', 'Zaccagni', 'Da Cunha', 'Atta', 'Zaniolo', 'Barella', 'Vlasic', 'Frattesi', 'Taylor K.', 'Mastantuono', 'Moreira', 'Ederson D.S.', 'Rowe', 'Samardzic', 'Politano', 'Gaetano']

for t in targets:
    found = [p for p in players if p['name'] == t or t in p['name']]
    for p in found:
        print(f"{p['name']:<15} (FVM {int(p['fvm']):>3}) -> OVR: {p['test_ovr']} | Prezzo Cons: {p['test_prezzo']:>3} CR")
