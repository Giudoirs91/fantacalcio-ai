import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MASTER_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
ROOT_MASTER_PATH = os.path.join(ROOT_DIR, "processed_players_master.json")
INJ_PATH = os.path.join(ROOT_DIR, "config", "injuries_history.json")
TACTICAL_PATH = os.path.join(ROOT_DIR, "config", "tactical_db.json")

# 1. Aggiorna config/injuries_history.json
with open(INJ_PATH, "r", encoding="utf-8") as f:
    inj_db = json.load(f)

neto_cronistoria = [
    {
        "stagione": "25/26",
        "motivo": "Problemi alla coscia",
        "diagnosi": "Problemi alla coscia",
        "data_inizio": "15/09/2025",
        "data_fine": "20/01/2026",
        "giorni_stop": 128,
        "giorni": 128,
        "partite_perse": 19,
        "tipo": "muscolare",
        "in_corso": False
    },
    {
        "stagione": "23/24",
        "motivo": "Infortunio alla caviglia",
        "diagnosi": "Infortunio alla caviglia",
        "data_inizio": "27/10/2023",
        "data_fine": "24/11/2023",
        "giorni_stop": 29,
        "giorni": 29,
        "partite_perse": 3,
        "tipo": "articolare",
        "in_corso": False
    },
    {
        "stagione": "22/23",
        "motivo": "Ritardo di condizione",
        "diagnosi": "Ritardo di condizione",
        "data_inizio": "19/12/2022",
        "data_fine": "13/01/2023",
        "giorni_stop": 26,
        "giorni": 26,
        "partite_perse": 5,
        "tipo": "medico",
        "in_corso": False
    },
    {
        "stagione": "22/23",
        "motivo": "Infortunio alla coscia",
        "diagnosi": "Infortunio alla coscia",
        "data_inizio": "24/10/2022",
        "data_fine": "18/12/2022",
        "giorni_stop": 56,
        "giorni": 56,
        "partite_perse": 4,
        "tipo": "muscolare",
        "in_corso": False
    },
    {
        "stagione": "21/22",
        "motivo": "Raffreddore",
        "diagnosi": "Raffreddore",
        "data_inizio": "05/11/2021",
        "data_fine": "08/11/2021",
        "giorni_stop": 4,
        "giorni": 4,
        "partite_perse": 1,
        "tipo": "medico",
        "in_corso": False
    },
    {
        "stagione": "20/21",
        "motivo": "Caviglia slogata",
        "diagnosi": "Caviglia slogata",
        "data_inizio": "22/03/2021",
        "data_fine": "24/04/2021",
        "giorni_stop": 34,
        "giorni": 34,
        "partite_perse": 4,
        "tipo": "articolare",
        "in_corso": False
    },
    {
        "stagione": "19/20",
        "motivo": "Caviglia slogata",
        "diagnosi": "Caviglia slogata",
        "data_inizio": "23/01/2020",
        "data_fine": "14/02/2020",
        "giorni_stop": 23,
        "giorni": 23,
        "partite_perse": 5,
        "tipo": "articolare",
        "in_corso": False
    },
    {
        "stagione": "19/20",
        "motivo": "Infortunio alla mano",
        "diagnosi": "Infortunio alla mano",
        "data_inizio": "11/08/2019",
        "data_fine": "17/09/2019",
        "giorni_stop": 38,
        "giorni": 38,
        "partite_perse": 4,
        "tipo": "traumatico",
        "in_corso": False
    },
    {
        "stagione": "18/19",
        "motivo": "Infortunio alla schiena",
        "diagnosi": "Infortunio alla schiena",
        "data_inizio": "15/03/2019",
        "data_fine": "29/03/2019",
        "giorni_stop": 15,
        "giorni": 15,
        "partite_perse": 1,
        "tipo": "articolare",
        "in_corso": False
    },
    {
        "stagione": "15/16",
        "motivo": "Problema fisico",
        "diagnosi": "Problema fisico",
        "data_inizio": "16/04/2016",
        "data_fine": "02/05/2016",
        "giorni_stop": 17,
        "giorni": 17,
        "partite_perse": 4,
        "tipo": "medico",
        "in_corso": False
    }
]

if "Juventus" not in inj_db:
    inj_db["Juventus"] = {}

