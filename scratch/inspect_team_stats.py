import json

path = r"C:\Users\dorsi\.gemini\antigravity-ide\brain\bfc35dd4-8f66-493d-85a6-5ee5ab438d70\.system_generated\steps\435\content.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

idx1 = text.find('"__NEXT_DATA__"')
s = text[idx1:]
idx_start = s.find('>') + 1
idx_end = s.find('</script>')
raw_json = s[idx_start:idx_end]
data = json.loads(raw_json)
page_props = data.get('props', {}).get('pageProps', {})
stats = page_props.get('stats', {})
teams = stats.get('teams', [])
print(f"teams type: {type(teams)}, len: {len(teams)}")
for cat in teams:
    print(f"\n=== CATEGORY: {cat.get('header')} ===")
    for item in cat.get('items', []):
        title = item.get('title')
        key = item.get('key')
        top = item.get('topThree', [])
        top_str = ", ".join([f"{t.get('name')}: {t.get('statValue')}" for t in top[:2]])
        print(f"  - {title} (key: {key}) -> Top: {top_str}")
