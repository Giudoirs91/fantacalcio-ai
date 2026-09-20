import os
import json
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_INJ_2526 = os.path.join(ROOT_DIR, "config", "infortuni_storici_2025_26.json")
SRC_INJ_CURRENT = os.path.join(ROOT_DIR, "config", "injuries.json")
OUT_INJ_HIST = os.path.join(ROOT_DIR, "config", "injuries_history.json")

def classify_injury_type(motivo):
    m = (motivo or '').lower()
    if any(k in m for k in ['crociato', 'collaterale', 'menisco', 'legamento', 'caviglia', 'ginocchio', 'spalla', 'tendine', 'distorsione']):
        return 'articolare'
    if any(k in m for k in ['bicipite', 'femorale', 'flessori', 'coscia', 'polpaccio', 'adduttore', 'stiramento', 'lesione', 'strappo', 'risentimento', 'muscol']):
        return 'muscolare'
    if any(k in m for k in ['frattura', 'trauma', 'scontro', 'lussazione', 'contusione', 'ematoma']):
        return 'traumatico'
    if any(k in m for k in ['operat', 'intervento', 'chirurg']):
        return 'chirurgico'
    return 'medico'

def estimate_days_out(motivo, partite):
    tipo = classify_injury_type(motivo)
    if 'crociato' in motivo.lower():
        return max(150, partite * 14)
    if tipo == 'chirurgico':
        return max(60, partite * 10)
    if tipo == 'muscolare':
        return max(14, partite * 7)
    if tipo == 'articolare':
        return max(21, partite * 8)
    return max(5, partite * 6)

def calculate_fragility_index(partite_tot, recidive, current_injury, has_cruciate):
    score = 5.0 # Base
    score += min(45.0, partite_tot * 4.5)
    score += min(25.0, recidive * 12.0)
    if current_injury:
        score += 15.0
    if has_cruciate:
        score += 20.0
    
    score = min(100.0, max(0.0, score))
    
    if score <= 18:
        tier = 'ROCCIA'
        label = '🟢 Roccia (Massima Affidabilità)'
        badge = 'roccia'
    elif score <= 38:
        tier = 'STABILE'
        label = '🟢 Stabile (Fisiologico)'
        badge = 'stabile'
    elif score <= 62:
        tier = 'ATTENZIONE'
        label = '🟡 Attenzione (Soggetto a Stop)'
        badge = 'attenzione'
    elif score <= 82:
        tier = 'FRAGILE'
        label = '🔴 Fragile (Rischio Elevato)'
        badge = 'fragile'
    else:
        tier = 'CRISTALLO'
        label = '🚨 Cristallo (Altissimo Rischio)'
        badge = 'cristallo'
        
    return round(score, 1), tier, label, badge

def generate_medical_advice(tier, partite_tot, current_inj, recidive):
    if tier == 'ROCCIA':
        return "Calciatore integro e solido. Nessun problema muscolare ricorrente negli ultimi 24 mesi: affidabilità fisica massima."
    if tier == 'STABILE':
        return f"Storico fisico nella media ({partite_tot} partite perse). Gestibile normalmente senza particolari accoppiamenti."
    if tier == 'ATTENZIONE':
        return f"Attenzione: ha registrato {partite_tot} gare saltate e qualche affaticamento muscolare. Consigliata copertura economica in panchina."
    if tier == 'FRAGILE':
        rec_txt = f" con {recidive} ricadute muscolari" if recidive > 0 else ""
        return f"Profilo a rischio elevato: {partite_tot} partite saltate{rec_txt}. Fondamentale acquistare la sua riserva/coppia d'asta."
    return "Altissimo rischio infortuni o lungo degenza in corso. Prezzo d'asta da svalutare fortemente e obbligo assoluto di copertura."

