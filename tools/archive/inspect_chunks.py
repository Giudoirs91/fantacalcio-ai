import re
import urllib.request

with open('legaseriea.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

chunk_urls = re.findall(r'/_next/static/chunks/[^\s"\'<>]+\.js', content)
print("Chunks found:", len(chunk_urls))

for chunk_path in set(chunk_urls):
    full_url = "https://www.legaseriea.it" + chunk_path
    try:
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            js_code = resp.read().decode('utf-8')
            if 'stats' in js_code.lower() or 'statistiche' in js_code.lower() or 'dapi.legaseriea.it' in js_code:
                # Find all API routes in this chunk
                api_routes = re.findall(r'https?://[^\s"\'`<>]+', js_code)
                endpoints = re.findall(r'[\'"`](/api/[^\'"`]+|/v2/[^\'"`]+)[\'"`]', js_code)
                print(f"\n--- Chunk: {chunk_path} ({len(js_code)} bytes) ---")
                for ep in set(endpoints):
                    print("  Endpoint:", ep)
                for ar in set(api_routes):
                    if 'api' in ar or 'stats' in ar or 'dapi' in ar:
                        print("  Full API URL:", ar)
    except Exception as e:
        pass
