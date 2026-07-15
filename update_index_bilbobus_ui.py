import os
import re

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Metro and Tranvia SVGs globally
content = content.replace('"/static/img/logo_metro.svg"', '"/static/img/logo_metro_real.svg"')
content = content.replace('"/static/bilbobus.svg"', '"/static/img/logo_bilbobus_real.svg"')
content = content.replace(
    '<svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19h16v-2H4v2zM5 8v6h14V8c0-1.1-.9-2-2-2H7c-1.1 0-2 .9-2 2zm14 0V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v2"></path></svg>',
    '<img src="/static/img/logo_tranvia_real.svg" style="width: 22px; height: 22px; object-fit: contain;" alt="Tranvía">'
)
# Update Tranvia inline SVG in js
content = content.replace(
    '<svg viewBox="0 0 24 24" width="1.2em" height="1.2em" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: text-bottom; margin-right: 6px;"><path d="M4 19h16v-2H4v2zM5 8v6h14V8c0-1.1-.9-2-2-2H7c-1.1 0-2 .9-2 2zm14 0V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v2"></path></svg>',
    '<img src="/static/img/logo_tranvia_real.svg" style="width: 1.2em; height: 1.2em; vertical-align: text-bottom; margin-right: 6px; object-fit: contain;" alt="Tranvía">'
)

# 2. Update Bilbobus Card in HTML
old_bus_card = """                    <div class="linea-card" id="card-bus" onclick="toggleBus()" style="margin-top: 12px;">
                        <div class="linea-icon-wrapper" style="background-color: white; padding: 2px;">
                            <img src="/static/img/logo_bilbobus_real.svg" style="width: 22px; height: 22px; object-fit: contain;" alt="Bilbobus">
                        </div>
                        <div class="linea-info">
                            <strong>Bilbobus (Urbano)</strong>
                            <span>Haz clic para mostrar</span>
                        </div>
                    </div>"""
new_bus_card = """                    <div class="linea-card" id="card-bus" onclick="toggleBusMenu()" style="margin-top: 12px; cursor: pointer;">
                        <div class="linea-icon-wrapper" style="background-color: white; padding: 2px;">
                            <img src="/static/img/logo_bilbobus_real.svg" style="width: 22px; height: 22px; object-fit: contain;" alt="Bilbobus">
                        </div>
                        <div class="linea-info">
                            <strong>Bilbobus (Urbano)</strong>
                            <span id="bus-status-text">Haz clic para desplegar</span>
                        </div>
                        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" id="bus-chevron" style="margin-left: auto; transition: transform 0.3s;"><path d="M6 9l6 6 6-6"/></svg>
                    </div>
                    
                    <div id="bus-lines-container" style="display: none; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 8px; margin-top: 5px;">
                        <div style="display: flex; gap: 8px; margin-bottom: 10px;">
                            <button onclick="toggleAllBusLines(true)" style="flex: 1; padding: 6px; border-radius: 4px; background: #E3001B; color: white; border: none; cursor: pointer; font-size: 11px; font-weight: bold;">Activar Todas</button>
                            <button onclick="toggleAllBusLines(false)" style="flex: 1; padding: 6px; border-radius: 4px; background: #333; color: white; border: none; cursor: pointer; font-size: 11px; font-weight: bold;">Desactivar Todas</button>
                        </div>
                        <div id="bus-lines-grid" style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px;">
                            <!-- Botones generados dinámicamente -->
                        </div>
                    </div>"""
if "bus-lines-container" not in content:
    content = content.replace(old_bus_card, new_bus_card)

# 3. JS Logic for Bilbobus
old_bus_js = r"""        window.toggleBus = function\(\) \{[\s\S]*?if \(panelDetalles\.classList\.contains\('open'\) && document\.querySelector\('\.badge-linea'\) && document\.querySelector\('\.badge-linea'\)\.innerText\.includes\('BILBOBUS'\)\) \{\n                    cerrarPanel\(\);\n                \}\n            \}\n        \};"""

