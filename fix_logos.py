import os
import re

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Revert Metro Bilbao logo
content = content.replace('"/static/img/logo_metro_real.svg"', '"/static/img/logo_metro.svg"')

# 2. Revert Tranvia logo to its original state where it was replaced
# The inline SVG might be gone, so let's check what it was replaced with.
# It was replaced with <img src="/static/img/logo_tranvia_real.svg" ...>
old_tranvia_img = '<img src="/static/img/logo_tranvia_real.svg" style="width: 22px; height: 22px; object-fit: contain;" alt="Tranvía">'
new_tranvia_svg = '<svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19h16v-2H4v2zM5 8v6h14V8c0-1.1-.9-2-2-2H7c-1.1 0-2 .9-2 2zm14 0V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v2"></path></svg>'
content = content.replace(old_tranvia_img, new_tranvia_svg)

old_tranvia_img_inline = '<img src="/static/img/logo_tranvia_real.svg" style="width: 1.2em; height: 1.2em; vertical-align: text-bottom; margin-right: 6px; object-fit: contain;" alt="Tranvía">'
new_tranvia_svg_inline = '<svg viewBox="0 0 24 24" width="1.2em" height="1.2em" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: text-bottom; margin-right: 6px;"><path d="M4 19h16v-2H4v2zM5 8v6h14V8c0-1.1-.9-2-2-2H7c-1.1 0-2 .9-2 2zm14 0V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v2"></path></svg>'
content = content.replace(old_tranvia_img_inline, new_tranvia_svg_inline)

# 3. Fix Bilbobus marker rendering issue
old_marker = """
              el.innerHTML = `
                  <div class="estacion-dot" style="background: #E3001B; box-shadow: 0 0 8px rgba(227,0,27,0.6); width: 10px; height: 10px; border-radius: 50%;"></div>
                  <div class="estacion-label" style="background: rgba(0,0,0,0.8); border: 1px solid rgba(227,0,27,0.3); padding: 4px 6px;">
                      <div class="tooltip-estacion" style="display: flex; align-items: center; white-space: nowrap;">
                          <span style="color: #E3001B; font-weight: 700; margin-right: 4px; font-size: 10px;">B</span>
                          <span style="margin-right: 4px;">${estacion.nombre}</span>
                          ${lineasBadge}
                      </div>
                  </div>
              `;"""

new_marker = """
              el.innerHTML = `
                  <div class="estacion-dot" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #E3001B; box-shadow: 0 0 8px rgba(227,0,27,0.6); width: 10px; height: 10px; border-radius: 50%; z-index: 3;"></div>
                  <div class="tooltip-estacion" style="display: flex; align-items: center; white-space: nowrap; background: rgba(0,0,0,0.8); border: 1px solid rgba(227,0,27,0.3); padding: 4px 6px; border-radius: 6px; z-index: 4;">
                      <span style="color: #E3001B; font-weight: 700; margin-right: 4px; font-size: 10px;">B</span>
                      <span style="margin-right: 4px;">${estacion.nombre}</span>
                      ${lineasBadge}
                  </div>
              `;"""
content = content.replace(old_marker, new_marker)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Logos revertidos/arreglados y marcadores de Bilbobus corregidos.")
