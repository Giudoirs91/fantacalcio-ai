with open('data/raw/fantarefri_b64.txt', 'r') as f:
    b64 = f.read().strip()
with open('web/js/sample_fantarefri_data.js', 'w', encoding='utf-8') as f:
    f.write('// --- sample_fantarefri_data.js ---\n')
    f.write(f'const SAMPLE_FANTAREFRI_B64 = "{b64}";\n')
print('Created web/js/sample_fantarefri_data.js successfully!')
