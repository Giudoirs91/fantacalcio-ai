import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

ps = json.load(open('processed_players_master.json', encoding='utf-8'))

def get_p(name, role=None):
    clean = name.lower().strip()
    # exact
    for p in ps:
        if (not role or p['role'] == role) and p['name'].lower() == clean:
            return p
    # substring
    for p in ps:
        if (not role or p['role'] == role) and (clean in p['name'].lower() or p['name'].lower() in clean):
            return p
    return None

# Test finding players
test_names = [
    ('Martinez L.', 'A'), ('Scamacca', 'A'), ('Piccoli', 'A'), ('Kean', 'A'), ('Malen', 'A'),
    ('Douvikas', 'A'), ('Raimondo', 'A'), ('Diao', 'A'), ('Thuram', 'A'), ('Adams C.', 'A'),
    ('Nico Paz', 'C'), ('Calhanoglu', 'C'), ('Baturina', 'C'), ('Pulisic', 'C'), ('McTominay', 'C'),
    ('Barella', 'C'), ('Frattesi', 'C'), ('Bernabè', 'C'), ('Colpani', 'C'), ('Ferguson', 'C'),
    ('Dimarco', 'D'), ('Bremer', 'D'), ('Akanji', 'D'), ('Rrahmani', 'D'), ('Tavares N.', 'D'),
    ('Doig', 'D'), ('Bellanova', 'D'), ('Kalulu', 'D'), ('Molina', 'D'), ('Wesley', 'D'),
    ('Svilar', 'P'), ('Carnesecchi', 'P'), ('Meret', 'P'), ('Maignan', 'P'), ('De Gea', 'P'), ('Vicario', 'P')
]

for n, r in test_names:
    p = get_p(n, r)
    if not p:
        print(f"FAILED to find {n} ({r})")
    else:
        print(f"✓ {p['name']} ({p['role']} - {p['team']}): {p['prezzo_cons']} CR, OVR {p['ovr']}")
