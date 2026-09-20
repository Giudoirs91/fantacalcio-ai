import pdfplumber
import os

pdf_path = os.path.join("match report 26-27", "1__INT-MON_MatchReport_IT.pdf")

with pdfplumber.open(pdf_path) as pdf:
    for i in range(len(pdf.pages)):
        text = pdf.pages[i].extract_text()
        print(f"\n==================== PAGE {i+1} ====================")
        lines = [line.strip().encode('ascii', 'ignore').decode('ascii') for line in text.split('\n') if line.strip()]
        for l in lines[:10]:
            print(" ", l)
