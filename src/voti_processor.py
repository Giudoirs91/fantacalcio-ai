import os
import re
import glob
import pandas as pd
import numpy as np
from .player_matcher import clean_text

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def clean_voto(val):
    if pd.isna(val) or val is None:
        return None
    s = str(val).replace('*', '').replace(',', '.').strip()
    if s.lower() in ['s.v.', 'sv', '-', '']:
        return None
    try:
        return float(s)
    except Exception:
        return None

def load_voti_2026_27():
    """
    Scansiona la cartella data/raw/voti 26-27/ e carica tutti i file Excel ufficiali di giornata.
    Aggrega Media Voto, FantaMedia, partite a voto e storico voti per ciascun calciatore.
    """
    voti_dir = os.path.join(ROOT_DIR, "data", "raw", "voti 26-27")
    if not os.path.exists(voti_dir):
        voti_dir = "data/raw/voti 26-27"
        
    pattern = os.path.join(voti_dir, "Voti_Fantacalcio_Stagione_2026_27_Giornata_*.xlsx")
    files = sorted(glob.glob(pattern))
    
    if not files:
        print("[VotiProcessor] Nessun file voti 2026/27 trovato.")
        return {}
        
    player_voti = {}

    for filepath in files:
        m = re.search(r'Giornata_(\d+)', filepath)
        giornata = int(m.group(1)) if m else 1
        
        try:
            xl = pd.ExcelFile(filepath)
        except Exception as e:
            print(f"[VotiProcessor] Errore apertura {filepath}: {e}")
            continue

        sheet_to_use = 'Fantacalcio' if 'Fantacalcio' in xl.sheet_names else xl.sheet_names[0]
        
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_to_use, skiprows=5)
        except Exception as e:
            print(f"[VotiProcessor] Errore lettura sheet {sheet_to_use} in {filepath}: {e}")
            continue
            
        df = df[pd.to_numeric(df['Cod.'], errors='coerce').notna()].copy()
        
        for _, row in df.iterrows():
            try:
                cod = int(row['Cod.'])
                nome = str(row['Nome']).strip()
                ruolo = str(row['Ruolo']).strip()
                voto_puro = clean_voto(row.get('Voto'))
                
                gf = float(row.get('Gf', 0) or 0)
                gs = float(row.get('Gs', 0) or 0)
                rp = float(row.get('Rp', 0) or 0)
                rs = float(row.get('Rs', 0) or 0)
                rf = float(row.get('Rf', 0) or 0)
                au = float(row.get('Au', 0) or 0)
                amm = float(row.get('Amm', 0) or 0)
                esp = float(row.get('Esp', 0) or 0)
                ass = float(row.get('Ass', 0) or 0)
                
                bonus_malus = (gf * 3.0) - (gs * 1.0) + (rp * 3.0) - (rs * 3.0) - (au * 2.0) - (amm * 0.5) - (esp * 1.0) + (ass * 1.0)
                fanta_voto = round(voto_puro + bonus_malus, 2) if voto_puro is not None else None
                
                clean_n = clean_text(nome)
                # Aggrega SOLO per cod numerico: gli alias nome vengono creati alla fine
                primary_key = f"cod_{cod}"
                
                bm_parts = []
                if gf > 0: bm_parts.append(f"+{int(gf*3)} ({int(gf)}G)")
                if ass > 0: bm_parts.append(f"+{int(ass)} ({int(ass)}A)")
                if rp > 0: bm_parts.append(f"+{int(rp*3)} (Rig.Par)")
                if gs > 0: bm_parts.append(f"-{int(gs)} ({int(gs)}GS)")
                if rs > 0: bm_parts.append(f"-3 (Rig.Sbagliato)")
                if au > 0: bm_parts.append(f"-{int(au*2)} (Autogol)")
                if amm > 0: bm_parts.append(f"-0.5 (Amm)")
                if esp > 0: bm_parts.append(f"-1 (Esp)")
                bm_str = ", ".join(bm_parts) if bm_parts else ("Nessun bonus" if voto_puro is not None else "-")

                if primary_key not in player_voti:
                    player_voti[primary_key] = {
                        'cod': cod,
                        'nome': nome,
                        'clean_n': clean_n,  # salvato per creare l'alias alla fine
                        'ruolo': ruolo,
                        'voti_puri': [],
                        'fanta_voti': [],
                        'giornate_dettaglio': []
                    }
                
                record = player_voti[primary_key]
                
                record['giornate_dettaglio'].append({
                    'giornata': giornata,
                    'voto': voto_puro,
                    'fantavoto': fanta_voto,
                    'gf': gf,
                    'gs': gs,
                    'rp': rp,
                    'rs': rs,
                    'rf': rf,
                    'au': au,
                    'ass': ass,
                    'amm': amm,
                    'esp': esp,
                    'bonus_malus_str': bm_str
                })
                
                if voto_puro is not None:
                    record['voti_puri'].append(voto_puro)
                if fanta_voto is not None:
                    record['fanta_voti'].append(fanta_voto)
                    
            except Exception:
                continue

    summary_lookup = {}
    for k, data in player_voti.items():
        v_list = data['voti_puri']
        fv_list = data['fanta_voti']
        
        mv = round(float(np.mean(v_list)), 2) if v_list else 0.0
        fm = round(float(np.mean(fv_list)), 2) if fv_list else 0.0

        tot_b = 0.0
        tot_m = 0.0
        for g in data['giornate_dettaglio']:
            tot_b += (g.get('gf', 0) * 3.0) + (g.get('ass', 0) * 1.0) + (g.get('rp', 0) * 3.0)
            tot_m += (g.get('gs', 0) * 1.0) + (g.get('amm', 0) * 0.5) + (g.get('esp', 0) * 1.0) + (g.get('au', 0) * 2.0) + (g.get('rs', 0) * 3.0)
        
        entry = {
            'cod': data['cod'],
            'nome': data['nome'],
            'ruolo': data['ruolo'],
            'partite_a_voto': len(v_list),
            'media_voto_2627': mv,
            'fantamedia_2627': fm,
            'tot_bonus_2627': round(tot_b, 2),
            'tot_malus_2627': round(tot_m, 2),
            'voti_dettaglio': sorted(data['giornate_dettaglio'], key=lambda x: x['giornata'])
        }
        # Chiave primaria (cod_XXX)
        summary_lookup[k] = entry
        # Alias per nome pulito: punta allo stesso oggetto per coerenza
        clean_alias = data.get('clean_n', '')
        if clean_alias and clean_alias not in summary_lookup:
            summary_lookup[clean_alias] = entry

    print(f"[VotiProcessor] Aggregati voti 2026/27 ({len(files)} giornate caricate, {len(summary_lookup)} chiavi indicizzate).")
    return summary_lookup
