import pdfplumber
import os
import re
import pandas as pd

REPORT_DIR = "match report 26-27"
pdf_files = [f for f in os.listdir(REPORT_DIR) if f.endswith(".pdf")]

print(f"Testing extraction on {len(pdf_files)} Match Report PDFs...")

for fname in sorted(pdf_files):
    fpath = os.path.join(REPORT_DIR, fname)
    with pdfplumber.open(fpath) as pdf:
        # Title and Match info from Page 1 or 2
        p1_text = pdf.pages[0].extract_text() or ""
        p2_text = pdf.pages[1].extract_text() or ""
        
        # Match header (e.g. "INTER 4-1 MONZA" or "ATALANTA 2-0 SASSUOLO")
        lines = p2_text.split('\n')
        match_title = lines[4] if len(lines) > 4 else "Unknown"
        print(f"PDF: {fname:<32} -> {match_title}")
