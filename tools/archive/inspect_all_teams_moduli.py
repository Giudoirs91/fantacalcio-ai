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
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Match team names and modulo
        # Look for the score line e.g. ATALANTA 2-1 SASSUOLO
        teams_line = ""
        modulo_line = ""
        for i, line in enumerate(lines):
            if " - " in line or re.search(r'[A-Z\s]+\s+\d+-\d+\s+[A-Z\s]+', line):
                teams_line = line
            if re.search(r'\d-\d-\d(-\d)?\s+\d-\d-\d(-\d)?', line):
                modulo_line = line
        print(f"=== {fname} ===")
        print(f"Teams Header: {teams_line}")
        print(f"Moduli: {modulo_line}")
