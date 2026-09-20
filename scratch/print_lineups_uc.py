import json

with open("config/tactical_db.json", "r", encoding="utf-8") as f:
    tactical = json.load(f)

print("UDINESE:")
u = tactical.get("Udinese", {})
print("All:", u.get("all"), "Modulo:", u.get("modulo"))
for b in u.get("ballottaggi", []):
    print(" -", b.get("player"), b.get("pct"), "vs", b.get("vs"))

print("\nCAGLIARI:")
c = tactical.get("Cagliari", {})
print("All:", c.get("all"), "Modulo:", c.get("modulo"))
for b in c.get("ballottaggi", []):
    print(" -", b.get("player"), b.get("pct"), "vs", b.get("vs"))
