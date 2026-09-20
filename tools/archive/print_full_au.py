with open('webpack.js', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

idx = code.find('a.u=')
print(code[idx:idx+12000])
