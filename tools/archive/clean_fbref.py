import sys

with open('fbref_stats_25-26.csv', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

clean_lines = []
for line in lines:
    if '\"type\":700013' in line:
        line = line.split('\"type\":700013')[0].strip() + '\n'
    clean_lines.append(line)

with open('fbref_stats_25-26.csv', 'w', encoding='utf-8') as f:
    f.writelines(clean_lines)

print(f"Cleaned fbref_stats_25-26.csv: {len(clean_lines)} lines.")
