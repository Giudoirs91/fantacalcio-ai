"""
tools/sync_set_pieces_fantacalcio.py
===================================
Scarica ed estrae la gerarchia ufficiale di Rigoristi e Calci Piazzati (Punizioni e Corner)
dalla guida ufficiale di Fantacalcio.it (https://www.fantacalcio.it/rigoristi-serie-a).

Genera:
1. config/set_pieces.json (gerarchia completa per squadra)
2. Assegna rigorista_tier e piazzati_tier nel database processed_players_master.json
"""

import os
import sys
import json
import urllib.request
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.player_matcher import clean_text, match_player_name

URL = "https://www.fantacalcio.it/rigoristi-serie-a"
CONFIG_OUT = os.path.join(ROOT_DIR, "config", "set_pieces.json")
MASTER_PLAYERS_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")

# Normalizzazione nomi squadre fantacalcio.it -> database
TEAM_NORM = {
    "atalanta": "Atalanta",
    "bologna": "Bologna",
    "cagliari": "Cagliari",
    "como": "Como",
    "fiorentina": "Fiorentina",
    "frosinone": "Frosinone",
    "genoa": "Genoa",
    "inter": "Inter",
    "juventus": "Juventus",
    "lazio": "Lazio",
    "lecce": "Lecce",
    "milan": "Milan",
    "monza": "Monza",
    "napoli": "Napoli",
    "parma": "Parma",
    "roma": "Roma",
    "sassuolo": "Sassuolo",
    "torino": "Torino",
    "udinese": "Udinese",
    "venezia": "Venezia"
}


def fetch_set_pieces():
    print(f"\n[SetPieces Sync] Scaricamento dati da: {URL}")
    req = urllib.request.Request(
        URL,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8')

    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.find_all('div', class_='team-card')
    print(f"[SetPieces Sync] Trovate {len(cards)} schede squadra.")

    result = {}

    for c in cards:
        # Estrai nome squadra
        team_elem = c.find('h2') or c.find('h3') or c.find(class_='team-name') or c.find('strong')
        raw_team_name = ""
        if team_elem:
            raw_team_name = team_elem.get_text(strip=True)
        else:
            first_text = c.get_text(separator='|', strip=True).split('|')[0]
            raw_team_name = first_text

        team_key = raw_team_name.strip().lower()
        team_name = TEAM_NORM.get(team_key, raw_team_name.strip().title())

        # Estrai i link dei calciatori dentro la card: i primi 3 sono i rigoristi, i successivi 3 i piazzati
        player_links = c.find_all('a', href=lambda h: h and '/squadre/' in h)
        player_names = [a.get_text(strip=True) for a in player_links if a.get_text(strip=True)]

        rigoristi = player_names[:3] if len(player_names) >= 3 else player_names
        piazzati = player_names[3:6] if len(player_names) >= 6 else player_names[3:]

        result[team_name] = {
            "rigoristi": rigoristi,
            "calci_piazzati": piazzati
        }
        print(f"  ✓ {team_name:12} | Rigori: {', '.join(rigoristi)} | Piazzati: {', '.join(piazzati)}")

    # Salva config JSON
    os.makedirs(os.path.dirname(CONFIG_OUT), exist_ok=True)
    with open(CONFIG_OUT, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n[SetPieces Sync] Salvato database piazzati in: {CONFIG_OUT}")

    return result


def apply_set_pieces_to_master(set_pieces_data):
    """Aggiorna processed_players_master.json con i tier rigoristi e piazzati."""
    if not os.path.exists(MASTER_PLAYERS_PATH):
        print(f"⚠️ {MASTER_PLAYERS_PATH} non trovato.")
        return

    with open(MASTER_PLAYERS_PATH, 'r', encoding='utf-8') as f:
        master_players = json.load(f)

    print(f"\n[SetPieces Sync] Aggiornamento master players ({len(master_players)} giocatori)...")

    # Resetta i campi precedenti se presenti
    for p in master_players:
        p['rigorista_tier'] = 0
        p['piazzati_tier'] = 0

    matched_rigoristi = 0
    matched_piazzati = 0

    for team, data in set_pieces_data.items():
        team_players = [p for p in master_players if p.get('team', '').lower() == team.lower()]
        
        # Rigoristi
        for tier, name in enumerate(data.get('rigoristi', []), 1):
            matched = False
            norm_name = clean_text(name).lower()
            if not norm_name:
                continue

            for p in team_players:
                p_name = clean_text(p.get('name') or p.get('nome') or '').lower()
                if not p_name:
                    continue
                # Confronto intelligente
                if norm_name == p_name or norm_name in p_name or p_name in norm_name:
                    p['rigorista_tier'] = tier
                    matched = True
                    matched_rigoristi += 1
                    break

            if not matched:
                # Prova su tutti i giocatori con match di squadra flessibile
                for p in master_players:
                    p_name = clean_text(p.get('name') or p.get('nome') or '').lower()
                    if not p_name:
                        continue
                    if (norm_name == p_name or norm_name in p_name) and p.get('team', '').lower() == team.lower():
                        p['rigorista_tier'] = tier
                        matched_rigoristi += 1
                        break

        # Piazzati
        for tier, name in enumerate(data.get('calci_piazzati', []), 1):
            matched = False
            norm_name = clean_text(name).lower()
            if not norm_name:
                continue

            for p in team_players:
                p_name = clean_text(p.get('name') or p.get('nome') or '').lower()
                if not p_name:
                    continue
                if norm_name == p_name or norm_name in p_name or p_name in norm_name:
                    p['piazzati_tier'] = tier
                    matched = True
                    matched_piazzati += 1
                    break

            if not matched:
                for p in master_players:
                    p_name = clean_text(p.get('name') or p.get('nome') or '').lower()
                    if not p_name:
                        continue
                    if (norm_name == p_name or norm_name in p_name) and p.get('team', '').lower() == team.lower():
                        p['piazzati_tier'] = tier
                        matched_piazzati += 1
                        break

    with open(MASTER_PLAYERS_PATH, 'w', encoding='utf-8') as f:
        json.dump(master_players, f, indent=2, ensure_ascii=False)

    print(f"✓ Master players aggiornato: {matched_rigoristi} rigoristi mappati, {matched_piazzati} specialisti piazzati mappati!")


def main():
    data = fetch_set_pieces()
    apply_set_pieces_to_master(data)


if __name__ == "__main__":
    main()
