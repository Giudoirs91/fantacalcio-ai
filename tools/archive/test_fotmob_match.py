import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.player_matcher import clean_text, resolve_player
from src.stats_processor import load_fotmob_stats, load_quotazioni

fotmob = load_fotmob_stats()
df_quot = load_quotazioni()

print('FotMob sample names (first 10):')
for k in list(fotmob.keys())[:10]:
    print(' ', k)

print('\nTesting matching on some top players:')
test_names = ['Kean', 'Dimarco', 'Martinez L.', 'Orsolini', 'Paz N.', 'Vlahovic', 'Dybala', 'Pellegrini Lo.', 'De Ketelaere', 'Kossounou', 'Barella']

for tn in test_names:
    cn = clean_text(tn)
    res = resolve_player(cn, '', fotmob)
    matched_name = res['name'] if res else "NOT MATCHED"
    print(f"{tn:<20} -> {matched_name}")
