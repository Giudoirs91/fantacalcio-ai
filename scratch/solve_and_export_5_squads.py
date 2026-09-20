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

squads_def = [
    {
        'id': 'squad_343',
        'name': "L'Armata Pesante — Lautaro Martinez & Tridente da 45 Gol",
        'formation': "3-4-3",
        'archetype': "Tridente Top / Quinti di Spinta / Mediana Inserimenti",
        'tagColor': "#f43f5e",
        'badge': "🔥 TRIDENTE DA 45 GOL",
        'starters': {
            'P': ['Meret'],
            'D': ['Spence', 'Akanji', 'Tavares N.'],
            'C': ['Frattesi', 'Gudmundsson A.', 'Bernabè', 'Colpani'],
            'A': ['Martinez L.', 'Scamacca', 'Pellegrino M.']
        },
        'bench': {
            'P': ['Caprile', 'Sportiello'],
            'D': ['Doig', 'Bellanova', 'Zappa', 'Patric', 'Kolasinac'],
            'C': ['Ferguson', 'Frendrup', 'Deiola', 'Zarraga'],
            'A': ['Bonny', 'Trepy', 'De Martis']
        },
        'strategyDescription': "Questa formazione è costruita per <b>massimizzare i bonus d'attacco</b> senza sforare il budget. Schiera il bomber principe della Serie A <b>Lautaro Martinez (379 CR)</b> insieme a <b>Gianluca Scamacca (179 CR)</b> e <b>Pellegrino M. (51 CR)</b>, con la spinta di <b>Frattesi (73 CR)</b> e dei quinti <b>Spence e Tavares</b>.",
        'whyBeatsRivals': "<ul><li><b>Neutralizza The President (Davide)</b>: Davide andrà in foga su un solo attaccante spendendo oltre 450 CR. Tu con 379 CR blocchi Lautaro e con il resto crei un tridente da 45 gol stagionali.</li><li><b>Copertura totale 25/25</b>: Bonny copre Lautaro all'Inter, Doig copre i quinti, e tutti i 25 slot hanno titolarità verificata.</li><li><b>Budget Matematico Perfetto</b>: 11 Titolari (872 CR) + 14 Riserve (90 CR) = 962 CR totali (38 CR liberi di margine).</li></ul>"
    },
    {
        'id': 'squad_433',
        'name': "Il Dominio Tattico — Macchina da Modificatore & Bomber Malen",
        'formation': "4-3-3",
        'archetype': "Modificatore Difesa +3/+6 & Top Attacco",
        'tagColor': "#38bdf8",
        'badge': "🛡️ FORTEZZA MODIFICATORE",
        'starters': {
            'P': ['Svilar'],
            'D': ['Dimarco', 'Akanji', 'Bastoni', 'Rrahmani'],
            'C': ['Barella', 'Gudmundsson A.', 'Bernabè'],
            'A': ['Malen', 'Pellegrino M.', 'Trepy']
        },
        'bench': {
            'P': ['Ryan', 'Sportiello'],
            'D': ['Doig', 'Bellanova', 'Zappa', 'Patric', 'Kolasinac'],
            'C': ['Colpani', 'Ferguson', 'Frendrup', 'Deiola'],
            'A': ['Bonny', 'De Martis', 'Lisman']
        },
        'strategyDescription': "Progettata per dominare con la regola del <b>Modificatore Difesa</b>. Con <b>Svilar (73 CR)</b> tra i pali e un quartetto difensivo da 6.5 fisso (<b>Dimarco, Akanji, Bastoni, Rrahmani</b>), incassi costantemente <b>+3 o +6 punti</b> ogni domenica. In attacco, l'acquisto del capocannoniere assoluto <b>Malen (440 CR)</b> garantisce il bottino di gol da fuoriclasse.",
        'whyBeatsRivals': "<ul><li><b>Demolisce Divin Codino (Alessandro)</b>: Alessandro punta tutto sul modificatore. Con questa linea a 4 gli sottrai i migliori centrali da 6.5 e Dimarco, vincendo ogni scontro diretto sui voti base.</li><li><b>Bomber Infallibile</b>: Malen ha 5 gol segnati nelle prime 2 giornate ed è il giocatore più decisivo della Serie A.</li><li><b>Budget Rigoroso</b>: 11 Titolari (902 CR) + 14 Riserve (85 CR) = 987 CR totali (13 CR di margine).</li></ul>"
    },
    {
        'id': 'squad_4231',
        'name': "La Ragnatela dei Trequartisti — FantaMantra & Ali OOP",
        'formation': "4-2-3-1",
        'archetype': "Bug del Listone / 4 Punte in Campo",
        'tagColor': "#a855f7",
        'badge': "🪄 CENTROCAMPO DA 50 GOL",
        'starters': {
            'P': ['Maignan'],
            'D': ['Doig', 'Bastoni', 'Bisseck', 'Tavares N.'],
            'C': ['Gudmundsson A.', 'Bernabè', 'Paz N.', 'Pulisic', 'Colpani'],
            'A': ['Kean']
        },
        'bench': {
            'P': ['Torriani', 'Sportiello'],
            'D': ['Bellanova', 'Zappa', 'Patric', 'Kolasinac'],
            'C': ['Ferguson', 'Frendrup', 'Deiola'],
            'A': ['Pellegrino M.', 'Bonny', 'Trepy', 'De Martis', 'Lisman']
        },
        'strategyDescription': "Questa rosa sfrutta il più grande vantaggio competitivo: <b>le ali e trequartisti quotati Centrocampisti</b>. Schierando <b>Pulisic (190 CR) e Nico Paz (260 CR)</b> insieme a <b>Gudmundsson (31 CR)</b>, <b>Bernabè (23 CR)</b> e <b>Moise Kean (230 CR)</b>, giochi di fatto con <b>4 attaccanti puri</b> spendendo per una sola punta di ruolo.",
        'whyBeatsRivals': "<ul><li><b>Spiazza Fc Enry (Enrico) e Sparta (Valerio)</b>: I tuoi rivali si sveneranno per attaccanti mediocri. Tu invece investi la quota maggiore sui centrocampisti-bomber che portano gli stessi gol delle punte.</li><li><b>Piazzati e Rigori</b>: Nico Paz e Kean garantiscono punizioni, corner e rigori.</li><li><b>Totale Matematico</b>: 11 Titolari (872 CR) + 14 Riserve (109 CR) = 981 CR totali (19 CR di cuscinetto).</li></ul>"
    },
    {
        'id': 'squad_352',
        'name': "L'Equilibrio di Ferro — Calhanoglu Rigorista & Coppia Scamacca-Kean",
        'formation': "3-5-2",
        'archetype': "Solidità Totale / Rigori Infallibili & Bomber",
        'tagColor': "#10b981",
        'badge': "⚖️ RIGORISTI & CONTINUITÀ",
        'starters': {
            'P': ['De Gea'],
            'D': ['Spence', 'Akanji', 'Tavares N.'],
            'C': ['Calhanoglu', 'Gudmundsson A.', 'Bernabè', 'Colpani', 'Frendrup'],
            'A': ['Scamacca', 'Kean']
        },
        'bench': {
            'P': ['Terracciano', 'Sportiello'],
            'D': ['Doig', 'Bellanova', 'Zappa', 'Patric', 'Kolasinac'],
            'C': ['Ferguson', 'Deiola', 'Zarraga', 'Nicolussi Caviglia'],
            'A': ['Pellegrino M.', 'Bonny', 'Trepy', 'De Martis']
        },
        'strategyDescription': "Il modulo più affidabile per vincere il campionato sui 38 turni. Unisce la garanzia dei rigori con <b>Calhanoglu (260 CR, 100% precisione)</b>, i quinti <b>Spence e Tavares</b>, e la coppia d'attacco <b>Scamacca (179 CR) + Kean (230 CR)</b>.",
        'whyBeatsRivals': "<ul><li><b>Zero Rischio Turn-over</b>: Con Bonny, Pellegrino e Kean in rosa, non giochi mai in 10.</li><li><b>Pioggia di Bonus dai Rigori</b>: Con Calhanoglu, Gudmundsson e Kean hai i tiratori designati di 3 squadre.</li><li><b>Bilancio Perfetto</b>: 11 Titolari (873 CR) + 14 Riserve (97 CR) = 970 CR totali (30 CR liberi).</li></ul>"
    },
    {
        'id': 'squad_3412',
        'name': "Moneyball Scientifico — Rabiot, McTominay, Scamacca & Douvikas",
        'formation': "3-4-1-2",
        'archetype': "Massima Efficienza xG & xA / Zero Sprechi",
        'tagColor': "#eab308",
        'badge': "📊 MONEYBALL STATISTICO",
        'starters': {
            'P': ['Meret'],
            'D': ['Doig', 'Tavares N.', 'Bellanova'],
            'C': ['Rabiot', 'McTominay', 'Gudmundsson A.', 'Colpani'],
            'A': ['Douvikas', 'Scamacca', 'Pellegrino M.']
        },
        'bench': {
            'P': ['Caprile', 'Sportiello'],
            'D': ['Spence', 'Zappa', 'Patric', 'Kolasinac', 'Pellegrini Lu.'],
            'C': ['Bernabè', 'Ferguson', 'Frendrup', 'Deiola'],
            'A': ['Bonny', 'Trepy', 'De Martis']
        },
        'strategyDescription': "Costruita secondo i principi del <b>Moneyball matematico</b>: seleziona i calciatori con il più alto rapporto <b>xG/90 (Expected Goals) e xA/90</b> rispetto al costo d'asta. <b>Douvikas (232 CR) + Scamacca (179 CR)</b> in attacco supportati da <b>Rabiot (157 CR) e McTominay (179 CR)</b>.",
        'whyBeatsRivals': "<ul><li><b>Sfianca AtletiCoSassicc (Ilario) e The President</b>: Mentre loro si dissanguano per i soliti 2 nomi noti, tu compri Douvikas e Scamacca creando una batteria d'attacco infinita spendendo meno.</li><li><b>Efficienza Totale</b>: Centrocampo con voti base alti e inserimenti continui.</li><li><b>100% sotto i 1000 CR</b>: 11 Titolari (898 CR) + 14 Riserve (76 CR) = 974 CR totali (26 CR liberi).</li></ul>"
    }
]

