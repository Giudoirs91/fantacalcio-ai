import glob

for fpath in glob.glob("*.js") + glob.glob("chunks/*.js"):
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    if '72784:' in code:
        print(f"FOUND 72784 in {fpath}!")
        idx = code.find('72784:')
        print(code[idx:idx+2500])
