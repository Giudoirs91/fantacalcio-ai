import re

# We will read tools/build_seo_site.py and rewrite generate_player_page to produce the EXACT 1:1 structure of player_profile.js
builder_code = '''
def compute_bonus_malus_str(v):
    if not v:
        return '-'
    if v.get('bonus_malus_str') and v['bonus_malus_str'] != '-' and 'undefined' not in str(v['bonus_malus_str']):
        return str(v['bonus_malus_str'])
    parts = []
    gf = float(v.get('gf') or 0)
    ass = float(v.get('ass') or 0)
    rp = float(v.get('rp') or 0)
    gs = float(v.get('gs') or 0)
    rs = float(v.get('rs') or 0)
    au = float(v.get('au') or 0)
    amm = float(v.get('amm') or 0)
    esp = float(v.get('esp') or 0)
    if gf > 0: parts.append(f"+{int(gf * 3)} ({int(gf)}G)")
    if ass > 0: parts.append(f"+{int(ass)} ({int(ass)}A)")
    if rp > 0: parts.append(f"+{int(rp * 3)} (Rig.Par)")
    if gs > 0: parts.append(f"-{int(gs)} ({int(gs)}GS)")
    if rs > 0: parts.append("-3 (Rig.Sbagliato)")
    if au > 0: parts.append(f"-{int(au * 2)} (Autogol)")
    if amm > 0: parts.append("-0.5 (Amm)")
    if esp > 0: parts.append("-1 (Esp)")
    if parts: return ", ".join(parts)
    if v.get('voto') is not None: return "Nessun bonus"
    return '-'

def render_mantra_quick_badges(mantra_str):
    if not mantra_str or mantra_str in ['-', 'null', 'undefined']:
        return '<span style="color:#94a3b8;font-size:12px;font-weight:600;">-</span>'
    roles = [r.strip() for r in re.split(r'[;,/ ]+', mantra_str) if r.strip()]
    if not roles:
        return '<span style="color:#94a3b8;font-size:12px;font-weight:600;">-</span>'
    return "".join([f'<span class="mantra-pill {r.lower()}">{clean_html(r)}</span>' for r in roles])

def get_match_info_for_team_and_round(team_name, round_num):
    if not CALENDAR_DATA:
        return None
    r_obj = next((r for r in CALENDAR_DATA if r.get('giornata') == round_num), None)
    if not r_obj or not r_obj.get('matches'):
        return None
    t_clean = (team_name or '').upper().strip()
    for m in r_obj['matches']:
        h_clean = (m.get('home') or '').upper().strip()
        a_clean = (m.get('away') or '').upper().strip()
        if h_clean == t_clean:
            return {
                'opponent': m.get('away'),
                'is_home': True,
                'match_str': f"{m.get('home')} vs {m.get('away')}",
                'date': r_obj.get('date', '')
            }
        if a_clean == t_clean:
            return {
                'opponent': m.get('home'),
                'is_home': False,
                'match_str': f"{m.get('away')} @ {m.get('home')}",
                'date': r_obj.get('date', '')
            }
    return None

def compute_expected_fantamedia(p):
    has2627 = bool(p.get("has_data_2627") and (p.get("presenze_2627") or 0) > 0)
    presenze = (p.get("presenze_2627") if has2627 else p.get("presenze")) or 1
    mv = float(p.get("mv_2627") if has2627 else (p.get("mv") or 6.0)) or 6.0
    real_fm = float(p.get("fm_2627") if has2627 else (p.get("fm") or mv)) or mv
    
    if p.get("xfm") is not None and p.get("delta_xfm") is not None:
        return {
            "xfm": round(float(p["xfm"]), 2),
            "realFm": round(real_fm, 2),
            "delta": round(float(p["delta_xfm"]), 2),
            "has2627": has2627
        }
    
    role = p.get("role", "C")
    if role == 'P':
        gs = float(p.get("gol_subiti_2627") if has2627 else (p.get("gs") or 0)) or 0
        cs = float(p.get("clean_sheets_2627") if has2627 else (p.get("clean_sheets_2526") or 0)) or 0
        xfm = round(mv - (gs / presenze) + (cs * 0.5 / presenze), 2)
        delta = round(real_fm - xfm, 2)
        return {"xfm": xfm, "realFm": round(real_fm, 2), "delta": delta, "has2627": has2627}
    else:
        xg = float(p.get("xg_2627") or (float(p.get("xg90_2627") or 0) * float(p.get("minuti_2627") or 90) / 90 if has2627 else (p.get("xg_2526") or 0)))
        xa = float(p.get("xa_2627") or (float(p.get("xa90_2627") or 0) * float(p.get("minuti_2627") or 90) / 90 if has2627 else (p.get("xa_2526") or 0)))
        malus = float(p.get("amm_2627") or p.get("amm") or 0) * 0.5 + float(p.get("esp_2627") or p.get("esp") or 0) * 1.0
        bonus_attesi = (xg * 3.0) + (xa * 1.0)
        xfm = round(mv + ((bonus_attesi - malus) / presenze), 2)
        delta = round(real_fm - xfm, 2)
        return {"xfm": xfm, "realFm": round(real_fm, 2), "delta": delta, "has2627": has2627}
'''

print("Helper block defined.")
