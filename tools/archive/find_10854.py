import glob

for fpath in glob.glob("chunks/*.js"):
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    if '10854:' in code:
        print(f"FOUND 10854 in {fpath}!")
        idx = code.find('10854:')
        print(code[idx:idx+3500])
