import re
import glob

for fname in ['chunk_page.js', 'chunk_7936.js', 'chunk_5239.js', 'chunk_6972.js']:
    try:
        with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        print(f"=== {fname} ({len(code)} bytes) ===")
        # Look for stats / api / endpoints / player stats queries
        matches = re.findall(r'https?://[^\s"\'`<>]+', code)
        for m in set(matches):
            if any(k in m.lower() for k in ['dapi', 'stats', 'statistiche', 'player', 'seriea', 'legaseriea']):
                print("  URL:", m)
        
        # Look for template strings with api or stats
        queries = re.findall(r'[`"\']([^`"\']*(?:stats|statistiche|player|giocatori|season|championship)[^`"\']*)[`"\']', code, re.IGNORECASE)
        print("  Sample queries/endpoints:")
        for q in set(queries):
            if any(k in q.lower() for k in ['/v2/', '/api/', 'statistics', 'stats', 'competitions']):
                print("    ->", q)
    except Exception as e:
        print(f"Error {fname}: {e}")
