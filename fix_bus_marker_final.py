import re

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CSS to include Bilbobus styles
css_metro = r"(\.estacion-marker-metro \.tooltip-estacion \{ border-color: rgba\(var\(--metro-rgb\), 0\.2\); \})"
css_bus = """\\1
        .estacion-marker-bus .punto-svg { filter: drop-shadow(0 0 4px rgba(227,0,27,0.6)); border-radius: 3px; background: white; }
        .estacion-marker-bus:hover .punto-svg { filter: drop-shadow(0 0 8px rgba(227,0,27,0.9)); }
        .estacion-marker-bus .tooltip-estacion { border-color: rgba(227,0,27,0.4); }"""
content = re.sub(css_metro, css_bus, content)

# 2. Update crearMarcadorBus
old_marker = r"""        function crearMarcadorBus\(estacion\) \{[\s\S]*?iconAnchor: \[8, 8\] \}\)\n            \}\);"""
new_marker = """        function crearMarcadorBus(estacion) {
            const el = document.createElement('div');
            el.className = 'estacion-marker estacion-marker-bus';
            
            const lineasBadge = estacion.lineas.slice(0,3).map(l => `<span style="font-size: 8px; background: rgba(255,255,255,0.2); padding: 1px 3px; border-radius: 2px;">${l}</span>`).join(' ') + (estacion.lineas.length > 3 ? '<span style="font-size: 8px; color: #aaa;">...</span>' : '');
            
            const logoB = `<img src="/static/img/logo_bilbobus_real.svg" style="width: 16px; height: 16px; border-radius: 3px; background: white;">`;
            
            el.innerHTML = `
                <img src="/static/img/logo_bilbobus_real.svg" class="punto-svg" style="border-radius: 3px; background: white;" alt="Bilbobus">
                <div class="tooltip-estacion" style="display: flex; align-items: center; white-space: nowrap; gap: 6px;">
                    ${logoB}
                    <span style="color: white; font-weight: 600;">${estacion.nombre}</span>
                    <div style="display: flex; gap: 2px;">${lineasBadge}</div>
                </div>
            `;
            
            const marker = L.marker([estacion.latitud, estacion.longitud], {
                icon: L.divIcon({ html: el, className: '', iconSize: [16, 16], iconAnchor: [8, 8] })
            });"""

content = re.sub(old_marker, new_marker, content)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Marcador de Bilbobus reconstruido correctamente.")
