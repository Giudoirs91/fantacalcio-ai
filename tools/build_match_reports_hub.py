import os
import sys
import json
import re
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

MATCHES_JSON = os.path.join(ROOT_DIR, "data", "raw", "match_reports_matches_g1_g2.json")
PLAYERS_CSV = os.path.join(ROOT_DIR, "data", "raw", "match_reports_players_g1_g2.csv")
TEAMS_JSON = os.path.join(ROOT_DIR, "data", "raw", "match_reports_teams.json")
RANKINGS_JSON = os.path.join(ROOT_DIR, "data", "raw", "match_reports_rankings_physical.json")
OUT_JSON = os.path.join(ROOT_DIR, "data", "processed", "match_reports_hub.json")

# Custom AI Analysis commentary for Giornata 8 matches
G8_AI_ANALYSIS = {
    "CAGLIARI 0-2 BOLOGNA": {
        "summary": "Il Bologna di Italiano sbanca la Unipol Domus con una prova matura e di totale controllo tattico, blindando il risultato con i gol di Casale e Bernardeschi. Cagliari generoso ma poco incisivo nel terzo finale.",
        "fantacalcio_impact": "Bernardeschi ritrova lo status da primo slot d'attacco con gol (+3) e giocate di altissima qualità. Casale regala un +3 a sorpresa da corner. Skorupski porta a casa il clean sheet con voto solido. Nel Cagliari poche sufficienze, Caprile evita un passivo più pesante.",
        "man_of_the_match": "Federico Bernardeschi (Bologna) — Gol, qualità e pericolosità costante nel 3-4-3.",
        "key_stat": "Bologna con il 60%+ di possesso e Skorupski con 0 gol subiti (Clean Sheet)."
    },
    "COMO 2-0 SASSUOLO": {
        "summary": "Trionfo spettacolare del Como di Fabregas al Sinigaglia: ritmo europeo, fraseggio rapido e una doppietta letale di Anastasios Douvikas che annichilisce il Sassuolo.",
        "fantacalcio_impact": "Douvikas è il crack assoluto della giornata con una doppietta da favola (+6) e 3 tiri nello specchio. Caqueret sforna assist e 4 passaggi chiave (+1). Butez ottiene il clean sheet. Nel Sassuolo Turati si arrende dopo 4 parate; l'attacco neroverde non punge.",
        "man_of_the_match": "Anastasios Douvikas (Como) — Doppietta d'autore, presenza fisica e senso del gol da top di reparto.",
        "key_stat": "Douvikas 2 gol con 3 conclusioni nello specchio; Caqueret oltre 11.7 km percorsi e 1 assist."
    },
    "INTER 2-1 FIORENTINA": {
        "summary": "Successo di carattere e sofferenza per l'Inter a San Siro. Marcus Thuram e Zieliński firmano il 2-0, poi Jiménez accorcia per la Fiorentina che sbatte contro la difesa nerazzurra e deve ringraziare uno straordinario De Gea per aver tenuto viva la partita.",
        "fantacalcio_impact": "Marcus Thuram mostruoso: 9 tiri totali e gol vittoria (+3). Zieliński chirurgico al tiro (+3). Diouf e Fagioli regalano assist (+1). Nota di merito assoluta per David De Gea: nonostante i 2 gol subiti, compie 9 parate miracolose meritando un voto da fuoriclasse.",
        "man_of_the_match": "Marcus Thuram (Inter) — Dominante a livello fisico e balistico, 9 conclusioni verso la porta viola.",
        "key_stat": "David De Gea 9 parate decisive, record stagionale di parate in un singolo big match."
    },
    "LAZIO 2-1 PARMA": {
        "summary": "Vittoria fondamentale della Lazio all'Olimpico contro un Parma combattivo. I biancocelesti passano con Taylor e un'autorete sfortunata di Diego Carlos, mentre i ducali rispondono con il sigillo del promettente Lontani.",
        "fantacalcio_impact": "Nuno Tavares è un treno inarrestabile: 12.38 km percorsi (leader del match) e cross a ripetizione. Taylor ripaga la fiducia con il gol (+3). Nel Parma gioia per il giovane Lontani (+3 su assist di Fabbian), ma pesa il malus autogol di Diego Carlos (-2).",
        "man_of_the_match": "Nuno Tavares (Lazio) — Prestazione dominante lungo l'out sinistro: 12.38 km e spinta instancabile.",
        "key_stat": "Nuno Tavares 12.38 km corsi ad altissima intensità; Lazio padrona delle fasce."
    },
    "NAPOLI 3-3 ROMA": {
        "summary": "Derby del Sole leggendario al Diego Armando Maradona: 6 reti, sorpassi e controsorpassi a viso aperto. Anguissa e una superlativa doppietta di McTominay trascinano il Napoli; la Roma risponde colpo su colpo con la magia di Soulé e l'incredibile doppietta del difensore Balerdi.",
        "fantacalcio_impact": "Trionfo di bonus per i fantallenatori: McTominay fa sfracelli a centrocampo con una doppietta (+6) e 12.49 km percorsi. Leonardo Balerdi firma una clamorosa doppietta da difensore centrale (+6 da sogno!). Assist per Olivera, Politano, Wesley e Malen (quest'ultimo con 5 passaggi chiave). Entrambi i portieri pagano i 3 gol subiti ma Gollini effettua 6 grandi parate.",
        "man_of_the_match": "Scott McTominay (Napoli) & Leonardo Balerdi (Roma) — Entrambi mattatori assoluti con doppietta a referto.",
        "key_stat": "McTominay 12.49 km corsi e 2 gol; Balerdi 2 gol con 2 tiri nello specchio."
    },
    "TORINO 3-2 MONZA": {
        "summary": "Gara elettrizzante e ricca di colpi di scena all'Olimpico Grande Torino. I granata superano il Monza per 3-2 grazie alle reti di Belghali, Vlašić e Fitz-Jim. Per i brianzoli non bastano il gol di Varela e l'autorete di Patterson.",
        "fantacalcio_impact": "Nikola Vlašić leader assoluto: gol del +3 e ben 12.30 km percorsi da vero maratoneta. Sorprese Belghali e Fitz-Jim a segno (+3 ciascuno). Assist pregiati di Simeone e Gineitis. Nel Monza Varela conferma il suo momento d'oro con l'ennesimo gol (+3); Patterson rimedia il malus autogol.",
        "man_of_the_match": "Nikola Vlašić (Torino) — Faro della manovra granata: qualità realizzativa, oltre 12 km percorsi e carisma.",
        "key_stat": "Aboukhlal (Monza) tocca il picco velocistico del turno con 29.80 km/h in sprint."
    },
    "GENOA 1-0 VENEZIA": {
        "summary": "Il Genoa di Daniele De Rossi conquista 3 punti d'oro a Marassi piegando il Venezia di Davide Nicola per 1-0. Decide il match la combinazione al 25' tra El Shaarawy ed Ellertsson, con i padroni di casa in controllo quasi totale del ritmo gara.",
        "fantacalcio_impact": "Mikael Ellertsson colpisce da centrocampista incursore regalando un +3 prezioso. Stephan El Shaarawy si dimostra ispiratissimo sfornando l'assist decisivo (+1). Justin Bijlow porta a casa un clean sheet impeccabile con voto favorevole per il modificatore. Nel Venezia gara di sacrificio per Yeboah e Adams che restano a secco di occasioni.",
        "man_of_the_match": "Mikael Ellertsson (Genoa) — Tempismo perfetto nell'inserimento da gol, intensità e strappi continui lungo la corsia.",
        "key_stat": "Genoa con quasi il 69% di possesso palla e 0 gol subiti (Clean Sheet per Bijlow)."
    },
    "LECCE 0-2 JUVENTUS": {
        "summary": "Autoritaria vittoria della Juventus di Luciano Spalletti al Via del Mare. I bianconeri archiviano la pratica Lecce già nella prima frazione con le firme d'autore di Weston McKennie e Douglas Luiz, controllando il match con oltre il 71% di possesso palla.",
        "fantacalcio_impact": "Serata trionfale per la mediana bianconera: Douglas Luiz fa registrare un sontuoso +4 (gol e assist), imponendosi come dominatore della partita. McKennie ritrova il bonus pesante (+3) e Gatti aggiunge un assist (+1). Guglielmo Vicario ottiene il clean sheet con zero pericoli. Nel Lecce serata amarissima per Kialonda Gaspar: doppio giallo ed espulsione al 94' con pesante malus a referto.",
        "man_of_the_match": "Douglas Luiz (Juventus) — Gol, assist e regia da fuoriclasse: prestazione dominante in entrambe le fasi.",
        "key_stat": "Juventus con il 71.3% di possesso palla e 0 tiri nello specchio concessi al Lecce."
    },
    "UDINESE 0-2 MILAN": {
        "summary": "Grande prova di maturità e qualità del Milan di Rúben Amorim al Bluenergy Stadium di Udine. Il Diavolo sblocca subito la contesa con un lampo di Christian Pulisic (su assist di Modric) e raddoppia prima dell'intervallo con Gonçalo Ramos, congelando la ripresa con oltre l'80% di possesso palla.",
        "fantacalcio_impact": "Pulisic conferma il suo status da top di reparto con il gol fulmineo del +3. Luka Modric illumina il campo da professore aggiungendo un altro assist vincente (+1). Gonçalo Ramos ripaga la maglia da titolare trovando il gol (+3). Mike Maignan sigilla la porta con un clean sheet di assoluta tranquillità. Nell'Udinese Keinan Davis lotta ma la retroguardia friulana cede al palleggio rossonero.",
        "man_of_the_match": "Christian Pulisic (Milan) — Imprendibile tra le linee, sblocca il match a freddo e semina il panico palla al piede.",
        "key_stat": "Milan padrone assoluto del campo con l'80.9% di possesso palla e clean sheet per Maignan."
    },
    "ATALANTA 4-4 FROSINONE": {
        "summary": "Spettacolo pirotecnico alla New Balance Arena di Bergamo: una sfida al cardiopalma tra Atalanta e Frosinone che si chiude con un clamoroso 4-4 e 8 reti totali. Frosinone due volte avanti con la doppietta fulminea di Romano Schmid e la pennellata di Giacomo Calò; l'Atalanta reagisce furiosamente trascinata dalla doppietta di Krstović e dai sigilli di Éderson ed Elmas. Nel finale i ciociari strappano il pari con Aleksa Terzić, mentre la Dea chiude in 10 per l'espulsione di Éderson.",
        "fantacalcio_impact": "Festa clamorosa di bonus e malus: Nikola Krstović è incontenibile con una doppietta da favola e 1 assist vincente (+7 complessivo!). Eljif Elmas ripaga la fiducia con il gol del +3. Nel Frosinone prestazione stellare per Romano Schmid (doppietta del +6) e soprattutto per Farès Ghedjemis, autore di un'incredibile tripletta di assist (+3 totale!). Bonus anche per Calò (+3) e Terzić (+3). Serata da incubo per i portieri Carnesecchi e Palmisani (4 gol subiti a testa) e per Éderson, che dopo il gol del +3 viene espulso al 69' per doppio giallo con pesante malus a referto.",
        "man_of_the_match": "Nikola Krstović (Atalanta) & Farès Ghedjemis (Frosinone) — Krstović trascinatore con 2 gol e 1 assist; Ghedjemis visionario puro con 3 assist vincenti.",
        "key_stat": "8 gol totali, 19 tiri nello specchio complessivi e tripletta di assist per Farès Ghedjemis."
    }
}

