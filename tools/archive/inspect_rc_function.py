with open('chunks/b9e39b43-b5eda7c146674b07.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

idx = code.find('rc=')
if idx != -1:
    print("Snippet of rc:\n", code[idx:idx+4000])
