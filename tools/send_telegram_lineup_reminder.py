"""
send_telegram_lineup_reminder.py - Alert Scadenza Formazione (Sabato ore 14:30)
================================================================================
Invia un alert su Telegram 30 minuti prima dell'inizio delle partite di Serie A:
- Avviso perentorio per la consegna della formazione (calcio d'inizio ore 15:00).
- Link prioritario alla lista infortunati ufficiale:
  👉 https://www.fantamasterai.it/infortunati-serie-a/
- Teaser sintetici per invogliare a leggere i consigli di giornata:
  👉 https://www.fantamasterai.it/consigli-fantacalcio/
- Link al comparatore 1vs1 Chi Schiero:
  👉 https://www.fantamasterai.it/chi-schiero/
"""

import os
import sys
import json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.telegram_engine import (
    load_telegram_config,
    get_upcoming_round,
    get_top_advice_by_role,
    send_telegram_message
)

def build_lineup_reminder_message(round_num):
    top_advice = get_top_advice_by_role(round_num)
    
    p_gk = top_advice.get('P', [{}])[0].get('player', {}) if top_advice.get('P') else {}
    p_df = top_advice.get('D', [{}])[0].get('player', {}) if top_advice.get('D') else {}
    p_mf = top_advice.get('C', [{}])[0].get('player', {}) if top_advice.get('C') else {}
    p_fw = top_advice.get('A', [{}])[0].get('player', {}) if top_advice.get('A') else {}

    msg = f"⏰ *MISTER, NON DIMENTICARTI DI INSERIRE LA FORMAZIONE!* ⏳\n\n"
    msg += f"🚨 *Fra mezz'ora inizia il primo turno della giornata di Serie A (ore 15:00)!*\n\n"
    
    msg += f"Prima di consegnare la tua rosa, fai un controllo fondamentale per evitare di giocare in 10:\n"
    msg += f"🚑 *Controlla la lista ufficiale degli infortunati e tempi di rientro:*\n"
    msg += f"👉 *https://www.fantamasterai.it/infortunati-serie-a/*\n\n"
    
    msg += f"━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"💡 *CHI SCHIERARE? I CONSIGLI FLASH DELLA GIORNATA {round_num}:*\n"
    msg += f"Ecco i punti chiave analizzati dal nostro algoritmo per non sbagliare:\n\n"
    
    msg += f"🧤 *Tra i Pali:* Occhio alle gare insidiose in trasferta. *{p_gk.get('name', 'Il portiere top')}* guida l'indice di imbattibilità per il modificatore.\n\n"
    msg += f"🛡️ *In Difesa:* Spazio ai difensori che salgono sui corner e terzini di spinta come *{p_df.get('name', 'il top di reparto')}*.\n\n"
    msg += f"🪄 *A Centrocampo:* Schiera i rigoristi e chi calcia i piazzati: *{p_mf.get('name', 'la stella')}* ha un volume di Expected Assist sopra la media.\n\n"
    msg += f"⚡ *In Attacco:* Non farti ingannare dalle riserve dell'ultimo minuto. Bomber come *{p_fw.get('name', 'il bomber')}* vanno messi a tutti i costi.\n\n"
    
    msg += f"📖 *Leggi l'analisi completa con tutti i consigliati ruolo per ruolo:*\n"
    msg += f"👉 *https://www.fantamasterai.it/consigli-fantacalcio/*\n\n"
    
    msg += f"⚔️ *Hai ancora un dubbio dell'ultimo minuto?*\n"
    msg += f"Metti a confronto i tuoi 2 giocatori testa a testa nel comparatore AI:\n"
    msg += f"👉 *https://www.fantamasterai.it/chi-schiero/*\n\n"
    msg += f"Buon fantacalcio e buona Serie A a tutti i fantallenatori! 🍀"
    return msg

def send_lineup_reminder(dry_run=False):
    config = load_telegram_config()
    token = config.get("bot_token")
    channel_id = config.get("channel_id", "@fantamasterai")
    round_num = get_upcoming_round()

    print(f"=== [Telegram] Alert Scadenza Formazione (Turno {round_num}) per {channel_id} ===")
    message_text = build_lineup_reminder_message(round_num)

    if dry_run:
        print("\n--- ANTEPRIMA ALERT FORMAZIONE (DRY-RUN) ---")
        print(f"Canale di destinazione: {channel_id}")
        print("\nTesto del messaggio:")
        print(message_text)
        print("--- FINE ANTEPRIMA (Nessun messaggio inviato su Telegram) ---\n")
        return {"ok": True, "dry_run": True}

    msg_res = send_telegram_message(token, channel_id, message_text)
    print("✓ Alert inviato con successo!")
    return {"msg_res": msg_res}

if __name__ == '__main__':
    dry = "--dry-run" in sys.argv
    send_lineup_reminder(dry_run=dry)
