import re

with open('chunk_page.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

print("Length of chunk_page.js:", len(code))

# Search for the widget or component that renders the player stats table
idx = code.find('basic-stats')
while idx != -1:
    print("=== basic-stats context ===")
    print(code[max(0, idx-400):min(len(code), idx+600)])
    print("="*60)
    idx = code.find('basic-stats', idx+1)
