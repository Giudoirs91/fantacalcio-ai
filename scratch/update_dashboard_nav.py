import os

dashboard_path = "Dashboard_Fanta_1000.html"
with open(dashboard_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
target_found = False
for i, line in enumerate(lines):
    new_lines.append(line)
    if 'id="tabMatchdayAdviceBtn"' in line and not target_found:
        indent = " " * 24
        new_lines.append(f'{indent}<a href="infortunati-serie-a/index.html" class="dropdown-item" id="tabInjuriesBtn">🩺 Infortunati &amp; Tempi di Recupero</a>\n')
        new_lines.append(f'{indent}<a href="rigoristi-serie-a/index.html" class="dropdown-item" id="tabPenaltiesBtn">🎯 Rigoristi &amp; Calci Piazzati</a>\n')
        new_lines.append(f'{indent}<div class="dropdown-divider"></div>\n')
        target_found = True

if target_found:
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("SUCCESS: Infortunati and Rigoristi links added to Dashboard_Fanta_1000.html navbar!")
else:
    print("WARNING: tabMatchdayAdviceBtn not found in lines")
