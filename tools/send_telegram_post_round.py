"""
tools/send_telegram_post_round.py
=================================
Invia sul canale Telegram @fantamasterai il post ufficiale di FINE TURNO:
- Top 3 e Flop 3 di giornata (con voti e fantavoti ricalcolati)
  👉 https://www.fantamasterai.it/top-flop/
- Statistiche più interessanti e curiosità del turno
  👉 https://www.fantamasterai.it/statistiche-serie-a/
- Call to action verso l'11 migliore e importazione rosa
  👉 https://www.fantamasterai.it

IMPORTANTE: Questo script viene eseguito SOLO su richiesta esplicita,
dopo che l'utente ha caricato e validato i voti e le statistiche dell'ultima giornata!
"""

import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from tools.daily_telegram_briefing import build_post_round_message, get_latest_completed_round
from src.telegram_engine import load_telegram_config, send_telegram_message


def run_post_round_broadcast(dry_run=False, round_override=None):
    round_num = round_override or get_latest_completed_round()
    print(f"\n=== [Post-Round Telegram] Preparazione Top & Flop Giornata {round_num} ===")

    msg, reply_markup = build_post_round_message(round_num)

    if dry_run:
        print("\n================= ANTEPRIMA POST-ROUND (DRY-RUN) =================")
        print(msg)
        print("\nBottoni Inline Telegram:")
        for row in reply_markup.get('inline_keyboard', []):
            print(" ", [b['text'] for b in row])
        print("===================================================================\n")
        print("✓ Nessun messaggio inviato (modalità dry-run attiva). Per inviare realmente usa --send")
        return msg

    cfg = load_telegram_config()
    token = cfg.get("bot_token")
    channel_id = cfg.get("channel_id")

    print(f"-> Invio broadcast post-round a {channel_id}...")
    res = send_telegram_message(token, channel_id, msg, reply_markup=reply_markup)
    if res and res.get('ok'):
        print("✓ Post-Round inviato con successo su Telegram!")
    else:
        print("❌ Errore durante l'invio del messaggio.")
    return res


if __name__ == '__main__':
    is_live = "--send" in sys.argv
    round_arg = None
    for a in sys.argv:
        if a.startswith("--round="):
            try:
                round_arg = int(a.split("=")[1])
            except ValueError:
                pass
    run_post_round_broadcast(dry_run=not is_live, round_override=round_arg)
