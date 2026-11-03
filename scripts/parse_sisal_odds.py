import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def parse_sisal(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        d = json.load(f)
    
    event_info = d.get('avvenimentoFe', {})
    desc_event = event_info.get('descrizione', 'Sconosciuto')
    print(f"\n=======================================================")
    print(f"EVENTO: {desc_event} ({filepath})")
    print(f"Data: {event_info.get('data')} {event_info.get('ora')}")
    print(f"=======================================================")
    
    scommesse = d.get('scommessaMap', {})
    info_map = d.get('infoAggiuntivaMap', {})
    
    print(f"Totale scommesse disponibili: {len(scommesse)}")
    
    # Raccogli tutti i mercati e i loro esiti
    markets = []
    for s_id, s_obj in scommesse.items():
        desc = s_obj.get('descrizione', '')
        # trova tutte le info aggiuntive legate a questa scommessa
        esiti_list = []
        for info_id in s_obj.get('infoAggiuntivaKeyList', []):
            info_item = info_map.get(str(info_id))
            if not info_item:
                continue
            param = info_item.get('parametro', '')
            desc_info = info_item.get('descrizione', '')
            for esito in info_item.get('esitoList', []):
                desc_esito = esito.get('descrizione', '')
                quota = esito.get('quota', 0) / 100.0 if esito.get('quota') else 0.0
                esiti_list.append({
                    'param': param,
                    'info_desc': desc_info,
                    'desc': desc_esito,
                    'quota': quota,
                    'stato': esito.get('stato')
                })
        markets.append({
            'id': s_id,
            'desc': desc,
            'esiti': esiti_list
        })
    return desc_event, markets

for path in ['data/raw/odds/sass-lazio.json', 'data/raw/odds/roma-cagl.json']:
    desc, mkts = parse_sisal(path)
    print(f"Campione mercati per {desc}:")
    for m in mkts[:15]:
        print(f"  - {m['desc']} ({len(m['esiti'])} esiti)")
