import re
import json

with open('legaseriea.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

dapi_urls = re.findall(r'https?://dapi\.legaseriea\.it/[^\s"\'<>]+', content)
print("dapi urls found:", len(dapi_urls))
for u in sorted(set(dapi_urls))[:20]:
    print(u)

# Also let's check for any api endpoints mentioned in the js files or chunks
chunk_urls = re.findall(r'/_next/static/chunks/[^\s"\'<>]+\.js', content)
print("Chunks found:", len(chunk_urls))
for c in chunk_urls[:5]:
    print("Chunk:", c)
