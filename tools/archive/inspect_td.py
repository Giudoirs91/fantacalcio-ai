import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('chunk_6972.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

idx = code.find('tD=')
print(code[idx:idx+2500])
