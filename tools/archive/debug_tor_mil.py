import pdfplumber
import os

pdf_path = os.path.join("match report 26-27", "1_TOR-MIL_MatchReport_IT.pdf")
with pdfplumber.open(pdf_path) as pdf:
    print("TOR-MIL pages:", len(pdf.pages))
    for i, p in enumerate(pdf.pages):
        txt = p.extract_text() or ""
        first_line = txt.split('\n')[0] if txt else ""
        has_stats = "STATISTICHE GIOCATORE" in txt
        print(f"Page {i+1}: {first_line[:30]} | Has Player Stats: {has_stats} | Tables: {len(p.extract_tables())}")
