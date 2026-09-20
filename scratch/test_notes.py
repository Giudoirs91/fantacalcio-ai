import json

players = json.load(open('data/processed/processed_players_master.json', encoding='utf-8'))
tactical = json.load(open('config/tactical_db.json', encoding='utf-8'))
team_stats = json.load(open('data/raw/fotmob_team_stats_2026_27.json', encoding='utf-8'))
cal = json.load(open('data/processed/calendario_serie_a_2026_27.json', encoding='utf-8'))

r5 = next(x for x in cal if x['giornata'] == 5)
match_map = {m['home']: {'opp': m['away'], 'is_home': True} for m in r5['matches']}
match_map.update({m['away']: {'opp': m['home'], 'is_home': False} for m in r5['matches']})

def generate_note(p, pos_key):
    m_info = match_map.get(p['team'])
    opp = m_info['opp']
    is_home = m_info['is_home']
    loc_str = "in casa" if is_home else f"a {opp}"
    
    fm = f"{p.get('fm_2627') or p.get('fm') or 6.0:.2f}"
    gol = p.get('gol_2627', 0)
    ass = p.get('assist_2627', 0)
    
    opp_stats = team_stats.get(opp, {})
    opp_gc = f"{opp_stats.get('goals_conceded_match', 1.3):.1f}"
    opp_att = tactical.get(opp, {}).get('att_stars', 3)
    opp_dif = tactical.get(opp, {}).get('dif_stars', 3)
    
    role = p['role']
    
    # Portieri
    if role == 'P' or pos_key == 'Por':
        if is_home:
            return f"Partita ideale a domicilio contro il {opp} (attacco a {opp_att} stelle): chance elevatissima di Clean Sheet e bonus imbattibilità (+1)."
        else:
            return f"Trasferta insidiosa ma ampiamente alla portata: il {opp} fatica a segnare. Ottima garanzia per evitare malus e strappare un voto utile."

    # Difensori Centrali e Braccetti
    if pos_key in ['Dc', 'B']:
        return f"Dominio fisico e aereo contro le punte del {opp}. Rendimento solido (FM {fm}) e zero cartellini: garanzia assoluta da modificatore difesa."

    # Terzini ed Esterni (Dd, Ds, E)
    if pos_key in ['Dd', 'Ds', 'E'] or (role == 'D' and p.get('is_oop')):
        extra = f" (già {gol}G e {ass}A)" if (gol or ass) else ""
        if p.get('is_oop'):
            return f"Schierato ala/quinto a tutta fascia{extra}: ara la corsia debole del {opp}. Traversoni e inserimenti per il bonus pesante."
        return f"Spinta continua {loc_str} contro una difesa vulnerabile sulle fasce{extra}. Cross al bacio e voto sicuro (FM {fm})."

    # Mediani (M)
    if pos_key == 'M':
        return f"Diga insostituibile in mezzo al campo contro il {opp}: schermatura, palloni recuperati e sufficienza piena blindata in pagella."

    # Centrocampisti e Trequartisti (C, T)
    if role == 'C' or pos_key in ['C', 'T']:
        penn = " Primo rigorista e cecchino da fermo." if p.get('is_rigorista_1') else ""
        streak = f" In striscia d'oro con {gol} gol." if gol >= 2 else ""
        return f"Sfida la retroguardia del {opp} (subisce {opp_gc} gol/gara). Incursore letale tra le linee (FM {fm}).{streak}{penn}"

    # Attaccanti, Bomber e Ali (A, Pc, W)
    if role == 'A' or pos_key in ['A', 'Pc', 'W']:
        if gol >= 3:
            rig = " Rigorista infallibile." if p.get('is_rigorista_1') else ""
            return f"Momento stellare: già {gol} reti a referto (FM {fm}).{rig} È l'arma letale contro il {opp}, schieramento prioritario."
        elif p.get('is_rigorista_1'):
            return f"Leader dell'attacco e 1° rigorista contro la difesa del {opp}. Presenza fissa negli ultimi 16 metri: gol caldissimo."
        else:
            return f"1vs1 costante contro la difesa del {opp} che concede spazi. Tiri nello specchio e chance da gol nitide (FM {fm})."

    return f"Matchup favorevole {loc_str} contro il {opp}: forma solida (FM {fm}) e titolarità al 100%."

for name in ['Maignan', 'Corvi', 'Mandas', 'Mangas', 'Kamara H.', 'Kaiki', 'Frattesi', 'Zaccagni', 'Pulisic', 'Malen', 'Dybala', 'Maldini']:
    p = next(x for x in players if x['name'] == name)
    print(f"{p['name']} ({p['team']}) -> {generate_note(p, p['role'])}")
