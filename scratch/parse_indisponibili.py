from bs4 import BeautifulSoup
import re

path = r'C:\Users\dorsi\.gemini\antigravity-ide\brain\867131f5-e3ac-404d-86be-6fad3b886bba\.system_generated\steps\267\content.md'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Print divs or sections under "Infortunati della Serie A"
infort_h2 = soup.find(lambda tag: tag.name == 'h2' and 'Infortunati' in tag.text)
if infort_h2:
    parent = infort_h2.find_parent()
    print("Infortunati h2 parent:", parent.name, parent.get('class'))
    # look at siblings or children
    for child in parent.find_all(recursive=False):
        print("  Child tag:", child.name, child.get('class'))

team_cards = soup.find_all(class_='team-card')
print(f"Total team-cards: {len(team_cards)}")
for tc in team_cards[:5]:
    team_name_el = tc.find(class_='team-name')
    team_name = team_name_el.get_text(strip=True) if team_name_el else "Unknown"
    print(f"\n=== SQUADRA: {team_name} ===")
    items = tc.find_all(class_='team-item')
    print(f"  Items trovati: {len(items)}")
    for it in items:
        name_el = it.find(class_='item-name')
        desc_el = it.find(class_='item-description')
        name = name_el.get_text(strip=True) if name_el else ""
        desc = desc_el.get_text(strip=True) if desc_el else ""
        # Also check any other classes or tags inside item
        subtags = [f"<{t.name} class='{t.get('class')}'>{t.get_text(strip=True)}</{t.name}>" for t in it.find_all(recursive=False)]
        print(f"    - Giocatore: '{name}' | Info: '{desc}' | Tags: {subtags}")