inj_db["Juventus"]["Neto"] = {
    "id": 283,
    "tm_id": "111819",
    "tm_name": "Norberto Murara Neto",
    "name": "Neto",
    "team": "Juventus",
    "ruolo": "P",
    "partite_saltate_totali": 50,
    "giorni_stop_totali": 350,
    "disponibilita_pct": 82.5,
    "recidive_muscolari": 2,
    "indice_fragilita_score": 55.0,
    "livello_fragilita": "ATTENZIONE",
    "fragility_label": "🟡 Attenzione (Soggetto a Stop)",
    "fragility_badge": "attenzione",
    "consiglio_medico_ai": "Esperto portiere brasiliano con storico di stop muscolari e articolari. Attualmente integro e disponibile come 2° portiere della Juventus dopo il grave infortunio di Grabara.",
    "infortunio_attivo": False,
    "cronistoria_infortuni": neto_cronistoria
}

with open(INJ_PATH, "w", encoding="utf-8") as f:
    json.dump(inj_db, f, indent=2, ensure_ascii=False)
print("✓ Infortuni aggiornati per Neto in config/injuries_history.json")

# 2. Aggiorna config/tactical_db.json
with open(TACTICAL_PATH, "r", encoding="utf-8") as f:
    tac_db = json.load(f)

if "Juventus" in tac_db and "lineup" in tac_db["Juventus"]:
    for pos in tac_db["Juventus"]["lineup"]:
        if pos.get("pos") == "POR":
            pos["sub_name"] = "Neto"
            print("✓ Portiere di riserva Juventus aggiornato a Neto in config/tactical_db.json")

with open(TACTICAL_PATH, "w", encoding="utf-8") as f:
    json.dump(tac_db, f, indent=2, ensure_ascii=False)

# 3. Aggiorna processed_players_master.json (data/processed e root)
with open(MASTER_PATH, "r", encoding="utf-8") as f:
    players = json.load(f)

vicario = next((p for p in players if p.get("name") == "Vicario"), None)
if not vicario:
    raise ValueError("Vicario non trovato")

# Aggiorna Vicario: coppia con Neto
vicario["coppia_nome"] = "Neto"
vicario["coppia_id"] = 283
vicario["coppia_ruolo"] = "P"
vicario["coppia_tipo"] = "RISERVA"
vicario["coppia_dettaglio"] = "2° Portiere (Neto)"

# Rimuovi eventuale vecchio Neto se presente
players = [p for p in players if p.get("id") != 283 and not (p.get("name") == "Neto" and p.get("team") == "Juventus")]

