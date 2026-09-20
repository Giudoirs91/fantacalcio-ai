import re

with open(r'C:\Users\dorsi\.gemini\antigravity-ide\brain\6407e6e6-e258-4577-8610-5fc007ee1b1c\.system_generated\steps\104\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Trova tutte le immagini o link di formazioni
images = re.findall(r'!\[(.*?)\]\((.*?)\)', text)
print(f"Trovate {len(images)} immagini nell'articolo:")
for alt, url in images[:25]:
    print(f"Alt: {alt} -> URL: {url}")
