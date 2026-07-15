import os

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

sel_mod = """            } else if (marcadoresBusPorId[id]) {
                if (!busActivo) toggleBus();
                const marker = marcadoresBusPorId[id];
                const estacion = todasLasEstacionesBus.find(e => e.id === id);
                abrirPanelBus(estacion, marker);

            } else {"""

if sel_mod in content:
    # First, undo all of them
    content = content.replace(sel_mod, '} else {')
    print("Undo successful.")
else:
    print("sel_mod not found")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)
