import os

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Undo the invalid Promise.all insertion
if "cargarEstacionesBus();\n            fetch('/api/estaciones').then(r => r.json())," in content:
    content = content.replace(
        "cargarEstacionesBus();\n            fetch('/api/estaciones').then(r => r.json()),",
        "fetch('/api/estaciones').then(r => r.json()),"
    )

# Insert correctly before Promise.all
if "cargarEstacionesBus();" not in content:
    content = content.replace(
        "Promise.all([",
        "cargarEstacionesBus();\n          Promise.all(["
    )

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Sintaxis de Promise.all arreglada.")
