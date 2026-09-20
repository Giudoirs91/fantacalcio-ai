import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
ps = json.load(open('processed_players_master.json', encoding='utf-8'))

def find_p(name, role=None):
    clean = name.lower().strip()
    for p in ps:
        if (not role or p['role'] == role) and p['name'].lower() == clean:
            return p
    for p in ps:
        if (not role or p['role'] == role) and (clean in p['name'].lower() or p['name'].lower() in clean):
            return p
    return None

# Definizione dei 5 Archetipi
squads_def = [
    {
        "id": "squad_343",
        "name": "L'Armata Pesante — Tridente Bomber & Lautaro Top",
        "formation": "3-4-3",
        "archetype": "Super-Top Bomber (Lautaro) + Tridente da 45 Gol",
        "tagColor": "#f43f5e",
        "badge": "🔥 LAUTARO + TRIDENTE PESANTE",
        "starters": {
            "P": ["Meret"],
            "D": ["Dimarco", "Tavares N.", "Doig"],
            "C": ["Baturina", "McTominay", "Bernabè", "Colpani"],
            "A": ["Martinez L.", "Scamacca", "Piccoli"]
        },
        "bench": {
            "P": ["Caprile", "Contini"],
            "D": ["Bellanova", "Zappa", "Patric", "Gila", "Chalobah T."],
            "C": ["Frendrup", "Ferguson", "Deiola", "Zarraga"],
            "A": ["Diao", "Trepy", "De Martis"]
        },
        "strategyDescription": "Strategia speculare a quella vincente delle aste reali: punta tutto sul Re dei Bomber <b>Lautaro Martinez (273 CR)</b> affiancato da un 2° slot di spessore come <b>Scamacca (123 CR)</b> e il rigorista <b>Piccoli (18 CR)</b>. A centrocampo l'impatto di <b>Baturina (88 CR)</b> e <b>McTominay (144 CR)</b> garantisce gol continui, mentre la difesa è guidata da <b>Dimarco (85 CR)</b>. La panchina è blindata con la coppia Napoli <b>Meret + Caprile</b> e la sleeper del momento <b>Diao (33 CR)</b>.",
        "whyBeatsRivals": "<ul><li><b>Il Capocannoniere in Rosa</b>: Hai il miglior giocatore del campionato (Lautaro OVR 98) senza aver sacrificato il resto della squadra.</li><li><b>Doppio Titolare da Bonus a Centrocampo</b>: Baturina (2 gol in 3 gare) + McTominay offrono il rendimento di due attaccanti aggiunti.</li><li><b>Panchina Efficace a Costo Minimo</b>: 6 slot a 1 credito e coperture certe su tutti i reparti.</li></ul>"
    },
    {
        "id": "squad_433",
        "name": "La Fortezza Modificatore — Svilar, Difesa d'Oro & Malen Bomber",
        "formation": "4-3-3",
        "archetype": "Porta Blindata + Modificatore +3/+6 & Capocannoniere Malen",
        "tagColor": "#38bdf8",
        "badge": "🛡️ MODIFICATORE DIFESA & MALEN",
        "starters": {
            "P": ["Svilar"],
            "D": ["Molina N.", "Bremer", "Akanji", "Rrahmani"],
            "C": ["Pulisic", "Frattesi", "Bernabè"],
            "A": ["Malen", "Douvikas", "Raimondo"]
        },
        "bench": {
            "P": ["Gollini", "Ryan"],
            "D": ["Tavares N.", "Bellanova", "Zappa", "Patric", "Doig"],
            "C": ["Colpani", "Ferguson", "Frendrup", "Deiola"],
            "A": ["Piccoli", "Trepy", "De Martis"]
        },
        "strategyDescription": "Ispirata alla rosa 'Autogol al 90': investe massicciamente sul modificatore con <b>Svilar (55 CR)</b> tra i pali e una linea a 4 sontuosa con <b>Molina (73 CR)</b>, <b>Bremer (44 CR)</b>, <b>Akanji (41 CR)</b> e <b>Rrahmani (36 CR)</b> per assicurarsi +3 o +6 di bonus difensivo ogni turno. Davanti schiera il capocannoniere assoluto <b>Malen (308 CR)</b> coadiuvato da <b>Douvikas (164 CR)</b> e dalla rivelazione <b>Raimondo (33 CR)</b>.",
        "whyBeatsRivals": "<ul><li><b>Punti Fissi ogni Domenica</b>: Il modificatore di difesa garantisce tra i 60 e gli 80 punti bonus nell'arco della stagione.</li><li><b>Tridente da 35+ Gol</b>: Malen + Douvikas + Raimondo formano uno dei pacchetti offensivi più prolifici del torneo.</li><li><b>Pulisic Incursore</b>: Pulisic (155 CR) inserito a centrocampo funge da 4° attaccante virtuale.</li></ul>"
    },
    {
        "id": "squad_4231",
        "name": "La Ragnatela dei Trequartisti — Calhanoglu, Pulisic, Paz & Kean",
        "formation": "4-2-3-1",
        "archetype": "Centrocampo Dominante (400+ CR) / Fanta-Registi & Rigoristi",
        "tagColor": "#a855f7",
        "badge": "🪄 MEDIANA DEI SOGNI (400 CR)",
        "starters": {
            "P": ["De Gea"],
            "D": ["Kalulu", "Akanji", "Tavares N.", "Doig"],
            "C": ["Paz N.", "Calhanoglu", "Pulisic", "Barella", "Bernabè"],
            "A": ["Kean"]
        },
        "bench": {
            "P": ["Terracciano P.", "Martinelli"],
            "D": ["Bellanova", "Zappa", "Patric", "Gila", "Chalobah T."],
            "C": ["Colpani", "Ferguson", "Frendrup", "Deiola"],
            "A": ["Scamacca", "Piccoli", "Trepy"]
        },
        "strategyDescription": "Riprende la strategia di 'PIROTS 5' e 'Ninja Fuma Foglia': investe oltre 450 crediti sulla mediana per creare il centrocampo più devastante della lega. Il cecchino <b>Calhanoglu (208 CR)</b>, la classe pura di <b>Nico Paz (155 CR)</b>, l'esplosività di <b>Pulisic (155 CR)</b> e la garanzia di <b>Barella (49 CR)</b>. Al centro dell'attacco c'è <b>Kean (162 CR)</b> con un primo cambio di lusso in panchina come <b>Scamacca (123 CR)</b>.",
        "whyBeatsRivals": "<ul><li><b>Dominio Totale della Mediana</b>: I tuoi centrocampisti segnano più degli attaccanti dei tuoi avversari.</li><li><b>Tutti i Piazzati in Pugno</b>: Rigori con Calhanoglu, punizioni e corner con Nico Paz e Pulisic.</li><li><b>Profondità Incredibile</b>: Scamacca in panchina pronto a subentrare per qualsiasi evenienza.</li></ul>"
    },
    {
        "id": "squad_352",
        "name": "Il Tridente Equilibrato — Thuram & Kean (Nessun 300 CR)",
        "formation": "3-5-2",
        "archetype": "Doppia Punta da 15+ Gol / Spesa Spalmata / Zero Dipendenza",
        "tagColor": "#10b981",
        "badge": "⚖️ THURAM + KEAN EQUILIBRIO",
        "starters": {
            "P": ["Maignan"],
            "D": ["Wesley", "Akanji", "Tavares N."],
            "C": ["McTominay", "Frattesi", "Baturina", "Bernabè", "Colpani"],
            "A": ["Thuram", "Kean"]
        },
        "bench": {
            "P": ["Torriani", "Sportiello"],
            "D": ["Bellanova", "Zappa", "Patric", "Gila", "Doig"],
            "C": ["Ferguson", "Frendrup", "Deiola", "Zarraga"],
            "A": ["Raimondo", "Piccoli", "Adams C.", "Trepy"]
        },
        "strategyDescription": "La strategia di 'FC VINO&PERCOCA': non spendere 350-400 crediti per un solo calciatore col rischio che si infortuni, ma acquistare due attaccanti top da 15-18 gol come <b>Marcus Thuram (193 CR)</b> e <b>Moise Kean (162 CR)</b>. Il budget risparmiato viene reinvestito su una porta élite (<b>Maignan 37 CR</b>), su un quinto d'attacco devastante (<b>Wesley 82 CR</b>) e su una mediana con <b>McTominay (144 CR)</b>, <b>Baturina (88 CR)</b> e <b>Frattesi (55 CR)</b>.",
        "whyBeatsRivals": "<ul><li><b>Zero Dipendenza da un Singolo Uomo</b>: Se Thuram rifiata, Kean segna. Se Kean è bloccato, colpiscono McTominay, Baturina o Frattesi.</li><li><b>Attacco Completo</b>: Dalla panchina entrano Raimondo (33 CR) e Che Adams (22 CR).</li><li><b>Rapporto Punti/Prezzo Massimo</b>: Nessun credito sprecato all'asta in duelli a rilancio infinito.</li></ul>"
    },
    {
        "id": "squad_3412",
        "name": "Moneyball Scientifico — Algoritmo xG/xA & Panchina Profonda",
        "formation": "3-4-1-2",
        "archetype": "Massima Efficienza Matematica / 38 Giornate di Continuità",
        "tagColor": "#eab308",
        "badge": "📊 EFFICIENZA PURA xG & STATS",
        "starters": {
            "P": ["Carnesecchi"],
            "D": ["Bremer", "Kalulu", "Tavares N."],
            "C": ["Baturina", "Frattesi", "Barella", "Bernabè"],
            "A": ["Douvikas", "Scamacca", "Raimondo"]
        },
        "bench": {
            "P": ["Musso", "Rossi F."],
            "D": ["Akanji", "Bellanova", "Zappa", "Patric", "Doig"],
            "C": ["Colpani", "Ferguson", "Frendrup", "Deiola"],
            "A": ["Diao", "Adams C.", "Piccoli"]
        },
        "strategyDescription": "La squadra scientifica basata sui dati avanzati 2026/27: punta sui calciatori che producono il più alto volume di Expected Goals e assist per credito speso. In porta <b>Carnesecchi (43 CR)</b> con le sue 18 parate in 3 gare; difesa solida guidata da <b>Bremer (44 CR)</b>; centrocampo mobile e continuo; attacco atomico composto da <b>Douvikas (164 CR)</b>, <b>Scamacca (123 CR)</b> e <b>Raimondo (33 CR)</b> con alternative immediate come <b>Diao (33 CR)</b> e <b>Adams (22 CR)</b>.",
        "whyBeatsRivals": "<ul><li><b>Rosa da 18 Titolari</b>: Praticamente ogni giocatore in panchina gioca e porta voto ogni settimana.</li><li><b>Spesa Chirurgica (~960 CR)</b>: Nessun buco in rosa, zero titolari fantasma, margini per svincoli e scambi.</li><li><b>Resistente agli Infortuni</b>: Perfetta per vincere una lega lunga a 38 giornate grazie alla profondità.</li></ul>"
    }
]

print("Verifica budget e composizione:")
for sq in squads_def:
    spent = 0
    p_count = 0
    missing = []
    
    for r in ['P', 'D', 'C', 'A']:
        for n in sq['starters'][r]:
            p = find_p(n, r)
            if not p: missing.append((n, r, 'starter'))
            else: spent += p['prezzo_cons']; p_count += 1
        for n in sq['bench'][r]:
            p = find_p(n, r)
            if not p: missing.append((n, r, 'bench'))
            else: spent += p['prezzo_cons']; p_count += 1
            
    print(f"\n• {sq['name']} ({sq['formation']}):")
    print(f"  Giocatori totali: {p_count}/25 | Spesa calcolata: {spent}/1000 CR (Liberi: {1000 - spent} CR)")
    if missing:
        print(f"  [ATTENZIONE] Mancanti: {missing}")
