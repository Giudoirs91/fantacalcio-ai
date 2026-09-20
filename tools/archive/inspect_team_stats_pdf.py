import pdfplumber
import os

test_pdf = os.path.join("match report 26-27", "1__INT-MON_MatchReport_IT.pdf")
with pdfplumber.open(test_pdf) as pdf:
    # Page 4
    print("=== PAGE 4 TABLES (TEMPO & STATISTICHE) ===")
    t4 = pdf.pages[3].extract_tables()
    for i, t in enumerate(t4):
        print(f"--- Table {i+1} ---")
        for row in t[:8]:
            safe_row = [str(c).replace('\n', ' ').encode('ascii', 'ignore').decode('ascii') if c else '' for c in row]
            print(" ", safe_row)

    # Page 6
    print("\n=== PAGE 6 (INDICATORI SQUADRA) ===")
    p6_text = pdf.pages[5].extract_text()
    lines = [l.strip().encode('ascii', 'ignore').decode('ascii') for l in p6_text.split('\n') if l.strip()]
    for l in lines[:15]:
        print(" ", l)

    # Page 9
    print("\n=== PAGE 9 (BARICENTRO) ===")
    p9_text = pdf.pages[8].extract_text()
    lines9 = [l.strip().encode('ascii', 'ignore').decode('ascii') for l in p9_text.split('\n') if l.strip()]
    for l in lines9[:15]:
        print(" ", l)
