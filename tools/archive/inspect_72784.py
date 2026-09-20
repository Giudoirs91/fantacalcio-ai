with open('chunk_7936.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

idx = code.find('72784:')
if idx != -1:
    print("Snippet of 72784:\n", code[idx:idx+2500])
