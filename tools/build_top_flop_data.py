import os
import sys
import re
import json
import glob
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOTI_DIR = os.path.join(ROOT_DIR, "data", "raw", "voti 26-27")
MATCHES_JSON = os.path.join(ROOT_DIR, "data", "raw", "match_reports_matches_g1_g2.json")
PLAYERS_MASTER = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
ROOT_PLAYERS_MASTER = os.path.join(ROOT_DIR, "processed_players_master.json")
OUT_JSON = os.path.join(ROOT_DIR, "data", "processed", "top_flop_rounds.json")

CALENDARIO_JSON = os.path.join(ROOT_DIR, "data", "processed", "calendario_serie_a_2026_27.json")
CONFIG_CAL_JSON = os.path.join(ROOT_DIR, "config", "calendario_serie_a_2026_27.json")

def load_team_matches():
    team_matches = {}

    # 1. Carica prima il calendario completo ufficiale 38 giornate
    cal_file = CALENDARIO_JSON if os.path.exists(CALENDARIO_JSON) else (CONFIG_CAL_JSON if os.path.exists(CONFIG_CAL_JSON) else None)
    if cal_file and os.path.exists(cal_file):
        try:
            with open(cal_file, 'r', encoding='utf-8') as f:
                cal_data = json.load(f)
            for round_obj in cal_data:
                g = round_obj.get('giornata')
                dt = round_obj.get('date', '')
                for m in round_obj.get('matches', []):
                    h = m.get('home', '').upper().strip()
                    a = m.get('away', '').upper().strip()
                    h_cap = m.get('home', '').strip()
                    a_cap = m.get('away', '').strip()
                    if g and h and a:
                        team_matches[(g, h)] = {
                            'opponent': a_cap,
                            'is_home': True,
                            'score_str': f"{h_cap} vs {a_cap}",
                            'team_score': None,
                            'opp_score': None,
                            'date': dt
                        }
                        team_matches[(g, a)] = {
                            'opponent': h_cap,
                            'is_home': False,
                            'score_str': f"{a_cap} @ {h_cap}",
                            'team_score': None,
                            'opp_score': None,
                            'date': dt
                        }
        except Exception as e:
            print(f"Errore caricamento calendario ufficiale: {e}")

    # 2. Sovrascrivi con i match reports reali se disponibili (con punteggi)
    if os.path.exists(MATCHES_JSON):
        try:
            with open(MATCHES_JSON, 'r', encoding='utf-8') as f:
                matches_info = json.load(f)
            for m in matches_info:
                g = m.get('giornata')
                h = m.get('home_team', '').upper().strip()
                a = m.get('away_team', '').upper().strip()
                title = m.get('match_title', '').strip()
                sh = m.get('score_home')
                sa = m.get('score_away')
                if g and h and a:
                    team_matches[(g, h)] = {
                        'opponent': a.capitalize(),
                        'is_home': True,
                        'score_str': title or f"{h.capitalize()} vs {a.capitalize()}",
                        'team_score': sh,
                        'opp_score': sa
                    }
                    team_matches[(g, a)] = {
                        'opponent': h.capitalize(),
                        'is_home': False,
                        'score_str': title or f"{a.capitalize()} @ {h.capitalize()}",
                        'team_score': sa,
                        'opp_score': sh
                    }
        except Exception as e:
            print(f"Errore caricamento match reports: {e}")

    return team_matches

