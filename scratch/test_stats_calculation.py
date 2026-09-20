import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

ps = json.load(open('data/processed/processed_players_master.json', encoding='utf-8'))

for p in ps:
    voti = p.get('voti_dettaglio_2627', [])
    tot_bonus = 0.0
    tot_malus = 0.0
    gf = 0
    gs = 0
    ass = 0
    amm = 0
    esp = 0
    rs = 0
    for v in voti:
        if v.get('voto') is not None:
            gf += v.get('gf', 0)
            gs += v.get('gs', 0)
            ass += v.get('ass', 0)
            amm += v.get('amm', 0)
            esp += v.get('esp', 0)
            rs += v.get('rs', 0)
            b = v.get('gf', 0) * 3 + v.get('ass', 0) * 1 + v.get('rp', 0) * 3
            m = v.get('gs', 0) * 1 + v.get('amm', 0) * 0.5 + v.get('esp', 0) * 1 + v.get('au', 0) * 2 + v.get('rs', 0) * 3
            tot_bonus += b
            tot_malus += m
    p['tot_bonus_2627'] = tot_bonus
    p['tot_malus_2627'] = tot_malus
    p['tot_gf_2627'] = gf
    p['tot_gs_2627'] = gs
    p['tot_ass_2627'] = ass
    p['tot_amm_2627'] = amm
    p['tot_esp_2627'] = esp

print("=== TOP GOL ===")
for p in sorted(ps, key=lambda x: x.get('tot_gf_2627', 0), reverse=True)[:8]:
    print(f"  {p['name']} ({p['role']} - {p['team']}): {p.get('tot_gf_2627')} Gol")

print("\n=== TOP ASSIST ===")
for p in sorted(ps, key=lambda x: x.get('tot_ass_2627', 0), reverse=True)[:8]:
    print(f"  {p['name']} ({p['role']} - {p['team']}): {p.get('tot_ass_2627')} Assist")

print("\n=== TOP xG ===")
for p in sorted(ps, key=lambda x: x.get('xg_2627') or 0, reverse=True)[:8]:
    print(f"  {p['name']} ({p['role']} - {p['team']}): {p.get('xg_2627')} xG")

print("\n=== TOP xA ===")
for p in sorted(ps, key=lambda x: x.get('xa_2627') or 0, reverse=True)[:8]:
    print(f"  {p['name']} ({p['role']} - {p['team']}): {p.get('xa_2627')} xA")

print("\n=== GOL SUBITI PORTIERI ===")
gks = [p for p in ps if p['role'] == 'P']
for p in sorted(gks, key=lambda x: x.get('tot_gs_2627', 0), reverse=True)[:8]:
    print(f"  {p['name']} ({p['team']}): {p.get('tot_gs_2627')} Gol Subiti (CS: {p.get('clean_sheets_2627', 0)})")

print("\n=== TOP BONUS ===")
for p in sorted(ps, key=lambda x: x.get('tot_bonus_2627', 0), reverse=True)[:8]:
    print(f"  {p['name']} ({p['role']} - {p['team']}): +{p.get('tot_bonus_2627')} Bonus")

print("\n=== TOP MALUS ===")
for p in sorted(ps, key=lambda x: x.get('tot_malus_2627', 0), reverse=True)[:8]:
    print(f"  {p['name']} ({p['role']} - {p['team']}): -{p.get('tot_malus_2627')} Malus")

print("\n=== TOP CARTELLINI GIALLI ===")
for p in sorted(ps, key=lambda x: x.get('tot_amm_2627', 0), reverse=True)[:8]:
    print(f"  {p['name']} ({p['role']} - {p['team']}): {p.get('tot_amm_2627')} Amm")

print("\n=== TOP FANTAMEDIA (min 3 gare) ===")
voted_3 = [p for p in ps if p.get('presenze_2627', 0) >= 3 and p.get('fm_2627')]
for p in sorted(voted_3, key=lambda x: x.get('fm_2627', 0), reverse=True)[:8]:
    print(f"  {p['name']} ({p['role']} - {p['team']}): FM {p.get('fm_2627')} ({p.get('presenze_2627')} gare)")

print("\n=== TOP MEDIA VOTO PURA (min 3 gare) ===")
for p in sorted(voted_3, key=lambda x: x.get('mv_2627', 0), reverse=True)[:8]:
    print(f"  {p['name']} ({p['role']} - {p['team']}): MV {p.get('mv_2627')} ({p.get('presenze_2627')} gare)")
