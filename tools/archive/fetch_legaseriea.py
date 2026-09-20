import urllib.request
import json
import re

url = 'https://www.legaseriea.it/serie-a/statistiche/giocatori'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        print(f"HTML retrieved, size: {len(html)} bytes")
        
        # Check for __NEXT_DATA__
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            print("Found __NEXT_DATA__!")
            page_props = data.get('props', {}).get('pageProps', {})
            print("pageProps keys:", list(page_props.keys()))
            with open('legaseriea_next_data.json', 'w', encoding='utf-8') as f:
                json.dump(page_props, f, ensure_ascii=False, indent=2)
            print("Saved legaseriea_next_data.json")
        else:
            print("No __NEXT_DATA__ found, searching for API calls or script tags...")
            scripts = re.findall(r'<script[^>]*src="([^"]+)"', html)
            print(f"Found {len(scripts)} scripts")
            for s in scripts[:10]:
                print("Script:", s)
except Exception as e:
    print(f"Error fetching: {e}")
