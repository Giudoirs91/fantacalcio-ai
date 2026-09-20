import sys
sys.stdout.reconfigure(encoding='utf-8')
import pdfplumber
import json
import re

pdf_path = "match report 26-27/2_ATA-BOL_MatchReport_IT.pdf"

print(f"=== APERTURA MATCH REPORT: {pdf_path} ===")

with pdfplumber.open(pdf_path) as pdf:
    print(f"Totale pagine: {len(pdf.pages)}")
    
    # 1. Info Match e Formazioni
    for idx, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        print(f"\n--- PAGINA {idx + 1} ---")
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:25]:
            print(f"  {line}")
