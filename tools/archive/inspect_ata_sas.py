import pdfplumber
import os

pdf_path = os.path.join("match report 26-27", "1_ATA-SAS_MatchReport_IT.pdf")
with pdfplumber.open(pdf_path) as pdf:
    p2 = pdf.pages[1]
    txt = p2.extract_text()
    lines = [l.strip().encode('ascii', 'ignore').decode('ascii') for l in txt.split('\n') if l.strip()]
    for l in lines[:40]:
        print(" ", l)
