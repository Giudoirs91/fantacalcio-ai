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
    props = json.loads(m.group(1))['props']['pageProps']
    stats_obj = props.get('stats', {})
    print("seasonsWithLinks:", stats_obj.get('seasonsWithLinks'))
    print("seasonStatLinks:", stats_obj.get('seasonStatLinks'))
