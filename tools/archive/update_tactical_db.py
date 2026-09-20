import json

with open('config/tactical_db.json', 'r', encoding='utf-8') as f:
    tac = json.load(f)

# 1. Atalanta
tac["Atalanta"]["flop"] = ["Godfrey"]
tac["Atalanta"]["sleeper"] = ["Samardzic", "Zalewski", "Rowe"]

# 2. Como
tac["Como"]["rigoristi"] = ["Kean", "Paz N.", "Douvikas"]
tac["Como"]["punizioni"] = ["Paz N.", "Baturina"]
tac["Como"]["corner"] = ["Paz N.", "Baturina"]
tac["Como"]["top"] = ["Kean", "Paz N.", "Couto"]
for p in tac["Como"]["lineup"]:
    if p["name"] == "Douvikas" or p["pos"] == "PC":
        p["name"] = "Kean"
        p["status"] = "1° Terminale Offensivo (Top Acquisto)"
    if p["name"] == "Nico Paz":
        p["name"] = "Paz N."

# 3. Fiorentina
tac["Fiorentina"]["rigoristi"] = ["Beto", "Goncalves P.", "Fagioli"]
tac["Fiorentina"]["punizioni"] = ["Goncalves P.", "Fagioli", "Mastantuono"]
tac["Fiorentina"]["corner"] = ["Goncalves P.", "Fagioli"]
tac["Fiorentina"]["top"] = ["Beto", "Goncalves P.", "Dodo"]
tac["Fiorentina"]["sleeper"] = ["Mastantuono", "Gnonto", "Ndour"]
for p in tac["Fiorentina"]["lineup"]:
    if p["name"] == "Kean" or p["pos"] == "PC":
        p["name"] = "Beto"
        p["status"] = "1° Punta Titolare (Nuovo Acquisto)"
    elif p["name"] == "Gudmundsson" or p["pos"] == "AS":
        p["name"] = "Gnonto"
        p["status"] = "Ala Sinistra (Nuovo Acquisto)"
    elif p["name"] == "Mandragora" or p["pos"] == "MED":
        p["name"] = "Goncalves P."
        p["pos_label"] = "Mezzala Offensiva"
        p["status"] = "Top Centrocampista (Nuovo Acquisto)"

# 4. Lazio
tac["Lazio"]["rigoristi"] = ["Zaccagni", "Gudmundsson A.", "Castellanos"]
tac["Lazio"]["top"] = ["Zaccagni", "Gudmundsson A.", "Tavares N."]
tac["Lazio"]["punizioni"] = ["Tavares N.", "Gudmundsson A.", "Zaccagni"]
tac["Lazio"]["corner"] = ["Tavares N.", "Gudmundsson A.", "Zaccagni"]
for p in tac["Lazio"]["lineup"]:
    if p["name"] in ["Dia", "Castellanos"] and p["pos"] in ["TRQ", "AS", "PC"]:
        if p["pos"] == "TRQ" or p["name"] == "Dia":
            p["name"] = "Gudmundsson A."
            p["status"] = "Top Trequartista / Seconda Punta"
    if p["name"] == "Nuno Tavares":
        p["name"] = "Tavares N."

# 5. Juventus
tac["Juventus"]["rigoristi"] = ["Vlahovic", "Koopmeiners", "Woltemade"]
tac["Juventus"]["sleeper"] = ["Woltemade", "Conceicao", "Sarr P."]
tac["Juventus"]["flop"] = ["Arthur"]

# 6. Torino
tac["Torino"]["rigoristi"] = ["Zapata", "Adams", "Mandragora"]
tac["Torino"]["punizioni"] = ["Mandragora", "Ilic", "Sosa"]
tac["Torino"]["top"] = ["Zapata", "Ricci", "Milinkovic-Savic"]
tac["Torino"]["sleeper"] = ["Mandragora", "Adams", "Coco"]
for p in tac["Torino"]["lineup"]:
    if p["name"] == "Pedersen":
        p["name"] = "Lazaro"
    if p["pos"] == "MED_D" or p["name"] == "Tameze":
        p["name"] = "Mandragora"
        p["status"] = "Titolare Mediana (Nuovo Acquisto)"

# 7. Inter
tac["Inter"]["rigoristi"] = ["Calhanoglu", "Martinez L.", "Taremi"]
tac["Inter"]["top"] = ["Martinez L.", "Calhanoglu", "Dimarco"]
tac["Inter"]["sleeper"] = ["Esposito F.P.", "Sucic P.", "Diouf"]
for p in tac["Inter"]["lineup"]:
    if p["name"] in ["Lautaro Martinez", "Lautaro"]:
        p["name"] = "Martinez L."
    if p["name"] == "Esposito P.":
        p["name"] = "Esposito F.P."

# 8. Milan
for p in tac["Milan"]["lineup"]:
    if p["name"] == "Goncalo Ramos":
        p["name"] = "Ramos G."
tac["Milan"]["rigoristi"] = ["Pulisic", "Ramos G.", "Hernandez T."]
tac["Milan"]["top"] = ["Pulisic", "Leao", "Ramos G."]

# 9. Lecce
for p in tac["Lecce"]["lineup"]:
    if p["name"] == "Danilo Veiga":
        p["name"] = "Veiga D."
tac["Lecce"]["top"] = ["Veiga D.", "Krstovic", "Falcone"]
tac["Lecce"]["punizioni"] = ["Veiga D.", "Berisha M."]
tac["Lecce"]["corner"] = ["Veiga D.", "Berisha M."]

# 10. Bologna
tac["Bologna"]["sleeper"] = ["Alhassane", "Odgaard", "Mbangula"]

# 11. Genoa
tac["Genoa"]["sleeper"] = ["Drameh", "Miretti", "Marcandalli"]
for p in tac["Genoa"]["lineup"]:
    if p["name"] == "Norton-Cuffy":
        p["name"] = "Drameh"
        p["status"] = "Titolare / Ballottaggio Sabelli"

# 12. Napoli
for p in tac["Napoli"]["lineup"]:
    if p["name"] == "Rafa Marin":
        p["name"] = "Marin R."
tac["Napoli"]["sleeper"] = ["Marin R.", "Spinazzola", "Ngonge"]

# 13. Parma
for p in tac["Parma"]["lineup"]:
    if p["name"] in ["Konate", "Ndiaye"]:
        p["name"] = "Diego Carlos"
        p["status"] = "Leader Difesa (Nuovo Acquisto)"
tac["Parma"]["sleeper"] = ["Diego Carlos", "Sohm", "Almqvist"]

# 14. Sassuolo
for p in tac["Sassuolo"]["lineup"]:
    if p["name"] in ["Macchioni", "Missori"]:
        p["name"] = "Caleta-Car"
        p["status"] = "Centrale Difesa (Nuovo Acquisto)"
tac["Sassuolo"]["sleeper"] = ["Caleta-Car", "Sulemana I.", "Volpato"]

# 15. Venezia
for p in tac["Venezia"]["lineup"]:
    if p["name"] in ["Kike Perez", "Perez"]:
        p["name"] = "Perez K."

with open('config/tactical_db.json', 'w', encoding='utf-8') as f:
    json.dump(tac, f, ensure_ascii=False, indent=2)

print('Updated config/tactical_db.json successfully!')
