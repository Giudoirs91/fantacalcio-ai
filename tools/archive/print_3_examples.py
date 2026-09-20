import sys
sys.path.insert(0, '.')
from src.pipeline import run_master_pipeline

res = run_master_pipeline()
players = res[0] if isinstance(res, tuple) else res
targets = ['Dimarco', 'Paz N.', 'Baldanzi', 'Pierotti', 'Martinez L.']
for p in players:
    for t in targets:
        if t.lower() in p['name'].lower():
            msg = f"""=== {p['name']} ({p['team']}, {p['role']}) ===
  FVM: {p['fvm']}, OVR: {p['ovr']}, Prezzo: {p['prezzo_cons']} CR, Max Bid: {p['max_bid']} CR, Slot: {p['slot_fascia']}
  xG90: {p.get('xg90_2526')}, xA90: {p.get('xa90_2526')}, Rating: {p.get('rating_2526')}, Mins: {p.get('mins_2526')}
  OOP: {p.get('oop_val')}, Rigorista: {p.get('rigorista_val')}
  AI Advice: {p.get('ai_advice')}
"""
            print(msg.encode('ascii', 'ignore').decode('ascii'))
