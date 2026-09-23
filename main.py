import sys
import argparse
from src.pipeline import run_master_pipeline
from web.build_dashboard import build_standalone_dashboard

def main():
    parser = argparse.ArgumentParser(description="FANTA MASTER AI — Serie A 2026/27 Orchestrator")
    parser.add_argument("--pipeline-only", action="store_true", help="Esegue solo il calcolo e la pipeline dati")
    parser.add_argument("--dashboard-only", action="store_true", help="Compila solo la dashboard HTML standalone")
    parser.add_argument("--build", action="store_true", help="Esegue pipeline completa e compila la dashboard")
    parser.add_argument("--apk", action="store_true", help="Compila anche l'APK Android in dist/FantaMasterAI.apk")
    parser.add_argument("--serve", action="store_true", help="Avvia il server Live Real-Time per sincronizzare PC e Smartphone")
    parser.add_argument("--port", type=int, default=8000, help="Porta per il server Live (default: 8000)")

    args = parser.parse_args()

    if args.serve:
        from src.server import run_server
        run_server(port=args.port)
        return

    if args.apk:
        print("[Main] Esecuzione Completa + Compilazione APK Android...")
        run_master_pipeline()
        from tools.build_apk import build_apk
        build_apk()
        return

    if args.dashboard_only:
        print("[Main] Compilazione Dashboard Web...")
        build_standalone_dashboard()
    elif args.pipeline_only:
        print("[Main] Esecuzione Pipeline Quantitativa...")
        run_master_pipeline()
    else:
        print("[Main] Esecuzione Completa (Pipeline + Dashboard)...")
        run_master_pipeline()
        try:
            from tools.build_top_flop_data import run_pipeline as run_top_flop
            run_top_flop()
        except Exception as e:
            print(f"[Main] Avviso top/flop: {e}")
        try:
            from src.matchday_evaluator import evaluate_round
            evaluate_round(5)
        except Exception as e:
            print(f"[Main] Avviso matchday evaluation: {e}")
        build_standalone_dashboard(sync_android=False)
        print("\n--> Processo completato con successo! Puoi aprire 'Dashboard_Fanta_1000.html' nel tuo browser.")

if __name__ == "__main__":
    main()
