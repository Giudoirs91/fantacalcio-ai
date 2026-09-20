with open('chunks/b9e39b43-b5eda7c146674b07.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

print("Length of b9e39b43:", len(code))

idx = code.find('rE=')
if idx != -1:
    print("Snippet of rE:\n", code[idx:idx+3500])
