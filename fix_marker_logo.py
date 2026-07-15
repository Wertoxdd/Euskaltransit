import re

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the marker and tooltip to use the realistic "B" logo from the physical bus stops
old_marker = """
              el.innerHTML = `
                  <div class="estacion-dot" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #E3001B; box-shadow: 0 0 8px rgba(227,0,27,0.6); width: 10px; height: 10px; border-radius: 50%; z-index: 3;"></div>
                  <div class="tooltip-estacion" style="display: flex; align-items: center; white-space: nowrap; background: rgba(0,0,0,0.8); border: 1px solid rgba(227,0,27,0.3); padding: 4px 6px; border-radius: 6px; z-index: 4;">
                      <span style="color: #E3001B; font-weight: 700; margin-right: 4px; font-size: 10px;">B</span>
                      <span style="margin-right: 4px;">${estacion.nombre}</span>
                      ${lineasBadge}
                  </div>
              `;"""

new_marker = """
              const logoB = `<div style="display: inline-flex; align-items: center; justify-content: center; background: #E3001B; color: white; width: 14px; height: 14px; border-radius: 3px; font-weight: 900; font-size: 10px; font-family: 'Arial', sans-serif; box-shadow: 0 0 4px rgba(227,0,27,0.6);">B</div>`;
              
              el.innerHTML = `
                  <div class="estacion-dot" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 3;">
                      ${logoB}
                  </div>
                  <div class="tooltip-estacion" style="display: flex; align-items: center; white-space: nowrap; background: rgba(0,0,0,0.8); border: 1px solid rgba(227,0,27,0.3); padding: 4px 6px; border-radius: 6px; z-index: 4; gap: 6px;">
                      ${logoB}
                      <span style="color: white; font-weight: 600;">${estacion.nombre}</span>
                      <div style="display: flex; gap: 2px;">${lineasBadge}</div>
                  </div>
              `;"""

content = content.replace(old_marker, new_marker)

# Also fix the SVG Bilbobus logo text inside the actual generated SVG file to look better
with open('static/img/logo_bilbobus_real.svg', 'w', encoding='utf-8') as f:
    f.write('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect x="0" y="0" width="100" height="100" rx="15" ry="15" fill="#E3001B"/>
  <text x="50" y="58" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="24" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="-1">Bilbobus</text>
</svg>''')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Marcadores actualizados al diseño original de las paradas.")