neto_dict = {
    "id": 283,
    "name": "Neto",
    "role": "P",
    "mantra": "Por",
    "team": "Juventus",
    "fvm": 1.0,
    "qta": 1.0,
    "diff_q": 0.0,
    "presenze": 0,
    "mv": 0.0,
    "fm": 0.0,
    "gf": 0,
    "rf": 0,
    "ass": 0,
    "gs": 0,
    "amm": 0,
    "esp": 0,
    "diff_bm": 0.0,
    "titolarita": 0,
    "titolarita_ultime3": 0,
    "titolarita_mid": 0,
    "titolarita_storico": 25,
    "titolarita_dettaglio": "0/5 Presenze (Tesserato come Vice Vicario)",
    "has_data_2627": False,
    "presenze_2627": 0,
    "starts_2627": 0,
    "titolarita_desc_2627": "0/5 Presenze (2° Portiere)",
    "minuti_2627": 0,
    "gol_2627": 0,
    "assist_2627": 0,
    "tiri_2627": 0,
    "tiri_porta_2627": 0,
    "key_passes_2627": 0,
    "recuperi_2627": 0,
    "falli_subiti_2627": 0,
    "amm_2627": 0,
    "esp_2627": 0,
    "clean_sheets_2627": 0,
    "parate_2627": 0,
    "gol_subiti_2627": 0,
    "mv_2627": None,
    "fm_2627": None,
    "tot_bonus_2627": 0.0,
    "tot_malus_2627": 0.0,
    "partite_voto_2627": 0,
    "voti_dettaglio_2627": [],
    "xg_2627": None,
    "xg90_2627": None,
    "xa_2627": None,
    "xa90_2627": None,
    "xgot_2627": None,
    "big_chances_created_2627": None,
    "chances_created_2627": None,
    "rating_live_2627": None,
    "total_scoring_att_2627": None,
    "ontarget_scoring_att_2627": None,
    "won_contest_2627": None,
    "big_chance_missed_2627": None,
    "poss_won_att_3rd_2627": None,
    "goals_conceded_stat_2627": None,
    "save_pct_2627": None,
    "clean_sheet_stat_2627": None,
    "total_tackle_2627": None,
    "defensive_contributions_2627": None,
    "ball_recovery_stat_2627": None,
    "goals_prevented_2627": None,
    "minuti_stat_2627": 0,
    "fouls_2627": None,
    "has_data_2526": True,
    "league_2526": "Premier League (Bournemouth/Arsenal)",
    "xg_2526": 0.0,
    "xg90_2526": 0.0,
    "xgot_2526": 0.0,
    "xa_2526": 0.0,
    "xa90_2526": 0.0,
    "xg_xa90_2526": 0.0,
    "rating_2526": 6.85,
    "mins_2526": 2880,
    "tkl_int90_2526": 0.0,
    "shots90_2526": 0.0,
    "big_chances_created_2526": 0,
    "key_passes_2526": 0,
    "goals_prevented_2526": 2.1,
    "clean_sheets_2526": 7,
    "save_pct_2526": 72.4,
    "xg90": 0.0,
    "xa90": 0.0,
    "sh90": 0.0,
    "kp90": 0,
    "tkl_int90": 0.0,
    "fantascore": 58.0,
    "ovr": 68,
    "prezzo_cons": 1,
    "max_bid": 2,
    "fascia": "5ª Fascia (Low Cost / Slot 1 Credito)",
    "slot_fascia": "2° Portiere",
    "slot_num": 2,
    "integrita": "🟡 Attenzione (Soggetto a Stop) (82.5% disp.)",
    "integrita_badge": "attenzione",
    "fragilita_val": "🟡 Attenzione (Soggetto a Stop)",
    "fragilita_badge": "attenzione",
    "fragilita_score": 55.0,
    "fragility_score": 55.0,
    "fragilita_dettaglio": "50 gare saltate • Disp. 82.5%",
    "fragility_tier": "ATTENZIONE",
    "partite_saltate_totali": 50,
    "giorni_stop_totali": 350,
    "disponibilita_pct": 82.5,
    "recidive_muscolari": 2,
    "consiglio_medico_ai": "Esperto portiere brasiliano con storico di stop muscolari e articolari. Attualmente integro e disponibile come 2° portiere della Juventus dopo il grave infortunio di Grabara.",
    "cronistoria_infortuni": neto_cronistoria,
    "is_injured": False,
    "giornate_perse": 0,
    "is_chronic_fragile": False,
    "infortunio_status": "🟢 Disponibile",
    "infortunio_motivo": "",
    "infortunio_rientro": "",
    "infortunio_severity": "",
    "infortunio_tipo_stop": "",
    "rigorista_val": "-",
    "piazzati_val": "-",
    "oop_val": "-",
    "is_rigorista_1": False,
    "is_rigorista_2": False,
    "is_rigorista_3": False,
    "is_punizioni": False,
    "is_corner": False,
    "is_oop": False,
    "fpp_fpn": "NONE",
    "pos_label": "",
    "oop_type": "",
    "oop_desc": "",
    "oop_tier": "",
    "is_in_11": False,
    "is_in_ballottaggio": False,
    "pitch_pos": "",
    "is_top": False,
    "is_sleeper": False,
    "is_flop": False,
    "team_context": vicario.get("team_context", {}),
    "xfm": None,
    "delta_xfm": None,
    "floor": 5.4,
    "ceiling": 7.0,
    "spread": 1.6,
    "volatility_label": "BASSA",
    "tactical_profile": "🛡️ Floor Sicuro (Roccia Costante)",
    "tactical_advice": "Secondo portiere affidabile ed esperto: acquisto obbligato a 1 credito come copertura per chi possiede Vicario.",
    "sub_vote_prob": 5,
    "sub_impact_score": 10,
    "subs_on_count": 0,
    "super_sub_badge": "🛡️ COPERTURA PORTIERE",
    "sub_verdict": "Secondo portiere designato: subentra solo in caso di stop di Vicario.",
    "matchup_vulnerability": vicario.get("matchup_vulnerability", {}),
    "ai_advice": "🛡️ DA PRENDERE IN COPPIA CON VICARIO",
    "ai_advice_type": "coverage",
    "consiglio": "🛡️ DA PRENDERE IN COPPIA CON VICARIO",
    "coppia_nome": "Vicario",
    "coppia_id": 4964,
    "coppia_ruolo": "P",
    "coppia_tipo": "TITOLARE",
    "coppia_dettaglio": "Vice di Vicario",
    "coppia_ibrida": False
}

players.append(neto_dict)

# Salva sia in data/processed che nella root
with open(MASTER_PATH, "w", encoding="utf-8") as f:
    json.dump(players, f, indent=2, ensure_ascii=False)

with open(ROOT_MASTER_PATH, "w", encoding="utf-8") as f:
    json.dump(players, f, indent=2, ensure_ascii=False)

print(f"✓ Neto aggiunto con successo! Totale calciatori ora: {len(players)}")
