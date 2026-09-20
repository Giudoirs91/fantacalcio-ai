import sys
sys.stdout.reconfigure(encoding='utf-8')
import pdfplumber
import json
import re

pdf_path = r"data/raw/match report 26-27/3_GENCOM_MatchReport_IT.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"=== MATCH REPORT: {pdf_path} (Pagine: {len(pdf.pages)}) ===")
    
    print("\n--- PAGINA 2: FORMAZIONI E MODULI ---")
    p2_text = pdf.pages[1].extract_text() or ""
    for line in p2_text.split('\n')[:40]:
        print(" ", line)
        
    print("\n--- PAGINA 3: CRONOLOGIA / EVENTI ---")
    p3_text = pdf.pages[2].extract_text() or ""
    for line in p3_text.split('\n')[:40]:
        print(" ", line)
        
    # Search for STATISTICHE GIOCATORE
    p_stats = None
    for idx, p in enumerate(pdf.pages):
        txt = p.extract_text() or ""
        if "STATISTICHE GIOCATORE" in txt:
            p_stats = p
            print(f"\n--- PAGINA {idx + 1}: STATISTICHE GIOCATORE ---")
            break
            
    if p_stats:
        tables = p_stats.extract_tables()
        print(f"Tabelle trovate in p_stats: {len(tables)}")
        for t_idx, tbl in enumerate(tables):
            print(f"\nTabella {t_idx} (righe: {len(tbl)}):")
            for r in tbl[:15]:
                print("   ", r)
