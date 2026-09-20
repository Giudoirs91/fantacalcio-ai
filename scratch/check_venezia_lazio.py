import json

# 1. Tattica
with open("config/tactical_db.json", "r", encoding="utf-8") as f:
    tactical = json.load(f)

print("=== TATTICA VENEZIA ===")
ven = tactical.get("Venezia", {})
print("All:", ven.get("all"), "| Modulo:", ven.get("modulo"))
print("Top:", ven.get("top"))
print("Rigoristi:", ven.get("rigoristi"))
for b in ven.get("ballottaggi", [])[:6]:
    print(" -", b.get("player"), b.get("pct"), "vs", b.get("vs"))

print("\n=== TATTICA LAZIO ===")
laz = tactical.get("Lazio", {})
print("All:", laz.get("all"), "| Modulo:", laz.get("modulo"))
print("Top:", laz.get("top"))
print("Rigoristi:", laz.get("rigoristi"))
for b in laz.get("ballottaggi", [])[:6]:
    print(" -", b.get("player"), b.get("pct"), "vs", b.get("vs"))

# 2. FotMob Stats
print("\n=== STATS FOTMOB ===")
with open("data/raw/fotmob_team_stats_2026_27.json", "r", encoding="utf-8") as f:
    stats = json.load(f)

print("VENEZIA:", stats.get("Venezia"))
print("LAZIO:", stats.get("Lazio"))
