import json

# 1. Tattica
with open("config/tactical_db.json", "r", encoding="utf-8") as f:
    tactical = json.load(f)

print("=== TATTICA UDINESE ===")
udi = tactical.get("Udinese", {})
print("Allenatore:", udi.get("all"))
print("Modulo:", udi.get("modulo"))
print("Top:", udi.get("top"))
print("Rigoristi:", udi.get("rigoristi"))
print("Ballottaggi attacco/ali:")
for b in udi.get("ballottaggi", []):
    if any(p in b.get("player", "") for p in ["Lucca", "Thauvin", "Brenner", "Davis", "Bravo", "Karlstrom", "Lovric"]):
        print(f"  {b.get('player')} ({b.get('pct')}%) vs {b.get('vs')}")

print("\n=== TATTICA CAGLIARI ===")
cag = tactical.get("Cagliari", {})
print("Allenatore:", cag.get("all"))
print("Modulo:", cag.get("modulo"))
print("Top:", cag.get("top"))
print("Rigoristi:", cag.get("rigoristi"))
print("Ballottaggi attacco/ali:")
for b in cag.get("ballottaggi", []):
    if any(p in b.get("player", "") for p in ["Piccoli", "Luvumbo", "Gaetano", "Lapadula", "Marin", "Felici"]):
        print(f"  {b.get('player')} ({b.get('pct')}%) vs {b.get('vs')}")

# 2. FotMob Stats
print("\n=== STATS FOTMOB ===")
with open("data/raw/fotmob_team_stats_2026_27.json", "r", encoding="utf-8") as f:
    stats = json.load(f)

print("UDINESE:", stats.get("Udinese"))
print("CAGLIARI:", stats.get("Cagliari"))
