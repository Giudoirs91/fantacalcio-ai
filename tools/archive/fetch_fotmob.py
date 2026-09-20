import urllib.request
import re
import json

url = 'https://www.fotmob.com/it/leagues/55/stats/season/27044/players/expected_goals'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8')
    print(f'HTML length: {len(html)}')

pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
m = re.search(pattern, html)
if m:
    data = json.loads(m.group(1))
    print('Found __NEXT_DATA__!')
    page_props = data.get('props', {}).get('pageProps', {})
    print('pageProps keys:', list(page_props.keys()))
    
    data_prop = page_props.get('data', {})
    print('data_prop keys:', list(data_prop.keys()) if isinstance(data_prop, dict) else type(data_prop))
    if isinstance(data_prop, dict):
        for k, v in data_prop.items():
            print(f"  key: {k} -> {type(v)} (len: {len(v) if hasattr(v, '__len__') else 'N/A'})")
            if isinstance(v, dict):
                print(f"    subkeys: {list(v.keys())[:10]}")
            elif isinstance(v, list) and len(v) > 0:
                print(f"    sample 0: {v[0] if not isinstance(v[0], dict) else list(v[0].keys())[:10]}")
else:
    print('No __NEXT_DATA__ found')
