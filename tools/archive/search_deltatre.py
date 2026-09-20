import re
import glob

for fpath in glob.glob("*.js"):
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # search for .project("seriea", "football") or similar builder calls
    matches = re.findall(r'\.project\([^)]+\)[^;{}]*', content)
    if matches:
        print(f"\n=== File: {fpath} ===")
        for m in set(matches):
            print("  Path builder:", m[:150])
    
    # search for stats/statistics endpoints
    stats_matches = re.findall(r'[\'"`](/[^\'"`]*(?:stats|player|statistic|leaderboard)[^\'"`]*)[\'"`]', content)
    if stats_matches:
        print(f"Stats matches in {fpath}:")
        for sm in set(stats_matches):
            print("   ->", sm)
