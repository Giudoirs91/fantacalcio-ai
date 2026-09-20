import sys
sys.stdout.reconfigure(encoding='utf-8')
import pdfplumber

pdf_path = "match report 26-27/2_ATA-BOL_MatchReport_IT.pdf"

with pdfplumber.open(pdf_path) as pdf:
    # Page 2: Lineups & Formations
    print("=== FORMAZIONI E PANCHINE (PAGINA 2) ===")
    print(pdf.pages[1].extract_text())

    # Page 3: Cronologia / Eventi
    print("\n=== CRONOLOGIA EVENTI (PAGINA 3) ===")
    print(pdf.pages[2].extract_text())

    # Page 5: Statistiche Giocatori
    print("\n=== STATISTICHE GIOCATORI (PAGINA 5) ===")
    print(pdf.pages[4].extract_text())
