import pdfplumber
import os

test_pdf = os.path.join("match report 26-27", "1__INT-MON_MatchReport_IT.pdf")
with pdfplumber.open(test_pdf) as pdf:
    p5 = pdf.pages[4]
    tables = p5.extract_tables()
    print(f"Tables found on Page 5: {len(tables)}")
    for i, t in enumerate(tables):
        print(f"\n--- Table {i+1} (Rows: {len(t)}) ---")
        for row in t[:6]:
            safe_row = [str(c).replace('\n', ' ').encode('ascii', 'ignore').decode('ascii') if c else '' for c in row]
            print(" ", safe_row)