new_bus_js = """        window.busLineasActivas = new Set();
        window.datosGeojsonBus = null;
        window.grupoLineasBus = L.layerGroup();
        map.addLayer(window.grupoLineasBus);
        map.addLayer(grupoMarcadoresBus);
        
        window.toggleBusMenu = function() {
            const container = document.getElementById('bus-lines-container');
            const chevron = document.getElementById('bus-chevron');
            const isOpen = container.style.display === 'block';
            
            container.style.display = isOpen ? 'none' : 'block';
            chevron.style.transform = isOpen ? 'rotate(0deg)' : 'rotate(180deg)';
        };

        window.toggleAllBusLines = function(state) {
            const buttons = document.querySelectorAll('.bus-line-btn');
            buttons.forEach(btn => {
                const linea = btn.dataset.linea;
                if (state) {
                    window.busLineasActivas.add(linea);
                    btn.style.background = '#E3001B';
                    btn.style.color = 'white';
                } else {
                    window.busLineasActivas.delete(linea);
                    btn.style.background = '#333';
                    btn.style.color = '#aaa';
                }
            });
            actualizarMapaBus();
        };

        window.toggleSingleBusLine = function(linea, btn) {
            if (window.busLineasActivas.has(linea)) {
                window.busLineasActivas.delete(linea);
                btn.style.background = '#333';
                btn.style.color = '#aaa';
            } else {
                window.busLineasActivas.add(linea);
                btn.style.background = '#E3001B';
                btn.style.color = 'white';
            }
            actualizarMapaBus();
        };

        window.actualizarMapaBus = function() {
            window.grupoLineasBus.clearLayers();
            grupoMarcadoresBus.clearLayers();
            
            const cardSpan = document.getElementById('bus-status-text');
            if (window.busLineasActivas.size === 0) {
                cardSpan.innerText = 'Desactivado';
            } else {
                cardSpan.innerText = `${window.busLineasActivas.size} líneas activas`;
            }

            if (window.busLineasActivas.size === 0) return;

            // Draw Lines
            if (window.datosGeojsonBus) {
                const filteredFeatures = window.datosGeojsonBus.features.filter(f => window.busLineasActivas.has(f.properties.name));
                const glow = L.geoJSON(filteredFeatures, { style: { color: '#E3001B', weight: 4, opacity: 0.2, lineJoin: 'round', lineCap: 'round' } });
                const linea = L.geoJSON(filteredFeatures, { style: { color: '#E3001B', weight: 2, opacity: 0.9, lineJoin: 'round', lineCap: 'round' } });
                window.grupoLineasBus.addLayer(glow);
                window.grupoLineasBus.addLayer(linea);
            }

            // Draw Markers
            todasLasEstacionesBus.forEach(est => {
                const hasActiveLine = est.lineas.some(l => window.busLineasActivas.has(l));
                if (hasActiveLine) {
                    const marker = marcadoresBusPorId[est.id];
                    if (marker) grupoMarcadoresBus.addLayer(marker);
                }
            });
        };"""

content = re.sub(old_bus_js, new_bus_js, content)

# 4. Fix cargarEstacionesBus to initialize buttons
old_cargar = r"""        function cargarEstacionesBus\(\) \{[\s\S]*?\.catch\(e => console\.error\("Error al cargar shape Bilbobus:", e\)\);\n        \}"""

new_cargar = """        function cargarEstacionesBus() {
            fetch('/api/estaciones_bus')
                .then(r => r.json())
                .then(data => {
                    todasLasEstacionesBus = data;
                    const lineasSet = new Set();
                    todasLasEstacionesBus.forEach(est => {
                        const marker = crearMarcadorBus(est);
                        marcadoresBusPorId[est.id] = marker;
                        est.lineas.forEach(l => lineasSet.add(l));
                    });
                    
                    // Populate UI Grid
                    const grid = document.getElementById('bus-lines-grid');
                    const lineasArr = Array.from(lineasSet).sort((a,b) => a.localeCompare(b, undefined, {numeric: true}));
                    grid.innerHTML = '';
                    lineasArr.forEach(linea => {
                        const btn = document.createElement('button');
                        btn.className = 'bus-line-btn';
                        btn.dataset.linea = linea;
                        btn.innerText = linea;
                        btn.style = 'padding: 4px 2px; border-radius: 4px; background: #333; color: #aaa; border: none; cursor: pointer; font-size: 10px; font-weight: bold; transition: all 0.2s;';
                        btn.onclick = () => window.toggleSingleBusLine(linea, btn);
                        grid.appendChild(btn);
                    });
                })
                .catch(e => console.error("Error al cargar Bilbobus:", e));
                
            fetch('/static/bilbobus.geojson?v=' + new Date().getTime())
                .then(r => r.json())
                .then(data => {
                    window.datosGeojsonBus = data;
                    actualizarMapaBus();
                })
                .catch(e => console.error("Error al cargar shape Bilbobus:", e));
        }"""
content = re.sub(old_cargar, new_cargar, content)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("UI de Bilbobus y Logos oficiales actualizados.")