def generate_commentary(name, role, team, match_info, voto, fv, gf, gs, ass, amm, esp, au, rp, rs, is_top=True):
    opp = match_info.get('opponent', 'avversario') if match_info else 'avversario'
    score = match_info.get('score_str', '') if match_info else ''
    where = f"nel {score}" if score else f"contro il {opp}"

    # Specific custom gems if available
    if name == "Coulibaly L." and gf == 2:
        return f"Prestazione dominante a centrocampo condita da una clamorosa doppietta (+6) nel 3-2 contro il Monza."
    if name == "Mastantuono" and gf == 3:
        return f"Tripletta show e prestazione da fuoriclasse assoluto (+9) che trascina la Fiorentina nel rocambolesco 4-2 di Venezia."
    if name == "Moreira" and gf == 2:
        return f"Doppietta d'autore (+6) e lampi di pura classe a San Siro nel vibrante 2-2 contro la Lazio."
    if name == "Colombo" and rs > 0:
        return f"Pomeriggio da incubo: rigore fallito dal dischetto (-3) e prestazione molto opaca nella sconfitta 3-2 a Lecce."
    if name == "Zhegrova" and gf == 2:
        return f"Doppietta da trascinatore puro (+6) e folate offensive incontenibili nel pirotecnico 3-2 contro il Sassuolo."
    if name == "Malen" and gf >= 2:
        return f"Centravanti implacabile sotto porta: doppietta letale (+6) e costante punto di riferimento offensivo {where}."
    if name == "Diao" and gf >= 2:
        return f"Esplosione a sorpresa: devastante doppietta (+6) da subentrato di lusso {where}."
    if name == "Raimondo" and gf >= 2:
        return f"Fiuto del gol da rapace d'area: implacabile doppietta (+6) decisiva {where}."

    if is_top:
        if gf >= 3:
            return f"Tripletta da sogno e prestazione monumentale (+9) da dominatore assoluto {where}."
        elif gf == 2:
            return f"Prestazione dominante condita da una clamorosa doppietta (+6) {where}."
        elif gf == 1 and ass >= 1:
            return f"Leader tecnico totale: timbra il gol (+3) e sforna un assist illuminante (+1) {where}."
        elif gf == 1:
            return f"Letale e decisivo: trova il gol vittoria (+3) con un inserimento perfetto {where}."
        elif ass >= 2:
            return f"Visione di gioco stellare: regala 2 assist al bacio (+2) ai compagni {where}."
        elif ass == 1:
            return f"Rifinitore di altissimo livello: assist decisivo (+1) e manovra fluida {where}."
        elif rp >= 1:
            return f"Eroe assoluto di giornata: rigore parato da campione (+3) che salva il risultato {where}."
        elif voto >= 7.5:
            return f"Autentica muraglia difensiva e voto stellare ({voto}) senza concedere un millimetro {where}."
        else:
            return f"Gara di altissima intensità e sostanza con voto ampiamente positivo ({voto}) {where}."
    else:
        if rs >= 1:
            return f"Giornata da incubo: rigore fallito dagli undici metri (-3) e grave insufficienza {where}."
        elif au >= 1:
            return f"Pomeriggio sfortunatissimo: clamoroso autogol (-2) ed errore grave in fase difensiva {where}."
        elif esp >= 1:
            return f"Nervi tesi ed espulsione diretta (-1) che compromette la gara e danneggia i compagni {where}."
        elif role == 'P' and gs >= 4:
            return f"Tracollo difensivo: ben {gs} reti al passivo (-{gs}) e difesa completamente travolta {where}."
        elif role == 'P' and gs >= 3:
            return f"Pomeriggio nero tra i pali: {gs} gol subiti (-{gs}) e qualche incertezza nelle uscite {where}."
        elif role == 'P' and gs >= 2:
            return f"Due reti incassate (-2) e disattenzioni fatali che costano punti pesanti {where}."
        elif voto <= 4.5:
            if amm > 0:
                return f"Bocciatura senza appello: prestazione disastrosa (voto {voto}) condita da ammonizione (-0.5) {where}."
            return f"Grave insufficienza sul campo (voto {voto}): mai in partita e costantemente battuto {where}."
        elif voto <= 5.0:
            if amm > 0:
                return f"In affanno continuo contro gli attaccanti avversari, rimedia cartellino giallo (-0.5) e un pessimo voto {where}."
            return f"Prestazione molto al di sotto degli standard abituali con voto insufficiente ({voto}) {where}."
        else:
            return f"Giornata opaca e passivo pesante che pesa sul fantavoto complessivo ({fv}) {where}."

