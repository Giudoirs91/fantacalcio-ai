import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/raw/odds/roma-cagl.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

scommesse = d.get('scommessaMap', {})
info_map = d.get('infoAggiuntivaMap', {})

def search_roma_markets(keywords):
    print(f"\n--- RICERCA PER: {keywords} ---")
    for s_id, s_obj in scommesse.items():
        s_desc = s_obj.get('descrizione', '').strip()
        if any(k.upper() in s_desc.upper() for k in keywords):
            for k_data in s_obj.get('infoAggiuntivaKeyDataList', []):
                item = info_map.get(k_data.get('key'))
                if not item:
                    continue
                item_desc = item.get('descrizione', '').strip()
                esiti = [(e.get('descrizione', '').strip(), (e.get('quota') or 0)/100.0) for e in item.get('esitoList', []) if e.get('stato') == 1]
                print(f"  [{s_desc} | {item_desc}] -> {esiti}")

search_roma_markets(['TIRI IN PORTA SQUADRA', 'TIRI TOTALI SQUADRA', 'ENTRAMBE LE SQUADRE ALMENO'])
search_roma_markets(['COMBO: 1X2 + U/O', 'COMBO: 1X2 + MULTIGOAL', 'MULTIGOAL'])
search_roma_markets(['CARTELLINI', 'FALLI'])