def build_injuries_history_database():
    hist_db = {}
    
    # 1. Carica infortuni 2025/26
    raw_2526 = {}
    if os.path.exists(SRC_INJ_2526):
        with open(SRC_INJ_2526, 'r', encoding='utf-8') as f:
            raw_2526 = json.load(f)
            
    # 2. Carica infortuni attuali 2026/27
    raw_current = []
    if os.path.exists(SRC_INJ_CURRENT):
        with open(SRC_INJ_CURRENT, 'r', encoding='utf-8') as f:
            raw_current = json.load(f)
            
    current_map = {}
    for item in raw_current:
        p_name = item.get('player', '')
        if p_name:
            current_map[p_name.lower()] = item

    for team, players in raw_2526.items():
        if team not in hist_db:
            hist_db[team] = {}
            
        for name, pdata in players.items():
            cronistoria = []
            muscle_count = 0
            has_cruciate = False
            tot_days = 0
            tot_matches_2526 = pdata.get('partite_saltate', 0)
            
            for diag in pdata.get('diagnosi', []):
                mot = diag.get('motivo', 'Infortunio non specificato')
                pts = diag.get('partite', 1)
                tipo = classify_injury_type(mot)
                days = estimate_days_out(mot, pts)
                tot_days += days
                
                if tipo == 'muscolare':
                    muscle_count += 1
                if 'crociato' in mot.lower():
                    has_cruciate = True
                    
                cronistoria.append({
                    'stagione': '2025/26',
                    'motivo': mot,
                    'partite_perse': pts,
                    'giorni_stop': days,
                    'tipo': tipo,
                    'giornate': diag.get('giornate', [])
                })
                
            # Verifica se c'è un infortunio in corso per 2026/27
            cur_inj = None
            for c_k, c_v in current_map.items():
                if name.lower() in c_k or c_k in name.lower():
                    cur_inj = c_v
                    break
                    
            if cur_inj:
                mot_cur = cur_inj.get('motivo', 'Infortunio')
                tipo_cur = classify_injury_type(mot_cur)
                days_cur = 30 if cur_inj.get('severity') == 'orange' else 180
                tot_days += days_cur
                cronistoria.append({
                    'stagione': '2026/27',
                    'motivo': mot_cur,
                    'partite_perse': 3 if cur_inj.get('severity') == 'orange' else 15,
                    'giorni_stop': days_cur,
                    'tipo': tipo_cur,
                    'rientro_previsto': cur_inj.get('rientro', 'In corso'),
                    'in_corso': True
                })
                
            recidive = max(0, muscle_count - 1)
            tot_matches = tot_matches_2526 + (3 if cur_inj else 0)
            
            score, tier, label, badge = calculate_fragility_index(
                tot_matches, recidive, bool(cur_inj), has_cruciate
            )
            
            disponibilita = max(10, min(100, round(((38 - tot_matches) / 38.0) * 100, 1)))
            advice = generate_medical_advice(tier, tot_matches, bool(cur_inj), recidive)
            
            hist_db[team][name] = {
                'id': pdata.get('id'),
                'name': name,
                'team': team,
                'ruolo': pdata.get('ruolo', 'C'),
                'partite_saltate_totali': tot_matches,
                'partite_saltate_2025_26': tot_matches_2526,
                'giorni_stop_totali': tot_days,
                'disponibilita_pct': disponibilita,
                'recidive_muscolari': recidive,
                'indice_fragilita_score': score,
                'livello_fragilita': tier,
                'fragility_label': label,
                'fragility_badge': badge,
                'consiglio_medico_ai': advice,
                'infortunio_attivo': bool(cur_inj),
                'cronistoria_infortuni': cronistoria
            }
            
    os.makedirs(os.path.dirname(OUT_INJ_HIST), exist_ok=True)
    with open(OUT_INJ_HIST, 'w', encoding='utf-8') as f:
        json.dump(hist_db, f, ensure_ascii=False, indent=2)
        
    print(f"-> [InjuriesEngine] Database storico infortuni generato con successo in: {OUT_INJ_HIST}")
    return hist_db

if __name__ == '__main__':
    build_injuries_history_database()
