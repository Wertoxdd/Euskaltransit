import os
import re

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_logic = """        window.toggleBus = function() {
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
            }
        };"""

new_logic = """        window.busLineasActivas = new Set();
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

if old_logic in content:
    content = content.replace(old_logic, new_logic)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("JS actualizado.")
else:
    print("No se encontro old_logic.")
