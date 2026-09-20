import json

for name, path in [('Monza - Sassuolo', 'data/raw/odds/36381-1650.json'), ('Bologna - Torino', 'data/raw/odds/bolognatorino.json')]:
    print('=== ' + name + ' ===')
    d = json.load(open(path, encoding='utf-8'))
    info = d.get('infoAggiuntivaMap', {})
    for v in info.values():
        desc = (v.get('descrizione') or '').strip()
        if 'SQUADRA' in desc and 'TIRI IN PORTA IN ENTRAMBI' in desc:
            es = [f"{e.get('descrizione')} @ {e.get('quota')/100:.2f}" for e in v.get('esitoList', []) if e.get('descrizione') == 'SI']
            print(desc, ':', es)
        if desc.upper() in ['1X2 FALLI COMMESSI INC.TS', '1X2 TIRI IN PORTA', 'ARBITRO CONSULTA MONITOR VAR INCL. T.S.', 'CORNER PRIMI 10 MINUTI', 'ALMENO 4 CORNER IN ENTRAMBI I TEMPI']:
            es = [f"{e.get('descrizione')} @ {e.get('quota')/100:.2f}" for e in v.get('esitoList', [])]
            print(desc, ':', es)
