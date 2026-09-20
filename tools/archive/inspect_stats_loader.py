with open('chunk_7936.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

idx = code.find('basic-stats')
print("Snippet:\n", code[idx-200:idx+2500])
