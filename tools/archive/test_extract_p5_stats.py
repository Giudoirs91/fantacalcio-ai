import pdfplumber
import os
import re
import pandas as pd

REPORT_DIR = "match report 26-27"
pdf_files = [f for f in os.listdir(REPORT_DIR) if f.endswith(".pdf")]

print(f"Found {len(pdf_files)} Match Report PDFs in '{REPORT_DIR}':")
for f in pdf_files:
    print(f"  • {f}")

# Test extraction from Page 5 of Inter-Monza
test_pdf = os.path.join(REPORT_DIR, "1__INT-MON_MatchReport_IT.pdf")
with pdfplumber.open(test_pdf) as pdf:
    p5 = pdf.pages[4] # Page 5 (0-indexed 4)
    text = p5.extract_text()
    print("\n--- Raw Text Page 5 (Sample Lines) ---")
    lines = text.split('\n')
    for l in lines[:25]:
        print("  ", l.encode('ascii', 'ignore').decode('ascii'))
