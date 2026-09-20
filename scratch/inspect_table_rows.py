from bs4 import BeautifulSoup
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\dorsi\.gemini\antigravity-ide\brain\5669a18c-ff6d-45d7-87f2-c433188ebe8a\.system_generated\steps\713\content.md', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
table = soup.find('table', id='infortunati_ufficiali')
rows = table.find_all('tr')

print(f"Total rows: {len(rows)}")
for i, r in enumerate(rows[1:]):
    cols = [td.get_text(strip=True) for td in r.find_all(['td', 'th'])]
    # Also inspect links or spans inside Calciatore
    calciatore_td = r.find_all('td')[1] if len(r.find_all('td')) > 1 else None
    inner_text = calciatore_td.get_text(" ", strip=True) if calciatore_td else ""
    print(f"{i+1}. Squadra: {cols[0]} | Calciatore: '{inner_text}' | Motivo: {cols[2][:50]} | Rientro: {cols[3]}")
