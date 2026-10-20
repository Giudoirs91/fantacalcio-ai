"""
tools/telegram_approval_daemon.py
=================================
Demone di ascolto in background per le approvazioni Telegram.
Controlla ogni 3 secondi se l'amministratore (@GiuProf) ha cliccato su
[ ✅ Approva e Pubblica ] o [ ❌ Scarta ] o ha risposto con 'ok'/'approva'.
Appena riceve l'ok, pubblica istantaneamente il post sul canale @fantamasterai.
"""

import os
import sys
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.telegram_approval import check_approvals

def run_daemon():
    print("[TelegramDaemon] Demone di approvazione avviato. In ascolto real-time...")
    while True:
        try:
            results = check_approvals()
            if results:
                for action, d_id in results:
                    print(f"[{action}] Bozza {d_id} processata con successo!")
        except Exception as e:
            # Non interrompere il ciclo in caso di fluttuazioni di rete
            pass
        time.sleep(3)

if __name__ == "__main__":
    run_daemon()
