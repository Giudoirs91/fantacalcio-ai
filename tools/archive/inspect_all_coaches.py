import pdfplumber
import os
import re

REPORT_DIR = "match report 26-27"
pdf_files = sorted([f for f in os.listdir(REPORT_DIR) if f.endswith(".pdf")])

for fname in pdf_files:
    fpath = os.path.join(REPORT_DIR, fname)
    with pdfplumber.open(fpath) as pdf:
        p2 = pdf.pages[1]
        text = p2.extract_text() or ""
        lines = [l.strip().encode('ascii', 'ignore').decode('ascii') for l in text.split('\n') if l.strip()]
        
        # Look for Allenatore line at the bottom of Page 2
        all_lines = [l for l in lines if "Allenatore" in l or "ALLENATORE" in l]
        print(f"=== {fname} ===")
        for al in all_lines:
            print(" ", al)
        print("  Bottom 5 lines:")
        for l in lines[-6:]:
            print("   ", l)