def build_match_reports_hub():
    print("=== [Build Match Reports Hub] Generazione archivio interattivo Match Reports ===")
    
    if not os.path.exists(MATCHES_JSON) or not os.path.exists(PLAYERS_CSV):
        print("[ERRORE] File dati match reports non trovati.")
        return {}

    with open(MATCHES_JSON, 'r', encoding='utf-8') as f:
        matches_raw = json.load(f)

    df_players = pd.read_csv(PLAYERS_CSV)
    
    teams_stats_lookup = {}
    if os.path.exists(TEAMS_JSON):
        try:
            with open(TEAMS_JSON, 'r', encoding='utf-8') as f:
                teams_data = json.load(f)
                for t in teams_data:
                    key = (t.get('giornata'), t.get('match_name'), t.get('team'))
                    teams_stats_lookup[key] = t
        except Exception as e:
            print(f"Errore caricamento teams stats: {e}")

    rankings_lookup = {}
    if os.path.exists(RANKINGS_JSON):
        try:
            with open(RANKINGS_JSON, 'r', encoding='utf-8') as f:
                r_data = json.load(f)
                for r in r_data:
                    key = (r.get('giornata'), r.get('match_name'))
                    rankings_lookup[key] = r
        except Exception as e:
            print(f"Errore caricamento rankings: {e}")

    hub_by_round = {}

    for m in matches_raw:
        giornata = m.get('giornata', 1)
        m_title = m.get('match_title', '')
        home_team = m.get('home_team', '')
        away_team = m.get('away_team', '')
        score_home = m.get('score_home', 0)
        score_away = m.get('score_away', 0)
        moduli = m.get('moduli', [])
        
        match_id = f"g{giornata}_{home_team[:3].lower()}_{away_team[:3].lower()}"

        # Filtra calciatori per questa partita e giornata
        df_m = df_players[(df_players['giornata'] == giornata) & (df_players['match_name'] == m_title)]
        
        players_list = []
        scorers = []
        assisters = []
        own_goals = []
        yellow_cards = []
        red_cards = []
        goalkeepers = []

        home_starters = []
        away_starters = []
        home_bench = []
        away_bench = []

        for _, row in df_m.iterrows():
            p_dict = row.to_dict()
            pname = str(p_dict.get('player_name', '')).strip()
            team = str(p_dict.get('team', '')).strip()
            is_home = bool(p_dict.get('is_home', False))
            is_starter = bool(p_dict.get('is_starter', False))
            is_gk = bool(p_dict.get('role_gk', False))
            
            p_info = {
                'shirt_num': int(p_dict.get('shirt_num', 0)),
                'name': pname,
                'team': team,
                'is_home': is_home,
                'is_starter': is_starter,
                'is_gk': is_gk,
                'minutes': int(p_dict.get('minutes', 0)),
                'goals': int(p_dict.get('goals', 0)),
                'own_goals': int(p_dict.get('own_goals', 0) or 0),
                'assists': int(p_dict.get('assists', 0)),
                'shots': int(p_dict.get('total_shots', 0)),
                'shots_target': int(p_dict.get('shots_on_target', 0)),
                'key_passes': int(p_dict.get('key_passes', 0)),
                'recoveries': int(p_dict.get('ball_recoveries', 0)),
                'passes_completed': int(p_dict.get('passes_completed', 0)),
                'pass_acc': float(p_dict.get('pass_accuracy_pct', 0.0) or 0.0),
                'yellows': int(p_dict.get('yellow_cards', 0)),
                'reds': int(p_dict.get('red_cards', 0) or 0) + int(p_dict.get('double_yellows', 0) or 0),
                'km_distance': round(float(p_dict.get('km_distance', 0.0) or 0.0), 2),
                'sprint_speed_max': round(float(p_dict.get('sprint_speed_max', 0.0) or 0.0), 2),
                'saves': int(p_dict.get('saves', 0)),
                'goals_conceded': int(p_dict.get('goals_conceded', 0)),
                'clean_sheet': int(p_dict.get('clean_sheet', 0))
            }
            players_list.append(p_info)

            if p_info['goals'] > 0:
                scorers.append({'name': pname, 'team': team, 'goals': p_info['goals']})
            if p_info['own_goals'] > 0:
                own_goals.append({'name': pname, 'team': team, 'own_goals': p_info['own_goals']})
            if p_info['assists'] > 0:
                assisters.append({'name': pname, 'team': team, 'assists': p_info['assists']})
            if p_info['yellows'] > 0:
                yellow_cards.append({'name': pname, 'team': team})
            if p_info['reds'] > 0:
                red_cards.append({'name': pname, 'team': team})
            if is_gk:
                goalkeepers.append(p_info)

            if is_home:
                if is_starter:
                    home_starters.append(p_info)
                elif p_info['minutes'] > 0:
                    home_bench.append(p_info)
            else:
                if is_starter:
                    away_starters.append(p_info)
                elif p_info['minutes'] > 0:
                    away_bench.append(p_info)

        # Team stats
        t_home = teams_stats_lookup.get((giornata, m_title, home_team), {})
        t_away = teams_stats_lookup.get((giornata, m_title, away_team), {})

        # Top physical performers
        sorted_km = sorted([p for p in players_list if p['km_distance'] > 0], key=lambda x: x['km_distance'], reverse=True)[:3]
        sorted_speed = sorted([p for p in players_list if p['sprint_speed_max'] > 0], key=lambda x: x['sprint_speed_max'], reverse=True)[:3]

        # AI Analysis
        ai_data = G8_AI_ANALYSIS.get(m_title, {
            "summary": f"Sfida ad alta intensità tattica tra {home_team} e {away_team} terminata sul punteggio di {score_home}-{score_away}.",
            "fantacalcio_impact": "Dati ufficiali estratti a referto per le statistiche individuali e di squadra.",
            "man_of_the_match": scorers[0]['name'] if scorers else (players_list[0]['name'] if players_list else "Migliore in campo"),
            "key_stat": f"Risultato finale: {score_home}-{score_away}"
        })

        match_record = {
            'match_id': match_id,
            'giornata': giornata,
            'match_title': m_title,
            'home_team': home_team,
            'away_team': away_team,
            'score_home': score_home,
            'score_away': score_away,
            'moduli': moduli,
            'scorers': scorers,
            'own_goals': own_goals,
            'assisters': assisters,
            'yellow_cards': yellow_cards,
            'red_cards': red_cards,
            'goalkeepers': goalkeepers,
            'home_starters': home_starters,
            'away_starters': away_starters,
            'home_bench': home_bench,
            'away_bench': away_bench,
            'team_stats': {
                'home': t_home,
                'away': t_away
            },
            'physical_leaders': {
                'top_km': sorted_km,
                'top_speed': sorted_speed
            },
            'ai_analysis': ai_data
        }

        g_str = str(giornata)
        if g_str not in hub_by_round:
            hub_by_round[g_str] = {
                'giornata': giornata,
                'matches_count': 0,
                'matches': []
            }
        hub_by_round[g_str]['matches'].append(match_record)
        hub_by_round[g_str]['matches_count'] = len(hub_by_round[g_str]['matches'])

    # Salva il file JSON aggregato
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(hub_by_round, f, ensure_ascii=False, indent=2)

    print(f"✓ Generato {OUT_JSON} con {len(hub_by_round)} giornate archiviate:")
    for g_k, g_v in sorted(hub_by_round.items(), key=lambda x: int(x[0])):
        print(f"  • Giornata {g_k}: {g_v['matches_count']} partite con referti completi.")

    return hub_by_round

if __name__ == '__main__':
    build_match_reports_hub()
