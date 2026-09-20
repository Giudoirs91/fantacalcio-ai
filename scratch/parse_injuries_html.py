from bs4 import BeautifulSoup
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\dorsi\.gemini\antigravity-ide\brain\5669a18c-ff6d-45d7-87f2-c433188ebe8a\.system_generated\steps\713\content.md', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
tables = soup.find_all('table')
print('Tables count:', len(tables))
for i, t in enumerate(tables):
    print(f'Table {i}: class={t.get("class")}, id={t.get("id")}')
    rows = t.find_all('tr')
    print(f'  rows: {len(rows)}')
    if rows:
        print('  header:', [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])])
        if len(rows) > 1:
            print('  row 1:', [td.get_text(strip=True) for td in rows[1].find_all(['th', 'td'])])
        if len(rows) > 2:
            print('  row 2:', [td.get_text(strip=True) for td in rows[2].find_all(['th', 'td'])])

print("\n--- Headings ---")
for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])[:20]:
    print(h.name, h.get_text(strip=True))
