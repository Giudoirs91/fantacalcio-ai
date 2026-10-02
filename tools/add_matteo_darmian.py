import os
import openpyxl
import pandas as pd
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def add_matteo_darmian():
    excel_path = os.path.join(ROOT_DIR, "data", "raw", "Listone_definitivo_Fantacalcio_Stagione_2026_27.xlsx")
    print(f"1. Aggiunta a {excel_path}...")
    wb = openpyxl.load_workbook(excel_path)
    
    player_id = 2525
    row_data = [
        player_id,      # Id
        'D',            # R
        'Dd;Ds;E',      # RM (Mantra)
        'Darmian',      # Nome
        'Bologna',      # Squadra
        7,              # Qt.A
        7,              # Qt.I
        0,              # Diff.
        7,              # Qt.A M
        7,              # Qt.I M
        0,              # Diff.M
        9,              # FVM
        9               # FVM M
    ]
    
    # Aggiungi a 'Tutti' se non presente
    sheet_tutti = wb['Tutti']
    existing = False
    for r in range(2, sheet_tutti.max_row + 1):
        if sheet_tutti.cell(r, 4).value == 'Darmian':
            existing = True
            break
    
    if not existing:
        sheet_tutti.append(row_data)
        sheet_dif = wb['Difensori']
        sheet_dif.append(row_data)
        wb.save(excel_path)
        print("   -> Salvato con successo nel Listone Excel!")
    else:
        print("   -> Darmian già presente nel Listone Excel.")

    # 2. Aggiunta a preview_all_518_players_stats_2025_26.csv
    csv_path = os.path.join(ROOT_DIR, "data", "raw", "preview_all_518_players_stats_2025_26.csv")
    if os.path.exists(csv_path):
        print(f"2. Aggiunta a {csv_path}...")
        df = pd.read_csv(csv_path)
        if not (df['name'] == 'Darmian').any():
            new_row = {
                'id': player_id,
                'name': 'Darmian',
                'team_2627': 'Bologna',
                'role': 'D',
                'mantra': 'Dd;Ds;E',
                'fvm': 9.0,
                'has_data_2526': True,
                'league_2526': 'Serie A',
                'rating_2526': 6.78,
                'mins_2526': 246.0,
                'goals_2526': 0,
                'assists_2526': 0,
                'xg_2526': 0.1,
                'xg90_2526': 0.04,
                'xgot_2526': 0.05,
                'xa90_2526': 0.04,
                'shots90_2526': 0.37,
                'tkl_int90_2526': 2.56,
                'goals_prevented_2526': None
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(csv_path, index=False)
            print("   -> Salvato con successo in preview_all_518_players_stats_2025_26.csv!")
        else:
            print("   -> Darmian già presente nel CSV statistiche.")

    # 3. Aggiorna config/injuries_history.json
    inj_hist_path = os.path.join(ROOT_DIR, "config", "injuries_history.json")
    if os.path.exists(inj_hist_path):
        print(f"3. Aggiornamento {inj_hist_path} con storico infortuni Darmian Transfermarkt...")
        with open(inj_hist_path, "r", encoding="utf-8") as f:
            hist_db = json.load(f)
        
        if "Bologna" not in hist_db:
            hist_db["Bologna"] = {}
        
        hist_db["Bologna"]["Darmian"] = {
            "id": player_id,
            "tm_id": "54906",
            "tm_name": "Matteo Darmian",
            "name": "Darmian",
            "team": "Bologna",
            "ruolo": "D",
            "partite_saltate_totali": 28,
            "giorni_stop_totali": 136,
            "disponibilita_pct": 63.2,
            "recidive_muscolari": 1,
            "indice_fragilita_score": 62.0,
            "livello_fragilita": "ATTENZIONE",
            "fragility_label": "🟡 Attenzione (Soggetto a Stop)",
            "fragility_badge": "attenzione",
            "consiglio_medico_ai": "Attenzione: ha registrato 28 gare saltate con 1 stop muscolari. Consigliata copertura economica in panchina.",
            "infortunio_attivo": False,
            "cronistoria_infortuni": [
                {
                    "stagione": "25/26",
                    "motivo": "Gastroenterite",
                    "diagnosi": "Gastroenterite",
                    "data_inizio": "03/02/2026",
                    "data_fine": "07/02/2026",
                    "giorni_stop": 5,
                    "giorni": 5,
                    "partite_perse": 1,
                    "tipo": "medico",
                    "in_corso": False
                },
                {
                    "stagione": "25/26",
                    "motivo": "Problema al polpaccio",
                    "diagnosi": "Problema al polpaccio",
                    "data_inizio": "15/10/2025",
                    "data_fine": "13/01/2026",
                    "giorni_stop": 91,
                    "giorni": 91,
                    "partite_perse": 19,
                    "tipo": "muscolare",
                    "in_corso": False
                },
                {
                    "stagione": "25/26",
                    "motivo": "Lombalgia",
                    "diagnosi": "Lombalgia",
                    "data_inizio": "15/09/2025",
                    "data_fine": "20/09/2025",
                    "giorni_stop": 6,
                    "giorni": 6,
                    "partite_perse": 1,
                    "tipo": "medico",
                    "in_corso": False
                },
                {
                    "stagione": "24/25",
                    "motivo": "Infortunio alla coscia",
                    "diagnosi": "Infortunio alla coscia",
                    "data_inizio": "25/02/2025",
                    "data_fine": "18/03/2025",
                    "giorni_stop": 22,
                    "giorni": 22,
                    "partite_perse": 5,
                    "tipo": "muscolare",
                    "in_corso": False
                },
                {
                    "stagione": "24/25",
                    "motivo": "Contusione al ginocchio",
                    "diagnosi": "Contusione al ginocchio",
                    "data_inizio": "21/12/2024",
                    "data_fine": "01/01/2025",
                    "giorni_stop": 12,
                    "giorni": 12,
                    "partite_perse": 2,
                    "tipo": "traumatico",
                    "in_corso": False
                },
                {
                    "stagione": "22/23",
                    "motivo": "Infortunio agli adduttori",
                    "diagnosi": "Infortunio agli adduttori",
                    "data_inizio": "07/11/2022",
                    "data_fine": "08/12/2022",
                    "giorni_stop": 32,
                    "giorni": 32,
                    "partite_perse": 4,
                    "tipo": "muscolare",
                    "in_corso": False
                },
                {
                    "stagione": "21/22",
                    "motivo": "Infortunio alla coscia",
                    "diagnosi": "Infortunio alla coscia",
                    "data_inizio": "28/11/2021",
                    "data_fine": "21/12/2021",
                    "giorni_stop": 24,
                    "giorni": 24,
                    "partite_perse": 5,
                    "tipo": "muscolare",
                    "in_corso": False
                },
                {
                    "stagione": "19/20",
                    "motivo": "Stiramento alla coscia",
                    "diagnosi": "Stiramento alla coscia",
                    "data_inizio": "27/09/2019",
                    "data_fine": "15/10/2019",
                    "giorni_stop": 19,
                    "giorni": 19,
                    "partite_perse": 3,
                    "tipo": "muscolare",
                    "in_corso": False
                }
            ]
        }
        
        # Aggiorna anche Holm: infortunio_attivo = True
        if "Holm" in hist_db["Bologna"]:
            hist_db["Bologna"]["Holm"]["infortunio_attivo"] = True

        with open(inj_hist_path, "w", encoding="utf-8") as f:
            json.dump(hist_db, f, ensure_ascii=False, indent=2)
        print("   -> Salvato injuries_history.json con successo!")

    # 4. Aggiorna player_aliases.json
    aliases_path = os.path.join(ROOT_DIR, "config", "player_aliases.json")
    if os.path.exists(aliases_path):
        with open(aliases_path, "r", encoding="utf-8") as f:
            aliases = json.load(f)
        aliases["Matteo Darmian"] = "Darmian"
        with open(aliases_path, "w", encoding="utf-8") as f:
            json.dump(aliases, f, ensure_ascii=False, indent=2)
        print("   -> Aggiornato player_aliases.json!")

if __name__ == "__main__":
    add_matteo_darmian()
