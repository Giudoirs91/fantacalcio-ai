import pdfplumber
import os
import re

REPORT_DIR = "match report 26-27"
pdf_files = sorted([f for f in os.listdir(REPORT_DIR) if f.endswith(".pdf")])

for fname in pdf_files:
    fpath = os.path.join(REPORT_DIR, fname)
    with pdfplumber.open(fpath) as pdf:
        p2 = pdf.pages[1] if len(pdf.pages) > 1 else pdf.pages[0]
        text = p2.extract_text() or ""
        lines = [l.strip().encode('ascii', 'ignore').decode('ascii') for l in text.split('\n') if l.strip()]
        print(f"\n=======================================================")
        print(f"FILE: {fname}")
        print(f"=======================================================")
        for l in lines[:35]:
            print(" ", l)
