import pdfplumber
import os
import re
import pandas as pd

REPORT_DIR = "match report 26-27"
pdf_files = sorted([f for f in os.listdir(REPORT_DIR) if f.endswith(".pdf")])

def parse_player_stats_page(text, home_team, away_team, match_info):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Track which team we are parsing
    current_team = home_team
    players = []
    
    for line in lines:
        if away_team.upper() in line.upper() and len(line.split()) <= 3:
            current_team = away_team
            continue
            
        # Match player line: starts with shirt number, followed by name and minutes (e.g. "94 P. ESPOSITO 95' ...")
        # Regex: ^(\d+)\s+([A-Za-z\.\s\-\']+?)\s+(\d+)\'
        m = re.search(r'^(\d+)\s+([A-Za-z\.\'\s\-]+?)\s+(\d+)\'\s*(.*)$', line)
        if m:
            num = int(m.group(1))
            name = m.group(2).strip()
            mins = int(m.group(3))
            rest = m.group(4).strip()
            
            # Split remaining numbers
            nums = re.findall(r'\d+', rest)
            
            players.append({
                'match': match_info,
                'team': current_team,
                'shirt_num': num,
                'player_name': name,
                'minutes': mins,
                'raw_stats': rest,
                'numbers': nums
            })
            
    return players

test_pdf = os.path.join(REPORT_DIR, "1__INT-MON_MatchReport_IT.pdf")
with pdfplumber.open(test_pdf) as pdf:
    p5_text = pdf.pages[4].extract_text()
    parsed = parse_player_stats_page(p5_text, "INTER", "MONZA", "INTER 4-1 MONZA")
    print(f"Parsed {len(parsed)} players from Inter-Monza:")
    for p in parsed[:12]:
        print(f"  {p['shirt_num']:<3} {p['player_name']:<18} ({p['team']:<6}) -> Mins: {p['minutes']}' | raw: {p['raw_stats']}")
