import json
from datetime import datetime

raw_injuries = [
  {"squadra": "Atalanta", "calciatore": "HIEN Isak", "motivo": "Lesione del tendine del semimembranoso della gamba sinistra", "rientro": "11/10/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Atalanta", "calciatore": "SULEMANA Kamaldeen", "motivo": "Lesione di secondo grado del legamento collaterale mediale del ginocchio sinistro", "rientro": "11/10/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Atalanta", "calciatore": "SULEMANA Ibrahim", "motivo": "Lesione di secondo grado del legamento collaterale mediale del ginocchio sinistro", "rientro": "12/10/2026", "fonte": "redazione"},
  {"squadra": "Bologna", "calciatore": "EL AZZOUZI Oussama", "motivo": "Lesione del bicipite femorale della coscia sinistra", "rientro": "24/09/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Cagliari", "calciatore": "IDRISSI Riyad", "motivo": "Intervento di ricostruzione del legamento crociato anteriore del ginocchio sinistro", "rientro": "11/10/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Como", "calciatore": "ADDAI Jayden", "motivo": "Operato per la rottura del tendine d'Achille della gamba sinistra", "rientro": "11/10/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Fiorentina", "calciatore": "PARISI Fabiano", "motivo": "Intervento di ricostruzione del legamento crociato anteriore del ginocchio destro", "rientro": "01/11/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Genoa", "calciatore": "VENTURINO Lorenzo", "motivo": "Operato al ginocchio", "rientro": "04/09/2026", "fonte": "redazione"},
  {"squadra": "Inter", "calciatore": "SPENCE Djed", "motivo": "Smaltimento conseguenze piccolo infortunio pregresso", "rientro": "02/09/2026", "fonte": "redazione"},
  {"squadra": "Juventus", "calciatore": "EKHATOR Jeff", "motivo": "Lesione di basso grado del bicipite femorale della gamba destra", "rientro": "02/11/2026", "fonte": "redazione"},
  {"squadra": "Juventus", "calciatore": "MCKENNIE Weston", "motivo": "Affaticamento muscolare", "rientro": "04/09/2026", "fonte": "redazione"},
  {"squadra": "Juventus", "calciatore": "YILDIZ Kenan", "motivo": "Infortunio al piede sinistro, possibile intervento chirurgico", "rientro": "26/11/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Lazio", "calciatore": "DELE-BASHIRU Fisayo", "motivo": "Infortunio muscolare alla coscia", "rientro": "16/09/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Lazio", "calciatore": "ISAKSEN Gustav", "motivo": "Infiammazione dell'osso pubico (pubalgia)", "rientro": "17/09/2026", "fonte": "redazione"},
  {"squadra": "Lazio", "calciatore": "MARUSIC Adam", "motivo": "Problema muscolare alla coscia (flessore/quadricipite)", "rientro": "16/09/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Lazio", "calciatore": "PATRIC", "motivo": "Indisponibilità temporanea per percorso clinico programmato", "rientro": "04/09/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Lecce", "calciatore": "BERISHA Medon", "motivo": "Lesione del tendine riflesso del retto femorale destro, operato", "rientro": "07/09/2026", "fonte": "redazione"},
  {"squadra": "Monza", "calciatore": "PESSINA Matteo", "motivo": "Operato per la lussazione della rotula del ginocchio destro", "rientro": "28/10/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Monza", "calciatore": "TOURE Idrissa", "motivo": "Fastidio articolare", "rientro": "04/09/2026", "fonte": "redazione"},
  {"squadra": "Napoli", "calciatore": "BUONGIORNO Alessandro", "motivo": "Intervento di riparazione della radice del menisco mediale", "rientro": "30/09/2026", "fonte": "Transfermarkt"},
  {"squadra": "Napoli", "calciatore": "MARIANUCCI Luca", "motivo": "Lesione di alto grado del legamento collaterale mediale del ginocchio sinistro", "rientro": "11/10/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Napoli", "calciatore": "MCTOMINAY Scott", "motivo": "Lieve aritmia benigna, intervento di correzione mediante ablazione (PFA)", "rientro": "11/10/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Parma", "calciatore": "BERNABE Adrian", "motivo": "Risentimento muscolare in fase di smaltimento", "rientro": "05/09/2026", "fonte": "redazione"},
  {"squadra": "Parma", "calciatore": "CREMASCHI Benjamín", "motivo": "Intervento al menisco laterale del ginocchio sinistro", "rientro": "04/09/2026", "fonte": "redazione"},
  {"squadra": "Parma", "calciatore": "NICOLUSSI CAVIGLIA Hans", "motivo": "Lesione di medio grado alla coscia destra", "rientro": "04/09/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Roma", "calciatore": "BAH Muhammed", "motivo": "Rottura del legamento crociato", "rientro": "02/05/2027", "fonte": "ricerca sulle testate"},
  {"squadra": "Roma", "calciatore": "PELLEGRINI Lorenzo", "motivo": "Ricaduta muscolare al retto femorale coscia destra", "rientro": "02/09/2026", "fonte": "redazione"},
  {"squadra": "Sassuolo", "calciatore": "BOLOCA Daniel", "motivo": "Artroscopia al ginocchio sinistro per pulizia meniscale", "rientro": "04/09/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Sassuolo", "calciatore": "CANDE Fali", "motivo": "Ricostruzione legamento crociato anteriore ginocchio destro", "rientro": "15/09/2026", "fonte": "Transfermarkt"},
  {"squadra": "Sassuolo", "calciatore": "KONE Ismaël", "motivo": "Intervento di riduzione frattura gamba sinistra", "rientro": "17/01/2027", "fonte": "ricerca sulle testate"},
  {"squadra": "Sassuolo", "calciatore": "PIERAGNOLO Edoardo", "motivo": "Ricostruzione legamento crociato anteriore ginocchio destro", "rientro": "04/09/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Torino", "calciatore": "CASADEI Cesare", "motivo": "Affaticamento muscolare", "rientro": "03/09/2026", "fonte": "redazione"},
  {"squadra": "Torino", "calciatore": "ISRAEL Franco", "motivo": "Infortunio alla spalla", "rientro": "04/12/2026", "fonte": "Transfermarkt"},
  {"squadra": "Torino", "calciatore": "PELLEGRI Pietro", "motivo": "Rottura del legamento crociato del ginocchio", "rientro": "05/09/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Udinese", "calciatore": "PALMA Matteo", "motivo": "Fastidio muscolare alla coscia", "rientro": "22/09/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Udinese", "calciatore": "ZANIOLO Nicolò", "motivo": "Sospetto stiramento muscolare coscia", "rientro": "01/10/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Udinese", "calciatore": "ZANOLI Alessandro", "motivo": "Intervento per lesione legamento crociato anteriore", "rientro": "11/09/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Venezia", "calciatore": "ADORANTE Andrea", "motivo": "Operato per problema alla schiena", "rientro": "17/10/2026", "fonte": "ricerca sulle testate"},
  {"squadra": "Venezia", "calciatore": "MORENO Matías", "motivo": "Problemi muscolari in fase di recupero", "rientro": "04/09/2026", "fonte": "redazione"},
  {"squadra": "Venezia", "calciatore": "SVERKO Marin", "motivo": "Infortunio alle anche", "rientro": "17/10/2026", "fonte": "ricerca sulle testate"}
]

