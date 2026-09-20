import json

# 1. Tattica
with open("config/tactical_db.json", "r", encoding="utf-8") as f:
    tactical = json.load(f)

print("=== TATTICA FIORENTINA ===")
fio = tactical.get("Fiorentina", {})
print("Modulo DB:", fio.get("modulo"), "(Nuovo all: Paolo Vanoli)")
print("Top:", fio.get("top"))
print("Rigoristi:", fio.get("rigoristi"))
print("Ballottaggi:")
for b in fio.get("ballottaggi", [])[:8]:
    print(" -", b.get("player"), b.get("pct"), "vs", b.get("vs"))

print("\n=== TATTICA NAPOLI ===")
nap = tactical.get("Napoli", {})
print("All:", nap.get("all"), "| Modulo:", nap.get("modulo"))
print("Top:", nap.get("top"))
print("Rigoristi:", nap.get("rigoristi"))
print("Ballottaggi:")
for b in nap.get("ballottaggi", [])[:8]:
    print(" -", b.get("player"), b.get("pct"), "vs", b.get("vs"))

# 2. FotMob Stats
print("\n=== STATS FOTMOB ===")
with open("data/raw/fotmob_team_stats_2026_27.json", "r", encoding="utf-8") as f:
    stats = json.load(f)

print("FIORENTINA:", stats.get("Fiorentina"))
print("NAPOLI:", stats.get("Napoli"))