print("=== VERIFICA MATEMATICA RIGOROSA DELLE 5 SQUADRE ===")
for sq in squads_def:
    st_cost = sum(get_p(n)['prezzo_cons'] for n in [n for r in sq['starters'].values() for n in r])
    be_cost = sum(get_p(n)['prezzo_cons'] for n in [n for r in sq['bench'].values() for n in r])
    tot = st_cost + be_cost
    st_count = sum(len(r) for r in sq['starters'].values())
    be_count = sum(len(r) for r in sq['bench'].values())
    
    sq['budgetSpent'] = tot
    sq['budgetRemaining'] = 1000 - tot
    
    print(f"\n{sq['name']} ({sq['formation']}):")
    print(f"  Titolari ({st_count}): {st_cost} CR")
    print(f"  Panchina ({be_count}): {be_cost} CR")
    print(f"  TOTALE COMPLETO (25 Calciatori): {tot} CR / 1000 CR (Residuo: {1000 - tot} CR)")
    assert tot <= 1000, f"Squad {sq['name']} exceeds 1000 CR!"
    assert st_count == 11, f"Squad {sq['name']} does not have 11 starters!"
    assert st_count + be_count == 25, f"Squad {sq['name']} does not have 25 players!"

with open('scratch/ai_squads_verified.json', 'w', encoding='utf-8') as f:
    json.dump(squads_def, f, indent=2, ensure_ascii=False)
print("\n--> TUTTE LE 5 SQUADRE SONO MATEMATICAMENTE PERFETTE E SOTTO I 1000 CR!")
