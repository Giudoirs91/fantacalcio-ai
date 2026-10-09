"""
run_daily_update.py - Pipeline Quotidiana Completa (Infortuni + Build Sito + Telegram)
======================================================================================
Esegue la routine automatica del mattino:
1. Scarica e sincronizza gli infortuni ufficiali aggiornati (sync_injuries_fantacalcio_online.py).
2. Ricostruisce le pagine statiche e la tabella infortuni / probabili formazioni (build_seo_site.py).
3. Invia il messaggio Telegram con le pillole del giorno (daily_telegram_briefing.py).
"""

import os
import sys
import subprocess
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def step_1_sync_injuries():
    print("\n--- STEP 1: Sincronizzazione Infortuni Live & Ricalcolo Metriche ---")
    from tools.sync_injuries_fantacalcio_online import sync_injuries
    sync_injuries()
    
    print("\n--- STEP 1b: Ricostruzione Database Storico Infortuni & Fragilità ---")
    from tools.build_injuries_history import build_injuries_history_database
    build_injuries_history_database()

    print("\n--- STEP 1c: Esecuzione Master Pipeline & Ricalcolo Metriche/OVR ---")
    from src.pipeline import run_master_pipeline
    run_master_pipeline()

    print("\n--- STEP 1d: Compilazione Dashboard Standalone ---")
    from web.build_dashboard import build_standalone_dashboard
    build_standalone_dashboard()
    print("✓ Step 1 completato con successo.")


def step_2_build_site():
    print("\n--- STEP 2: Ricostruzione Pagine Sito (SEO & Infortunati) ---")
    from tools.build_seo_site import build_all
    build_all()
    print("✓ Step 2 completato.")


def step_3_send_telegram(dry_run=False):
    print("\n--- STEP 3: Invio Daily Briefing su Telegram ---")
    from tools.daily_telegram_briefing import run_daily_briefing
    run_daily_briefing(dry_run=dry_run)
    print("✓ Step 3 completato.")


def main():
    start_time = datetime.now()
    dry_run = "--dry-run" in sys.argv
    print(f"=== [FantaMasterAI] Avvio Routine Quotidiana ({start_time.strftime('%Y-%m-%d %H:%M:%S')}) ===")
    if dry_run:
        print("⚠️ Modalità DRY-RUN attiva: Telegram non invierà messaggi reali.")

    # 1. Aggiorna dati infortuni
    step_1_sync_injuries()

    # 2. Ricostruisce il sito in dist/
    step_2_build_site()

    # 3. Spedisce il briefing mattutino Telegram
    step_3_send_telegram(dry_run=dry_run)

    duration = (datetime.now() - start_time).total_seconds()
    print(f"\n=== [FantaMasterAI] Routine Quotidiana completata con successo in {duration:.1f} secondi! ===")


if __name__ == "__main__":
    main()
