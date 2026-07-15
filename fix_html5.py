import os

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all occurrences back
content = content.replace("cargarEstacionesBus();\n          Promise.all([", "Promise.all([")

# Insert ONLY before the first Promise.all
parts = content.split("Promise.all([", 1)
content = parts[0] + "cargarEstacionesBus();\n          Promise.all([" + parts[1]

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Arreglado el duplicado.")
