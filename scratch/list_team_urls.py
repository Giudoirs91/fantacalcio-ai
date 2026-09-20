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
teams = data.get('props', {}).get('pageProps', {}).get('stats', {}).get('teams', [])

print(f"Total metrics found: {len(teams)}")
urls = []
for t in teams:
    urls.append({
        'header': t.get('header'),
        'name': t.get('name'),
        'url': t.get('fetchAllUrl')
    })
    print(f"- {t.get('header')} -> {t.get('name')} -> {t.get('fetchAllUrl')}")

with open("scratch/team_stat_urls.json", "w", encoding="utf-8") as out:
    json.dump(urls, out, indent=2)