def run_pipeline():
    files = sorted(glob.glob(os.path.join(VOTI_DIR, "Voti_Fantacalcio_Stagione_2026_27_Giornata_*.xlsx")))
    if not files:
        print("Nessun file voti trovato.")
        return

    team_matches = load_team_matches()

    # Carica master listone
    master_players = []
    if os.path.exists(PLAYERS_MASTER):
        with open(PLAYERS_MASTER, 'r', encoding='utf-8') as f:
            master_players = json.load(f)

    p_by_id = {p['id']: p for p in master_players}
    # Reset o inizializza voti_dettaglio_2627 per tutti i calciatori
    for p in master_players:
        p['voti_dettaglio_2627'] = []

    rounds_data = {}

    for filepath in files:
        m = re.search(r'Giornata_(\d+)', filepath)
        g_num = int(m.group(1)) if m else 1

        try:
            xl = pd.ExcelFile(filepath)
            sheet = 'Fantacalcio' if 'Fantacalcio' in xl.sheet_names else xl.sheet_names[0]
            df = pd.read_excel(xl, sheet_name=sheet, skiprows=5)
            df = df[pd.to_numeric(df['Cod.'], errors='coerce').notna()].copy()

            df['Voto_clean'] = pd.to_numeric(df['Voto'].astype(str).str.replace('*', '').str.replace(',', '.'), errors='coerce')

            for col in ['Gf', 'Gs', 'Au', 'Amm', 'Esp', 'Ass', 'Rp', 'Rs', 'Rf']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                else:
                    df[col] = 0

            gf = df['Gf']
            gs = df['Gs']
            ass = df['Ass']
            amm = df['Amm']
            esp = df['Esp']
            aut = df['Au']
            rp = df['Rp']
            rs = df['Rs']

            df['FV_calc'] = df['Voto_clean'] + (gf * 3.0) - (gs * 1.0) + (rp * 3.0) - (rs * 3.0) - (aut * 2.0) - (amm * 0.5) - (esp * 1.0) + (ass * 1.0)
            df['FV_calc'] = df['FV_calc'].round(2)

            # Salva i voti per tutti i calciatori nel master listone
            for _, r in df.iterrows():
                cid = int(r['Cod.'])
                if cid in p_by_id:
                    pl = p_by_id[cid]
                    tm_upper = pl['team'].upper().strip()
                    m_info = team_matches.get((g_num, tm_upper), {})

                    has_voto = pd.notna(r['Voto_clean'])
                    voto_val = float(r['Voto_clean']) if has_voto else None
                    fv_val = float(r['FV_calc']) if has_voto else None

                    # Crea stringa bonus/malus sintetica
                    bm_parts = []
                    if r['Gf'] > 0: bm_parts.append(f"+{int(r['Gf']*3)} ({int(r['Gf'])}G)")
                    if r['Ass'] > 0: bm_parts.append(f"+{int(r['Ass'])} ({int(r['Ass'])}A)")
                    if r['Rp'] > 0: bm_parts.append(f"+{int(r['Rp']*3)} (Rig.Par)")
                    if r['Gs'] > 0: bm_parts.append(f"-{int(r['Gs'])} ({int(r['Gs'])}GS)")
                    if r['Rs'] > 0: bm_parts.append(f"-3 (Rig.Sbagliato)")
                    if r['Au'] > 0: bm_parts.append(f"-{int(r['Au']*2)} (Autogol)")
                    if r['Amm'] > 0: bm_parts.append(f"-0.5 (Amm)")
                    if r['Esp'] > 0: bm_parts.append(f"-1 (Esp)")
                    bm_str = ", ".join(bm_parts) if bm_parts else ("Nessun bonus" if has_voto else "-")

                    opp_name = m_info.get('opponent', '-')
                    match_str = m_info.get('score_str', f"vs {opp_name}")

                    pl['voti_dettaglio_2627'].append({
                        'giornata': g_num,
                        'match': match_str,
                        'opponent': opp_name,
                        'is_home': m_info.get('is_home', True),
                        'voto': voto_val,
                        'fantavoto': fv_val,
                        'gf': int(r['Gf']),
                        'gs': int(r['Gs']),
                        'ass': int(r['Ass']),
                        'amm': int(r['Amm']),
                        'esp': int(r['Esp']),
                        'au': int(r['Au']),
                        'rp': int(r['Rp']),
                        'rs': int(r['Rs']),
                        'bonus_malus_str': bm_str
                    })

            # Filtra chi ha voto per generare TOP & FLOP
            voted = df[df['Voto_clean'].notna()].copy()

            # TOP 15
            top_df = voted.sort_values(by=['FV_calc', 'Voto_clean'], ascending=[False, False]).head(15)
            top_list = []
            for _, r in top_df.iterrows():
                cid = int(r['Cod.'])
                pl = p_by_id.get(cid, {})
                tm_name = pl.get('team', 'Serie A')
                tm_upper = tm_name.upper().strip()
                m_info = team_matches.get((g_num, tm_upper), {})

                motivo_tags = []
                if r['Gf'] > 0: motivo_tags.append(f"{int(r['Gf'])} Gol (+{int(r['Gf']*3)})")
                if r['Ass'] > 0: motivo_tags.append(f"{int(r['Ass'])} Assist (+{int(r['Ass'])})")
                if r['Rp'] > 0: motivo_tags.append(f"{int(r['Rp'])} Rigore Parato (+{int(r['Rp']*3)})")
                if not motivo_tags: motivo_tags.append(f"Voto eccellente ({r['Voto_clean']})")

                comm = generate_commentary(
                    name=str(r['Nome']).strip(),
                    role=str(r['Ruolo']).strip(),
                    team=tm_name,
                    match_info=m_info,
                    voto=float(r['Voto_clean']),
                    fv=float(r['FV_calc']),
                    gf=int(r['Gf']),
                    gs=int(r['Gs']),
                    ass=int(r['Ass']),
                    amm=int(r['Amm']),
                    esp=int(r['Esp']),
                    au=int(r['Au']),
                    rp=int(r['Rp']),
                    rs=int(r['Rs']),
                    is_top=True
                )

                top_list.append({
                    'cod': cid,
                    'name': str(r['Nome']).strip(),
                    'role': str(r['Ruolo']).strip(),
                    'team': tm_name,
                    'opponent': m_info.get('opponent', '-'),
                    'match': m_info.get('score_str', ''),
                    'voto': float(r['Voto_clean']),
                    'fantavoto': float(r['FV_calc']),
                    'gf': int(r['Gf']),
                    'ass': int(r['Ass']),
                    'motivo': ", ".join(motivo_tags),
                    'commento': comm
                })

            # FLOP 15
            bot_df = voted.sort_values(by=['FV_calc', 'Voto_clean'], ascending=[True, True]).head(15)
            flop_list = []
            for _, r in bot_df.iterrows():
                cid = int(r['Cod.'])
                pl = p_by_id.get(cid, {})
                tm_name = pl.get('team', 'Serie A')
                tm_upper = tm_name.upper().strip()
                m_info = team_matches.get((g_num, tm_upper), {})

                motivo_tags = []
                if r['Rs'] > 0: motivo_tags.append("Rigore Fallito (-3)")
                if r['Gs'] > 0: motivo_tags.append(f"{int(r['Gs'])} Gol Subiti (-{int(r['Gs'])})")
                if r['Esp'] > 0: motivo_tags.append("Espulsione (-1)")
                if r['Au'] > 0: motivo_tags.append(f"Autogol (-{int(r['Au']*2)})")
                if r['Amm'] > 0: motivo_tags.append("Ammonizione (-0.5)")
                if not motivo_tags: motivo_tags.append(f"Insufficienza ({r['Voto_clean']})")

                comm = generate_commentary(
                    name=str(r['Nome']).strip(),
                    role=str(r['Ruolo']).strip(),
                    team=tm_name,
                    match_info=m_info,
                    voto=float(r['Voto_clean']),
                    fv=float(r['FV_calc']),
                    gf=int(r['Gf']),
                    gs=int(r['Gs']),
                    ass=int(r['Ass']),
                    amm=int(r['Amm']),
                    esp=int(r['Esp']),
                    au=int(r['Au']),
                    rp=int(r['Rp']),
                    rs=int(r['Rs']),
                    is_top=False
                )

                flop_list.append({
                    'cod': cid,
                    'name': str(r['Nome']).strip(),
                    'role': str(r['Ruolo']).strip(),
                    'team': tm_name,
                    'opponent': m_info.get('opponent', '-'),
                    'match': m_info.get('score_str', ''),
                    'voto': float(r['Voto_clean']),
                    'fantavoto': float(r['FV_calc']),
                    'gs': int(r['Gs']),
                    'amm': int(r['Amm']),
                    'esp': int(r['Esp']),
                    'motivo': ", ".join(motivo_tags),
                    'commento': comm
                })

            rounds_data[g_num] = {
                'round': g_num,
                'total_players_voted': len(voted),
                'top': top_list,
                'flop': flop_list
            }

        except Exception as e:
            print(f"Errore round {g_num}: {e}")

    # Ricalcola statistiche cumulative, medie 26/27 e trend per tutti i giocatori del master listone
    for p in master_players:
        valid_voti = [v['voto'] for v in p.get('voti_dettaglio_2627', []) if v['voto'] is not None]
        valid_fv = [v['fantavoto'] for v in p.get('voti_dettaglio_2627', []) if v['fantavoto'] is not None]

        tot_bonus = 0.0
        tot_malus = 0.0
        tot_gf = 0
        tot_gs = 0
        tot_ass = 0
        tot_amm = 0
        tot_esp = 0
        tot_rs = 0
        for v in p.get('voti_dettaglio_2627', []):
            if v.get('voto') is not None:
                tot_gf += v.get('gf', 0)
                tot_gs += v.get('gs', 0)
                tot_ass += v.get('ass', 0)
                tot_amm += v.get('amm', 0)
                tot_esp += v.get('esp', 0)
                tot_rs += v.get('rs', 0)
                b = v.get('gf', 0) * 3.0 + v.get('ass', 0) * 1.0 + v.get('rp', 0) * 3.0
                m = v.get('gs', 0) * 1.0 + v.get('amm', 0) * 0.5 + v.get('esp', 0) * 1.0 + v.get('au', 0) * 2.0 + v.get('rs', 0) * 3.0
                tot_bonus += b
                tot_malus += m
        p['tot_bonus_2627'] = round(tot_bonus, 2)
        p['tot_malus_2627'] = round(tot_malus, 2)
        p['gol_2627'] = tot_gf
        p['assist_2627'] = tot_ass
        p['gol_subiti_2627'] = tot_gs
        p['amm_2627'] = tot_amm
        p['esp_2627'] = tot_esp
        p['rigori_sbagliati_2627'] = tot_rs

        p['presenze_2627'] = len(valid_voti)
        p['starts_2627'] = len(valid_voti)
        if valid_voti:
            p['mv_2627'] = round(float(np.mean(valid_voti)), 2)
            p['fm_2627'] = round(float(np.mean(valid_fv)), 2)
            # Calcolo intelligente trend e momentum
            recent_voti = valid_voti[-3:] if len(valid_voti) >= 3 else valid_voti
            recent_fv = valid_fv[-3:] if len(valid_fv) >= 3 else valid_fv
            recent_mean_fv = float(np.mean(recent_fv)) if recent_fv else p['fm_2627']
            recent_goals = sum(v.get('gf', 0) for v in p.get('voti_dettaglio_2627', [])[-3:])
            recent_assists = sum(v.get('ass', 0) for v in p.get('voti_dettaglio_2627', [])[-3:])

            # Regole di classificazione trend intelligenti
            if recent_mean_fv >= 8.0 or recent_goals >= 2 or (p['fm_2627'] >= 7.5 and valid_fv[-1] >= 7.0):
                p['trend_2627'] = '🔥 On Fire'
                p['trend_class'] = 'fire'
            elif (recent_mean_fv - p['fm_2627'] >= 0.4) or (len(valid_fv) >= 2 and valid_fv[-1] > valid_fv[-2] + 1.0):
                p['trend_2627'] = '📈 In Crescita'
                p['trend_class'] = 'up'
            elif (p['fm_2627'] - recent_mean_fv >= 0.75 and recent_goals == 0 and recent_assists == 0 and recent_mean_fv < 6.0):
                p['trend_2627'] = '❄️ In Flessione'
                p['trend_class'] = 'down'
            elif p['role'] in ['A', 'C'] and recent_goals == 0 and recent_assists == 0 and len(valid_voti) >= 3 and recent_mean_fv <= 6.2:
                p['trend_2627'] = '⏳ A Secco'
                p['trend_class'] = 'warning'
            else:
                p['trend_2627'] = '⚖️ Costante'
                p['trend_class'] = 'neutral'

    # Salva top_flop_rounds.json
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(rounds_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Generato {OUT_JSON} con {len(rounds_data)} giornate.")

    # Salva master players arricchiti
    with open(PLAYERS_MASTER, 'w', encoding='utf-8') as f:
        json.dump(master_players, f, ensure_ascii=False, indent=2)
    print(f"✓ Aggiornato {PLAYERS_MASTER} con voti_dettaglio_2627 per {len(master_players)} calciatori.")

    if os.path.exists(ROOT_PLAYERS_MASTER):
        with open(ROOT_PLAYERS_MASTER, 'w', encoding='utf-8') as f:
            json.dump(master_players, f, ensure_ascii=False, indent=2)
        print(f"✓ Aggiornato {ROOT_PLAYERS_MASTER}.")

if __name__ == '__main__':
    run_pipeline()
