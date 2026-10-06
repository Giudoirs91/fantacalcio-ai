import sys
import json
import os
import re

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dist_dir = os.path.join(ROOT, "dist")
calciatore_dir = os.path.join(dist_dir, "calciatore")
existing_slugs = set(os.listdir(calciatore_dir)) if os.path.exists(calciatore_dir) else set()

print(f"Cartelle esistenti in dist/calciatore: {len(existing_slugs)}")

# Scansione di TUTTI i file HTML in dist
all_broken_calciatore = []
all_broken_other = []
total_html = 0
total_links = 0

for root, dirs, files in os.walk(dist_dir):
    for f in files:
        if f.endswith(".html"):
            total_html += 1
            f_path = os.path.join(root, f)
            with open(f_path, "r", encoding="utf-8", errors="ignore") as fp:
                text = fp.read()
            
            # Cerca tutti i link tipo href="..."
            matches = re.findall(r'href=[\'"]([^\'"]+)[\'"]', text)
            for href in matches:
                if href.startswith(('http://', 'https://', 'mailto:', 'tel:', 'javascript:', '#')):
                    continue
                clean_href = href.split('#')[0].split('?')[0]
                if not clean_href:
                    continue
                total_links += 1

                # Verifica se e' un link calciatore
                calcio_m = re.search(r'calciatore/([a-zA-Z0-9_-]+)/?', clean_href)
                if calcio_m:
                    target_slug = calcio_m.group(1)
                    if target_slug not in existing_slugs:
                        all_broken_calciatore.append((os.path.relpath(f_path, dist_dir), href, target_slug))
                else:
                    # Altro link interno (pagina, css, asset)
                    target_path = os.path.normpath(os.path.join(root, clean_href))
                    if os.path.isdir(target_path):
                        target_file = os.path.join(target_path, 'index.html')
                    else:
                        target_file = target_path
                    if not os.path.exists(target_file):
                        all_broken_other.append((os.path.relpath(f_path, dist_dir), href, target_file))

unique_missing_player_slugs = sorted(list(set(b[2] for b in all_broken_calciatore)))

print(f"Scansionati {total_html} file HTML, analizzati {total_links} link interni totali.")
print(f"1. Link Calciatori Rotti: {len(all_broken_calciatore)} (corrispondenti a {len(unique_missing_player_slugs)} slug mancanti)")
print(f"2. Altri Link Rotti (pagine/risorse): {len(all_broken_other)}")

if all_broken_other:
    print("\nDettaglio altri link rotti:")
    for b in all_broken_other[:10]:
        print(f"  IN {b[0]} --> {b[1]}")

print("\nEsempi di slug calciatore mancanti (404 Not Found):")
for s in unique_missing_player_slugs[:15]:
    src = next(b[0] for b in all_broken_calciatore if b[2] == s)
    print(f"  - /calciatore/{s}/  (richiesto in {src})")
