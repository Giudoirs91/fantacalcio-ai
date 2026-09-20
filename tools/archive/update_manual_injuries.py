import csv
import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(ROOT_DIR, 'data', 'raw', 'giocatori_ancora_non_matchati.csv')
DB_FILE = os.path.join(ROOT_DIR, 'config', 'infortuni_storici_2025_26.json')

def run():
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        db = json.load(f)
        
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            team = row['Squadra Listone'].strip()
            name = row['Nome Listone'].strip()
            try:
                partite = int(row['Partite perse'].strip())
            except ValueError:
                partite = 0
                
            if team in db and name in db[team]:
                p = db[team][name]
                p['partite_saltate'] = partite
                p['tm_matched_name'] = name + " (Manuale)"
                p['squadra_tm_2526'] = team
                p['giornate_saltate'] = []
                
                if partite > 0:
                    p['diagnosi'] = [{
                        "motivo": "Non specificato",
                        "partite": partite,
                        "giornate": []
                    }]
                else:
                    p['diagnosi'] = []
                    
                if partite == 0:
                    p['livello_fragilita'] = "🟢 Bassa"
                elif partite <= 6:
                    p['livello_fragilita'] = "🟡 Media"
                else:
                    p['livello_fragilita'] = "🔴 Alta"
            else:
                print(f"Giocatore non trovato nel db: {name} ({team})")

    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
        
    print("Database aggiornato con successo!")

if __name__ == '__main__':
    run()
