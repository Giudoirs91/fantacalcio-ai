import pdfplumber
import os

pdf_path = os.path.join("match report 26-27", "1__INT-MON_MatchReport_IT.pdf")

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total Pages in {pdf_path}: {len(pdf.pages)}")
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        first_lines = text.split('\n')[:5] if text else []
        print(f"\n--- Page {i+1} ---")
        print("Header:", first_lines)
