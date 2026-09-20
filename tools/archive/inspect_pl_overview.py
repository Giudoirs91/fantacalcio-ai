import urllib.request
import re
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = "https://www.fotmob.com/it/leagues/47/overview"
req = urllib.request.Request(url, headers=HEADERS)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8')

m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
if m:
    data = json.loads(m.group(1))
    page_props = data['props']['pageProps']
    print("PageProps keys:", list(page_props.keys()))
    if 'data' in page_props:
        print("Data keys:", list(page_props['data'].keys()))
    else:
        print("Fallback keys:", list(page_props.get('fallback', {}).keys())[:5])
