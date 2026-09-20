with open('chunk_6972.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

idx = code.find('.stats=')
if idx == -1:
    idx = code.find('stats(')

while idx != -1:
    print("=== stats context ===")
    print(code[max(0, idx-100):min(len(code), idx+300)])
    print("="*60)
    idx = code.find('stats(', idx+1)
