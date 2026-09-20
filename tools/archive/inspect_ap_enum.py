with open('chunk_7936.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

idx = code.find('._Q=')
if idx == -1:
    idx = code.find('._Q =')
if idx == -1:
    idx = code.find('_Q:')

print("Context of _Q:\n", code[max(0, idx-100):min(len(code), idx+1500)])
