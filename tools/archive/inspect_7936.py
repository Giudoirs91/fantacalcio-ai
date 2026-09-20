with open('chunk_7936.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

print("Length of chunk_7936.js:", len(code))

idx = code.find('basic-stats')
while idx != -1:
    print("=== basic-stats context ===")
    print(code[max(0, idx-400):min(len(code), idx+600)])
    print("="*60)
    idx = code.find('basic-stats', idx+1)
