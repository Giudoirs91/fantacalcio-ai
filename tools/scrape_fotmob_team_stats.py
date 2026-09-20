"""
Scrape and process the essential Serie A 2026/27 team stats from FotMob.
Selected Key Metrics for Fantacalcio:
1. expected_goals_team -> Total Expected Goals (Attacking quality)
2. expected_goals_conceded_team -> Total Expected Goals Conceded (True defensive solidity)
3. clean_sheet_team -> Clean sheets (Portieri & Modificatore Difesa)
4. big_chance_team -> Big chances created (Bonus generator volume)
5. touches_in_opp_box_team -> Area dominance (Offensive pressure)
6. corner_taken_team -> Corners taken (Value for set piece specialists & crossing fullbacks)
7. saves_team -> Saves per match (Low-cost / Modificatore goalkeeper goldmine)
8. goals_conceded_team_match -> Real goals conceded / match (Direct malus risk)
"""

import os
import json
import requests
import pandas as pd

ESSENTIAL_METRICS = [
    {
        "id": "xg_team",
        "name": "expected_goals_team",
        "label": "xG Totali",
        "category": "Attacco",
        "description": "Pericolosità offensiva creata"
    },
    {
        "id": "xga_team",
        "name": "expected_goals_conceded_team",
        "label": "xG Concessi (xGA)",
        "category": "Difesa",
        "description": "Pericolosità concessa agli avversari (più basso = difesa migliore)"
    },
    {
        "id": "clean_sheets",
        "name": "clean_sheet_team",
        "label": "Clean Sheet",
        "category": "Difesa/Portiere",
        "description": "Porta inviolata (bonus portiere & modificatore)"
    },
    {
        "id": "big_chances",
        "name": "big_chance_team",
        "label": "Grandi Occasioni Create",
        "category": "Attacco",
        "description": "Occasioni nitide da gol prodotte"
    },
    {
        "id": "touches_opp_box",
        "name": "touches_in_opp_box_team",
        "label": "Tocchi Area Avversaria",
        "category": "Attacco",
        "description": "Presenza offensiva negli ultimi 16 metri"
    },
    {
        "id": "corners",
        "name": "corner_taken_team",
        "label": "Corner Battuti",
        "category": "Piazzati",
        "description": "Opportunità da palla inattiva per tiratori e saltatori"
    },
    {
        "id": "saves_per_match",
        "name": "saves_team",
        "label": "Parate a Partita",
        "category": "Portiere",
        "description": "Volume di interventi per portieri da modificatore"
    },
    {
        "id": "goals_conceded_match",
        "name": "goals_conceded_team_match",
        "label": "Gol Subiti / Partita",
        "category": "Difesa",
        "description": "Rischio malus medio a giornata"
    }
]

TEAM_NAME_MAPPING = {
    "Inter": "Inter",
    "Juventus": "Juventus",
    "Milan": "Milan",
    "Napoli": "Napoli",
    "Roma": "Roma",
    "Lazio": "Lazio",
    "Atalanta": "Atalanta",
    "Fiorentina": "Fiorentina",
    "Bologna": "Bologna",
    "Torino": "Torino",
    "Como": "Como",
    "Genoa": "Genoa",
    "Parma": "Parma",
    "Cagliari": "Cagliari",
    "Udinese": "Udinese",
    "Empoli": "Empoli",
    "Hellas Verona": "Verona",
    "Verona": "Verona",
    "Monza": "Monza",
    "Lecce": "Lecce",
    "Venezia": "Venezia",
    "Sassuolo": "Sassuolo",
    "Pisa": "Pisa",
    "Cremonese": "Cremonese",
    "Palermo": "Palermo",
    "Sampdoria": "Sampdoria"
}

import subprocess

def fetch_metric(metric_info):
    name = metric_info["name"]
    url = f"https://data.fotmob.com/stats/55/season/36072/{name}.json"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        cmd = ['curl.exe', '-s', '--compressed', url]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=8, encoding='utf-8', errors='ignore')
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout)
            top_lists = data.get("TopLists", [])
            if top_lists:
                return top_lists[0].get("StatList", [])
    except Exception:
        pass

    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code == 200:
            data = r.json()
            top_lists = data.get("TopLists", [])
            if top_lists:
                return top_lists[0].get("StatList", [])
    except Exception as e:
        print(f"Error fetching {name}: {e}")
    return []

