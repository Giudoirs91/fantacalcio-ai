import re
from bs4 import BeautifulSoup

html_path = r'C:\Users\dorsi\.gemini\antigravity-ide\brain\7af7e5fc-14b8-4989-a38d-a88d602cb641\.system_generated\steps\379\content.md'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
for script in soup(['script', 'style', 'nav', 'header', 'footer']):
    script.extract()

text = soup.get_text()
lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 30]
clean_text = '\n\n'.join(lines)

with open('scratch/article_text.txt', 'w', encoding='utf-8') as f:
    f.write(clean_text)

print(f"Estratte {len(lines)} righe di testo significativo.")
print("\n--- PRIME RIGHE DELL'ARTICOLO ---")
print('\n\n'.join(lines[:15]))
