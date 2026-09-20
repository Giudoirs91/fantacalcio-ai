import urllib.request
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

req = urllib.request.Request('https://www.legaseriea.it/serie-a/statistiche/giocatori', headers=headers)
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8')

print("Searching for player names in raw HTML...")
# Check if player names like "COLOMBO", "DOUVIKAS", "LAURIENT" are in the raw HTML:
for name in ["COLOMBO", "DOUVIKAS", "LAURIENT", "SVIAR", "SVILAR", "FALCONE", "ADOPO"]:
    count = html.count(name)
    print(f"Name {name}: found {count} times")

# Let's inspect self.__next_f pushes
matches = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html)
print(f"Found {len(matches)} next_f pushes")

# Let's search inside the pushes for json strings
full_flight = ""
for m in matches:
    full_flight += m

print("Full flight length:", len(full_flight))
if "COLOMBO" in full_flight or "DOUVIKAS" in full_flight:
    print("Found players in flight payload!")

with open('flight_payload.txt', 'w', encoding='utf-8') as f:
    f.write(full_flight)
