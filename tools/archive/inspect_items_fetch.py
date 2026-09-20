with open('chunks/7134.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

idx = code.find('default:()=>A')
print("Snippet of A:\n", code[idx:idx+5000])