# Load master players to match exact names
with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

# Cutoff for orange vs red:
# Red (lunga degenza): rientro >= 10/10/2026 or grave (crociato, tendine d'achille, frattura, spalla a dicembre, 2027)
# Orange (prossimo al rientro / breve): rientro entro fine settembre / inizio ottobre (<= 05/10/2026) e stop breve

clean_injuries = []
for item in raw_injuries:
    # Match player
    raw_name = item['calciatore']
    parts = raw_name.split()
    matched = None
    for p in players:
        p_name_l = p['name'].lower()
        p_team_l = p['team'].lower()
        item_team_l = item['squadra'].lower()
        
        # Exact team match
        if item_team_l in p_team_l or p_team_l in item_team_l:
            # Check if any full token matches (e.g. "Pellegri" == "Pellegri")
            p_tokens = p_name_l.split()
            item_tokens = [t.lower() for t in parts]
            if any(it in p_tokens for it in item_tokens if len(it) > 2):
                matched = p
                break
            elif any(p_tok == it for p_tok in p_tokens for it in item_tokens if len(it) > 2):
                matched = p
                break
    
    if not matched:
        # Cross-team fallback only on full exact word match
        for p in players:
            p_tokens = p['name'].lower().split()
            item_tokens = [t.lower() for t in parts]
            if any(it in p_tokens and len(it) >= 4 for it in item_tokens):
                matched = p
                break

    player_name = matched['name'] if matched else parts[0].capitalize()
    player_id = matched['id'] if matched else None
    team_name = matched['team'] if matched else item['squadra']
    
    # Classify severity
    r_date_str = item['rientro']
    try:
        r_date = datetime.strptime(r_date_str, "%d/%m/%Y")
        # If date is in 2027 or >= 10 October 2026 or grave diagnosis -> RED (lunga degenza)
        is_grave = any(kw in item['motivo'].lower() for kw in ['crociato', 'tendine d\'achille', 'frattura', 'ablazione', 'lussazione rotula', 'alto grado', '2027'])
        if r_date > datetime(2026, 10, 5) or is_grave:
            severity = "red"
            tipo_stop = "Lunga Degenza"
        else:
            severity = "orange"
            tipo_stop = "Prossimo al Rientro"
    except Exception as e:
        severity = "orange"
        tipo_stop = "In Valutazione"
        
    clean_injuries.append({
        'player': player_name,
        'player_id': player_id,
        'team': team_name,
        'motivo': item['motivo'],
        'rientro': item['rientro'],
        'severity': severity, # 'orange' or 'red'
        'tipo_stop': tipo_stop,
        'fonte': item['fonte']
    })

# Save to config/injuries.json
with open('config/injuries.json', 'w', encoding='utf-8') as f:
    json.dump(clean_injuries, f, indent=2, ensure_ascii=False)

print(f"Salvato config/injuries.json con esattamente {len(clean_injuries)} infortuni ufficiali da Fantacalcio-Online:")
red_count = sum(1 for x in clean_injuries if x['severity'] == 'red')
orange_count = sum(1 for x in clean_injuries if x['severity'] == 'orange')
print(f"[RED] Lunga Degenza (Croce Rossa): {red_count}")
print(f"[ORANGE] Prossimo al Rientro (Croce Arancione): {orange_count}")
for x in clean_injuries[:10]:
    print(f"  [{x['severity'].upper():6}] {x['player']} ({x['team']}): {x['motivo']} | Rientro: {x['rientro']}")
