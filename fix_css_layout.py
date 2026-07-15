import re

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix grid overflow
old_grid = '<div id="bus-lines-grid" style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px;">'
new_grid = '<div id="bus-lines-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(36px, 1fr)); gap: 4px;">'
content = content.replace(old_grid, new_grid)

# 2. Fix Bilbobus badges wrapping logic
old_badge = """<div class="badge-linea" style="background: rgba(227,0,27,0.1); color: #E3001B; border-color: rgba(227,0,27,0.4); margin-bottom: 0; display: flex; flex-wrap: wrap; gap: 4px; align-items: center; flex: 1;">
                    <span style="font-weight: bold; margin-right: 4px;">BILBOBUS</span> ${lineasBadges}
                </div>"""

new_badge = """<div class="badge-linea" style="background: rgba(227,0,27,0.1); color: #E3001B; border-color: rgba(227,0,27,0.4); margin-bottom: 0; display: flex; gap: 8px; align-items: center; flex: 1;">
                    <div style="font-weight: bold; align-self: flex-start; padding-top: 2px;">BILBOBUS</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 4px; flex: 1;">${lineasBadges}</div>
                </div>"""

content = content.replace(old_badge, new_badge)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Arreglos de CSS aplicados correctamente.")
