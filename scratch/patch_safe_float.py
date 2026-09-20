import re

file_path = "tools/seo_player_template.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

safe_float_code = '''
def safe_float(val, default=0.0):
    if val is None or val == '' or val == '-' or val == 's.v.':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default
'''

if "def safe_float" not in content:
    content = safe_float_code + "\n" + content

# Replace compute_expected_fantamedia with robust version
old_compute = '''def compute_expected_fantamedia(p):
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
        return {"xfm": xfm, "realFm": round(real_fm, 2), "delta": delta, "has2627": has2627}'''

new_compute = '''def compute_expected_fantamedia(p):
    has2627 = bool(p.get("has_data_2627") and (p.get("presenze_2627") or 0) > 0)
    presenze = safe_float(p.get("presenze_2627") if has2627 else p.get("presenze"), 1.0)
    if presenze <= 0: presenze = 1.0
    mv_raw = p.get("mv_2627") if has2627 else p.get("mv")
    mv = safe_float(mv_raw, safe_float(p.get("mv"), 6.0)) or 6.0
    real_fm_raw = p.get("fm_2627") if has2627 else p.get("fm")
    real_fm = safe_float(real_fm_raw, safe_float(p.get("fm"), mv)) or mv
    
    if p.get("xfm") is not None and p.get("delta_xfm") is not None:
        return {
            "xfm": round(safe_float(p["xfm"], real_fm), 2),
            "realFm": round(real_fm, 2),
            "delta": round(safe_float(p["delta_xfm"], 0.0), 2),
            "has2627": has2627
        }
    
    role = p.get("role", "C")
    if role == 'P':
        gs = safe_float(p.get("gol_subiti_2627") if has2627 else p.get("gs"), 0.0)
        cs = safe_float(p.get("clean_sheets_2627") if has2627 else p.get("clean_sheets_2526"), 0.0)
        xfm = round(mv - (gs / presenze) + (cs * 0.5 / presenze), 2)
        delta = round(real_fm - xfm, 2)
        return {"xfm": xfm, "realFm": round(real_fm, 2), "delta": delta, "has2627": has2627}
    else:
        xg = safe_float(p.get("xg_2627") or (safe_float(p.get("xg90_2627")) * safe_float(p.get("minuti_2627"), 90) / 90.0 if has2627 else p.get("xg_2526")), 0.0)
        xa = safe_float(p.get("xa_2627") or (safe_float(p.get("xa90_2627")) * safe_float(p.get("minuti_2627"), 90) / 90.0 if has2627 else p.get("xa_2526")), 0.0)
        malus = safe_float(p.get("amm_2627") or p.get("amm"), 0.0) * 0.5 + safe_float(p.get("esp_2627") or p.get("esp"), 0.0) * 1.0
        bonus_attesi = (xg * 3.0) + (xa * 1.0)
        xfm = round(mv + ((bonus_attesi - malus) / presenze), 2)
        delta = round(real_fm - xfm, 2)
        return {"xfm": xfm, "realFm": round(real_fm, 2), "delta": delta, "has2627": has2627}'''

content = content.replace(old_compute, new_compute)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated seo_player_template.py with safe_float!")
