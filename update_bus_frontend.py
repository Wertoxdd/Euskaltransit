import os

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update crearMarcadorBus
old_marker = """
        function crearMarcadorBus(estacion) {
            const el = document.createElement('div');
            el.className = 'estacion-marker';
            
            const lineasBadge = estacion.lineas.slice(0,2).map(l => `<span style="font-size: 8px; background: rgba(255,255,255,0.2); padding: 1px 3px; border-radius: 2px;">${l}</span>`).join(' ');
            
            el.innerHTML = `
                <div class="estacion-dot" style="background: #E3001B; box-shadow: 0 0 8px rgba(227,0,27,0.6); width: 10px; height: 10px;"></div>
                <div class="estacion-label" style="background: rgba(0,0,0,0.8); border: 1px solid rgba(227,0,27,0.3); padding: 4px 6px;">
                    <div class="tooltip-estacion" style="display: flex; align-items: center; white-space: nowrap;">
                        <span style="color: #E3001B; font-weight: 700; margin-right: 4px; font-size: 10px;">B</span>
                        <span style="margin-right: 4px;">${estacion.nombre}</span>
                        ${lineasBadge}
                    </div>
                </div>
            `;"""

new_marker = """
        function crearMarcadorBus(estacion) {
            const el = document.createElement('div');
            el.className = 'estacion-marker';
            
            const lineasBadge = estacion.lineas.slice(0,3).map(l => `<span style="font-size: 8px; background: rgba(255,255,255,0.2); padding: 1px 3px; border-radius: 2px;">${l}</span>`).join(' ') + (estacion.lineas.length > 3 ? '<span style="font-size: 8px; color: #aaa;">...</span>' : '');
            
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
if "border-radius: 50%;" not in old_marker: # Prevent re-replace
    content = content.replace(old_marker, new_marker)


# 2. Add layer logic and load bilbobus.geojson
# toggleBus
old_toggle = """
        window.toggleBus = function() {
            const card = document.getElementById('card-bus');
            const estadoSpan = card.querySelector('.linea-info span');
            busActivo = !busActivo;
            
            if (busActivo) {
                map.addLayer(grupoMarcadoresBus);
                card.classList.add('activa-bus');
                estadoSpan.innerText = 'Mostrando en el mapa';
            } else {
                map.removeLayer(grupoMarcadoresBus);
                card.classList.remove('activa-bus');
                estadoSpan.innerText = 'Haz clic para mostrar';
                if (panelDetalles.classList.contains('open') && document.querySelector('.badge-linea').innerText.includes('BILBOBUS')) {
                    cerrarPanel();
                }
            }
        };"""

new_toggle = """
        window.toggleBus = function() {
            const card = document.getElementById('card-bus');
            const estadoSpan = card.querySelector('.linea-info span');
            busActivo = !busActivo;
            
            if (busActivo) {
                map.addLayer(grupoMarcadoresBus);
                if (window.grupoLineasBus) map.addLayer(window.grupoLineasBus);
                card.classList.add('activa-bus');
                estadoSpan.innerText = 'Mostrando en el mapa';
            } else {
                map.removeLayer(grupoMarcadoresBus);
                if (window.grupoLineasBus) map.removeLayer(window.grupoLineasBus);
                card.classList.remove('activa-bus');
                estadoSpan.innerText = 'Haz clic para mostrar';
                if (panelDetalles.classList.contains('open') && document.querySelector('.badge-linea') && document.querySelector('.badge-linea').innerText.includes('BILBOBUS')) {
                    cerrarPanel();
                }
            }
        };"""
if "window.grupoLineasBus" not in content:
    content = content.replace(old_toggle, new_toggle)


old_cargar = """
        function cargarEstacionesBus() {
            fetch('/api/estaciones_bus')
                .then(r => r.json())
                .then(data => {
                    todasLasEstacionesBus = data;
                    todasLasEstacionesBus.forEach(est => {
                        const marker = crearMarcadorBus(est);
                        marcadoresBusPorId[est.id] = marker;
                        grupoMarcadoresBus.addLayer(marker);
                    });
                })
                .catch(e => console.error("Error al cargar Bilbobus:", e));
        }"""

new_cargar = """
        function cargarEstacionesBus() {
            fetch('/api/estaciones_bus')
                .then(r => r.json())
                .then(data => {
                    todasLasEstacionesBus = data;
                    todasLasEstacionesBus.forEach(est => {
                        const marker = crearMarcadorBus(est);
                        marcadoresBusPorId[est.id] = marker;
                        grupoMarcadoresBus.addLayer(marker);
                    });
                })
                .catch(e => console.error("Error al cargar Bilbobus:", e));
                
            fetch('/static/bilbobus.geojson')
                .then(r => r.json())
                .then(data => {
                    window.grupoLineasBus = L.layerGroup();
                    const capaGlow = L.geoJSON(data, { style: { color: '#E3001B', weight: 4, opacity: 0.15, lineJoin: 'round', lineCap: 'round' } });
                    const capaLinea = L.geoJSON(data, { style: { color: '#E3001B', weight: 2, opacity: 0.8, lineJoin: 'round', lineCap: 'round' } });
                    window.grupoLineasBus.addLayer(capaGlow);
                    window.grupoLineasBus.addLayer(capaLinea);
                    if (busActivo) map.addLayer(window.grupoLineasBus);
                })
                .catch(e => console.error("Error al cargar shape Bilbobus:", e));
        }"""
if "bilbobus.geojson" not in content:
    content = content.replace(old_cargar, new_cargar)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Frontend actualizado con las geometrías de Bilbobus.")