def main():
    print("Scraping essential FotMob Serie A 2026/27 team stats...")
    teams_data = {} # standardized_team_name -> dict of stats

    for metric in ESSENTIAL_METRICS:
        m_id = metric["id"]
        m_name = metric["name"]
        stat_list = fetch_metric(metric)
        print(f"Fetched {metric['label']} ({m_name}): {len(stat_list)} teams")

        for row in stat_list:
            raw_team = row.get("ParticipantName", "").strip()
            std_team = TEAM_NAME_MAPPING.get(raw_team, raw_team)
            val = row.get("StatValue", 0)
            rank = row.get("Rank", 0)
            matches = row.get("MatchesPlayed", 0)

            if std_team not in teams_data:
                teams_data[std_team] = {
                    "squadra": std_team,
                    "raw_name": raw_team,
                    "partite_giocate": matches,
                    "team_id": row.get("TeamId", 0),
                    "team_color": row.get("TeamColor", "#333333")
                }
            
            if matches > teams_data[std_team]["partite_giocate"]:
                teams_data[std_team]["partite_giocate"] = matches

            teams_data[std_team][m_id] = val
            teams_data[std_team][f"{m_id}_rank"] = rank

    # Create Summary Ratings for Fanta Tactical Context
    # 1. Indice Forza Offensiva (Rank xG + Rank Big Chances + Rank Tocchi)
    # 2. Indice Solidità Difensiva (Rank xGA + Rank Clean Sheets + Rank Gol Subiti)
    for team, d in teams_data.items():
        xg_rk = d.get("xg_team_rank", 10)
        bc_rk = d.get("big_chances_rank", 10)
        box_rk = d.get("touches_opp_box_rank", 10)
        d["attacco_rank_medio"] = round((xg_rk + bc_rk + box_rk) / 3.0, 1)

        xga_rk = d.get("xga_team_rank", 10)
        cs_rk = d.get("clean_sheets_rank", 10)
        gc_rk = d.get("goals_conceded_match_rank", 10)
        d["difesa_rank_medio"] = round((xga_rk + cs_rk + gc_rk) / 3.0, 1)

        # Rating tier: Top, Buono, Medio, Fragile
        if d["difesa_rank_medio"] <= 5:
            d["difesa_label"] = "Muro Difensivo (Top 5)"
            d["difesa_tier"] = "top"
        elif d["difesa_rank_medio"] <= 10:
            d["difesa_label"] = "Solida (Metà Classifica Alta)"
            d["difesa_tier"] = "good"
        elif d["difesa_rank_medio"] <= 15:
            d["difesa_label"] = "Media (Vulnerabile)"
            d["difesa_tier"] = "medium"
        else:
            d["difesa_label"] = "Fragile (Alto Rischio Malus)"
            d["difesa_tier"] = "risk"

        if d["attacco_rank_medio"] <= 5:
            d["attacco_label"] = "Macchina da Bonus (Top 5)"
            d["attacco_tier"] = "top"
        elif d["attacco_rank_medio"] <= 10:
            d["attacco_label"] = "Buona Produzione"
            d["attacco_tier"] = "good"
        elif d["attacco_rank_medio"] <= 15:
            d["attacco_label"] = "Attacco Faticoso"
            d["attacco_tier"] = "medium"
        else:
            d["attacco_label"] = "Sterile (Poche Occasioni)"
            d["attacco_tier"] = "risk"

    os.makedirs("data/raw", exist_ok=True)
    json_path = "data/raw/fotmob_team_stats_2026_27.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(teams_data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(teams_data)} teams to {json_path}")

    # Also save CSV for easy preview
    df = pd.DataFrame(list(teams_data.values()))
    csv_path = "data/raw/fotmob_team_stats_2026_27.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"Saved CSV to {csv_path}")

    # Print a quick preview
    print("\nPreview Top 5 Attacchi (xG):")
    top_xg = sorted(teams_data.values(), key=lambda x: x.get("xg_team", 0), reverse=True)[:5]
    for t in top_xg:
        print(f"  {t['squadra']}: {t.get('xg_team')} xG (Rank {t.get('xg_team_rank')}) - {t['attacco_label']}")

    print("\nPreview Top 5 Difese (xGA più basso):")
    top_xga = sorted(teams_data.values(), key=lambda x: x.get("xga_team", 99))[:5]
    for t in top_xga:
        print(f"  {t['squadra']}: {t.get('xga_team')} xGA (Rank {t.get('xga_team_rank')}) - {t['difesa_label']}")

if __name__ == "__main__":
    main()
