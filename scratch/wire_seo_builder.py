import os

script_path = "tools/build_seo_site.py"
with open(script_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add calendar path near top
top_marker = 'DASHBOARD_HTML_PATH = os.path.join(ROOT_DIR, "Dashboard_Fanta_1000.html")'
cal_block = '''DASHBOARD_HTML_PATH = os.path.join(ROOT_DIR, "Dashboard_Fanta_1000.html")
CALENDAR_PATH = os.path.join(ROOT_DIR, "config", "calendario_serie_a_2026_27.json")
CALENDAR_DATA = []
if os.path.exists(CALENDAR_PATH):
    try:
        with open(CALENDAR_PATH, "r", encoding="utf-8") as f:
            CALENDAR_DATA = json.load(f)
    except Exception as e:
        print(f"Warning loading calendar: {e}")
'''
if top_marker in content and "CALENDAR_DATA" not in content:
    content = content.replace(top_marker, cal_block, 1)

# 2. Replace generate_player_page with import
start_str = "def generate_player_page(player, injuries_db, tactical_db):"
end_str = "def generate_injuries_pillar(players, injuries_db):"

idx_start = content.find(start_str)
idx_end = content.find(end_str)

if idx_start != -1 and idx_end != -1:
    content = content[:idx_start] + "from tools.seo_player_template import generate_player_page\n\n" + content[idx_end:]
    print("generate_player_page replaced with import from tools.seo_player_template")
else:
    print(f"ERROR locating generate_player_page: {idx_start}, {idx_end}")

# 3. Update call in build_all
old_call = "slug, p_html = generate_player_page(p, injuries_db, tactical_db)"
new_call = "slug, p_html = generate_player_page(p, injuries_db, tactical_db, CALENDAR_DATA, BASE_URL)"

if old_call in content:
    content = content.replace(old_call, new_call, 1)
    print("build_all call updated with calendar and base_url")
else:
    print("Notice: old_call not found (already updated?)")

with open(script_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: tools/build_seo_site.py successfully wired to tools/seo_player_template.py!")
