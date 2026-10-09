"""
send_telegram_friday_top.py - Messaggio Consigli & Top di Giornata (Venerdì ore 19:00)
======================================================================================
Invia sul canale Telegram @fantamasterai il messaggio ufficiale con i possibili
Top di Giornata per reparto calcolati dall'algoritmo predittivo, la Social Card HD
e il link diretto alla pagina:
👉 https://www.fantamasterai.it/consigli-fantacalcio/
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
    get_round_fixtures,
    generate_telegram_card_image,
    send_telegram_photo,
    send_telegram_message
)

def build_friday_19_message(round_num):
    top_advice = get_top_advice_by_role(round_num)
    _, round_date, _ = get_round_fixtures(round_num)

    p_gk = top_advice.get('P', [{}])[0].get('player', {}) if top_advice.get('P') else {}
    f_gk = top_advice.get('P', [{}])[0].get('fixture', {}) if top_advice.get('P') else {}

    p_df = top_advice.get('D', [{}])[0].get('player', {}) if top_advice.get('D') else {}
    f_df = top_advice.get('D', [{}])[0].get('fixture', {}) if top_advice.get('D') else {}

    p_mf = top_advice.get('C', [{}])[0].get('player', {}) if top_advice.get('C') else {}
    f_mf = top_advice.get('C', [{}])[0].get('fixture', {}) if top_advice.get('C') else {}

    p_fw = top_advice.get('A', [{}])[0].get('player', {}) if top_advice.get('A') else {}
    f_fw = top_advice.get('A', [{}])[0].get('fixture', {}) if top_advice.get('A') else {}

    msg = f"🔥 *I TOP DI GIORNATA — SERIE A (TURNO {round_num})* ⚽\n\n"
    msg += f"Mister, il weekend si avvicina! Ecco la selezione dei *4 calciatori con il più alto potenziale di bonus e rendimento atteso* secondo i modelli predittivi di Fanta Master AI:\n\n"

    msg += f"🧤 *PORTIERE TOP:* *{p_gk.get('name', 'N/D')}* ({p_gk.get('team', '')})\n"
    msg += f"   ↳ _{f_gk.get('label', '')} • OVR {p_gk.get('ovr', 80)}: clean sheet ad alta probabilità e solidità difensiva._\n\n"

    msg += f"🛡️ *DIFENSORE DA MODIFICATORE:* *{p_df.get('name', 'N/D')}* ({p_df.get('team', '')})\n"
    msg += f"   ↳ _{f_df.get('label', '')} • OVR {p_df.get('ovr', 80)}: garanzia da 6.5+ con pericolosità sui piazzati._\n\n"

    msg += f"🪄 *CENTROCAMPISTA DA BONUS:* *{p_mf.get('name', 'N/D')}* ({p_mf.get('team', '')})\n"
    msg += f"   ↳ _{f_mf.get('label', '')} • OVR {p_mf.get('ovr', 80)}: volume di Expected Assist (xA) e tiri verso la porta._\n\n"

    msg += f"⚡ *ATTACCANTE BOMBER:* *{p_fw.get('name', 'N/D')}* ({p_fw.get('team', '')})\n"
    msg += f"   ↳ _{f_fw.get('label', '')} • OVR {p_fw.get('ovr', 90)}: primo terminale offensivo ad alto xG._\n\n"

    msg += f"━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📋 *VUOI SCOPRIRE TUTTI I CONSIGLIATI RUOLO PER RUOLO?*\n"
    msg += f"Consulta la guida completa con fasce, rigoristi e sorprese di giornata:\n"
    msg += f"👉 *https://www.fantamasterai.it/consigli-fantacalcio/*\n\n"

    msg += f"⚔️ *DUBBI 1vs1? USA IL COMPARATORE AI:*\n"
    msg += f"👉 *https://www.fantamasterai.it/chi-schiero/*"
    return msg

def send_friday_top_message(dry_run=False):
    config = load_telegram_config()
    token = config.get("bot_token")
    channel_id = config.get("channel_id", "@fantamasterai")
    round_num = get_upcoming_round()

    print(f"=== [Telegram] Invio Top di Giornata (Turno {round_num}) a {channel_id} ===")
    
    # Genera la Social Card HD
    card_path = generate_telegram_card_image(round_num)
    message_text = build_friday_19_message(round_num)

    if dry_run:
        print("\n--- ANTEPRIMA MESSAGGIO (DRY-RUN) ---")
        print(f"Canale di destinazione: {channel_id}")
        print(f"Social card: {card_path}")
        print("\nTesto del messaggio:")
        print(message_text)
        print("--- FINE ANTEPRIMA (Nessun messaggio inviato su Telegram) ---\n")
        return {"ok": True, "dry_run": True}

    caption = f"🔥 *TOP CALCIATORI GIORNATA {round_num} — FANTA MASTER AI* 📅\n_Consigli predittivi ufficiali per il weekend di Serie A_"
    photo_res = send_telegram_photo(token, channel_id, card_path, caption=caption)
    msg_res = send_telegram_message(token, channel_id, message_text)

    print("✓ Invio completato con successo!")
    return {"photo_res": photo_res, "msg_res": msg_res}

if __name__ == '__main__':
    dry = "--dry-run" in sys.argv
    send_friday_top_message(dry_run=dry)
