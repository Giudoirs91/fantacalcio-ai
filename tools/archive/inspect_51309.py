with open('chunk_7936.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

idx = code.find('51309:')
if idx != -1:
    print("Snippet of 51309:\n", code[idx:idx+2500])
