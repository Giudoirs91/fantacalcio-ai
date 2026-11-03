import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def extract_key_odds(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    
    scommesse = d.get('scommessaMap', {})
    info_map = d.get('infoAggiuntivaMap', {})
    
    results = {}
    for s_id, s_obj in scommesse.items():
        s_desc = s_obj.get('descrizione', '')
        for k_data in s_obj.get('infoAggiuntivaKeyDataList', []):
            info_key = k_data.get('key')
            info_item = info_map.get(info_key)
            if not info_item:
                continue
            item_desc = info_item.get('descrizione', '')
            soglia = info_item.get('soglia', '')
            for esito in info_item.get('esitoList', []):
                e_desc = esito.get('descrizione', '')
                q = (esito.get('quota') or 0) / 100.0
                if esito.get('stato') == 1 and q > 1.0:
                    k = f"{s_desc} | {item_desc}"
                    if k not in results:
                        results[k] = []
                    results[k].append((e_desc, q))
    return results

print("=== ODDS HIGHLIGHTS: SASSUOLO - LAZIO ===")
sass_odds = extract_key_odds('data/raw/odds/sass-lazio.json')
for cat, lst in sass_odds.items():
    if any(term in cat.upper() for term in ['1X2 ESITO FINALE', 'UNDER / OVER', 'GOAL / NO GOAL', 'ENTRAMBE LE SQUADRE ALMENO', 'DUO', 'FALLI', 'CARTELLIN']):
        # filter interesting
        for e, q in lst:
            if 'U/O 2.5' in cat or 'U/O 1.5' in cat or '1X2' in cat or 'GOAL / NO GOAL' in cat or 'DUO' in cat or 'FALLI' in cat:
                if q <= 3.50 and q >= 1.25:
                    print(f"  {cat} -> {e} @ {q:.2f}")

print("\n=== ODDS HIGHLIGHTS: ROMA - CAGLIARI ===")
roma_odds = extract_key_odds('data/raw/odds/roma-cagl.json')
for cat, lst in roma_odds.items():
    if any(term in cat.upper() for term in ['1X2 ESITO FINALE', 'UNDER / OVER', 'GOAL / NO GOAL', 'ENTRAMBE LE SQUADRE ALMENO', 'DUO', 'FALLI', 'CARTELLIN']):
        for e, q in lst:
            if 'U/O 2.5' in cat or 'U/O 1.5' in cat or '1X2' in cat or 'GOAL / NO GOAL' in cat or 'DUO' in cat or 'FALLI' in cat:
                if q <= 3.50 and q >= 1.25:
                    print(f"  {cat} -> {e} @ {q:.2f}")
