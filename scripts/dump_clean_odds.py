import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def get_match_full(path):
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    scommesse = d.get('scommessaMap', {})
    info_map = d.get('infoAggiuntivaMap', {})
    
    odds = []
    for s_id, s_obj in scommesse.items():
        s_desc = s_obj.get('descrizione', '').strip()
        for k_data in s_obj.get('infoAggiuntivaKeyDataList', []):
            item = info_map.get(k_data.get('key'))
            if not item:
                continue
            item_desc = item.get('descrizione', '').strip()
            soglia = item.get('soglia', '')
            for es in item.get('esitoList', []):
                if es.get('stato') == 1:
                    odds.append({
                        'market': s_desc,
                        'sub': item_desc,
                        'soglia': soglia,
                        'outcome': es.get('descrizione', '').strip(),
                        'quota': (es.get('quota') or 0) / 100.0
                    })
    return odds

print("=== SASSUOLO - LAZIO: QUOTE CHIAVE ===")
sass = get_match_full('data/raw/odds/sass-lazio.json')
for o in sass:
    m = o['market']
    if m in ['1X2 ESITO FINALE', 'UNDER/OVER', 'GOAL/NOGOAL', 'DOPPIA CHANCE']:
        print(f"  [{m} - {o['sub']}] {o['outcome']} @ {o['quota']}")

print("\n=== ROMA - CAGLIARI: QUOTE CHIAVE ===")
roma = get_match_full('data/raw/odds/roma-cagl.json')
for o in roma:
    m = o['market']
    if m in ['1X2 ESITO FINALE', 'UNDER/OVER', 'GOAL/NOGOAL', 'DOPPIA CHANCE']:
        print(f"  [{m} - {o['sub']}] {o['outcome']} @ {o['quota']}")
