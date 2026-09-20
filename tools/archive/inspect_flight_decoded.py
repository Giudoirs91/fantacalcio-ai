import re
import json

with open('legaseriea.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Let's search for JSON structures inside self.__next_f.push
pushes = re.findall(r'self\.__next_f\.push\(\[1,"(.*)"\]\)', html)
print(f"Found {len(pushes)} pushes")

# Decode string escapes in pushes
decoded_text = ""
for p in pushes:
    # replace escaped quotes and newlines
    p_clean = p.replace('\\"', '"').replace('\\\\', '\\').replace('\\n', '\n')
    decoded_text += p_clean

print(f"Decoded flight text length: {len(decoded_text)}")

# Let's look for player names or stat objects
print("Searching for 'COLOMBO' or 'DOUVIKAS' in decoded text...")
for name in ["COLOMBO", "DOUVIKAS", "LAURIENT", "ADOPO", "NELSSON", "FALCONE", "SVILAR", "BUTEZ", "CAPRILE"]:
    print(f"Name {name}: found {decoded_text.count(name)} times")

if "COLOMBO" in decoded_text:
    idx = decoded_text.find("COLOMBO")
    print("Context around COLOMBO:\n", decoded_text[max(0, idx-300):min(len(decoded_text), idx+600)])
