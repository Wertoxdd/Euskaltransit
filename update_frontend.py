import os

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add CSS for Bilbobus
css_addition = """
        .linea-card.activa-bus { 
            background: linear-gradient(180deg, #181010 0%, #090505 100%);
            border-color: #261a1a;
            box-shadow: inset 0 2px 8px rgba(0,0,0,0.9);
            transform: translateY(1px);
            border-bottom-width: 1px;
        }
        .linea-card.activa-bus::after {
            background: #E3001B; box-shadow: 0 0 8px #E3001B, inset 0 1px 1px rgba(255,255,255,0.5);
        }
        .linea-card.activa-bus .linea-icon-wrapper { color: #fff; background: rgba(227,0,27,0.1); border-color: rgba(227,0,27,0.3); }

        @media (hover: hover) {
            .linea-card.activa-bus:hover { background: rgba(227,0,27,0.15); border-color: rgba(227,0,27,0.3); }
        }
"""
if "activa-bus" not in content:
    content = content.replace('.linea-card.activa-metro-l2 { \n            background: linear-gradient', css_addition + '\n        .linea-card.activa-metro-l2 { \n            background: linear-gradient')

# 2. Add Sidebar Button
button_addition = """
                    <div class="linea-card" id="card-bus" onclick="toggleBus()" style="margin-top: 12px;">
                        <div class="linea-icon-wrapper">
                            <svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19h16v-2H4v2zM5 8v6h14V8c0-1.1-.9-2-2-2H7c-1.1 0-2 .9-2 2zm14 0V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v2"></path></svg>
                        </div>
                        <div class="linea-info">
                            <strong>Bilbobus (Urbano)</strong>
                            <span>Haz clic para mostrar</span>
                        </div>
                    </div>
"""
if "card-bus" not in content:
    content = content.replace('                    <div class="linea-card" id="card-metro-l2"', button_addition + '\n                    <div class="linea-card" id="card-metro-l2"')

# 3. Add JS toggle function & vars
js_addition = """
        const grupoMarcadoresBus = L.layerGroup();
        let todasLasEstacionesBus = [];
        let marcadoresBusPorId = {};
        let busActivo = false;

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
            }
        };

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
        }

        const svgBus = `<svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px; margin-top: -2px;"><path d="M4 19h16v-2H4v2zM5 8v6h14V8c0-1.1-.9-2-2-2H7c-1.1 0-2 .9-2 2zm14 0V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v2"></path></svg>`;

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
            `;
            
            const marker = L.marker([estacion.latitud, estacion.longitud], {
                icon: L.divIcon({ html: el, className: '', iconSize: [14, 14], iconAnchor: [7, 7] })
            });
            
            marker.estacionData = estacion;
            marker.on('click', (ev) => {
                L.DomEvent.stopPropagation(ev);
                abrirPanelBus(estacion, marker);
            });
            
            return marker;
        }

        function abrirPanelBus(estacion, marker, zoomNivel = 17) {
            seleccionarMarcador(marker);
            map.flyTo([estacion.latitud, estacion.longitud], zoomNivel, { duration: 0.8, easeLinearity: 0.4 });

            panel.style.background = 'var(--bg-app)';
            panel.style.borderLeftColor = 'rgba(227,0,27,0.5)';
            panel.classList.add('abierto');
            
            document.getElementById('panel-titulo').innerHTML = `<div style="display: flex; align-items: center; gap: 6px;">${svgBus} <span>${estacion.nombre}</span></div>`;

            const lineasBadges = estacion.lineas.map(l => `<span style="background: rgba(227,0,27,0.2); color: #E3001B; padding: 2px 8px; border-radius: 10px; font-size: 0.7em; font-weight: 700;">${l}</span>`).join(' ');

            document.getElementById('contenido-parada').innerHTML = `
            <div class="panel-fade-item" style="animation-delay: 0.05s; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div class="badge-linea" style="background: rgba(227,0,27,0.1); color: #E3001B; border-color: rgba(227,0,27,0.4); margin-bottom: 0;">
                    BILBOBUS ${lineasBadges}
                </div>
                <button class="btn-recargar" onclick="abrirPanelBus(todasLasEstacionesBus.find(e => e.id === '${estacion.id}'), marcadorSeleccionado, map.getZoom())" title="Recargar Horarios" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 6px; color: var(--text-secondary); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s;">
                    <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
                    Actualizar
                </button>
            </div>
            
            <div class="panel-fade-item" style="animation-delay: 0.1s; margin-top: 15px;">
                <div style="font-size: 0.8em; color: var(--text-secondary); line-height: 1.5;">
                    Operado por Bilbobus.
                    <br>Los horarios mostrados están basados en las planificaciones GTFS oficiales.
                </div>
            </div>
            `;
        }
"""
if "grupoMarcadoresBus" not in content:
    content = content.replace('function cerrarPanel() {', js_addition + '\n        function cerrarPanel() {')

# 4. Call cargarEstacionesBus() in Promise.all
if "cargarEstacionesBus()" not in content:
    content = content.replace('fetch(\'/api/estaciones\')', 'cargarEstacionesBus();\n                fetch(\'/api/estaciones\')')

# 5. Add search support
search_mod = """
            todasLasEstacionesBus.forEach(est => {
                if (est.nombre.toLowerCase().includes(termino)) {
                    resultados.push({ id: est.id, nombre: est.nombre, tipo: 'bus', l1: false, l2: false, original: est.nombre });
                }
            });
"""
if "todasLasEstacionesBus.forEach(" not in content:
    content = content.replace('if (resultados.length === 0) {', search_mod + '\n            if (resultados.length === 0) {')

# 6. Search icon rendering
icon_mod = """
                } else if (res.tipo === 'bus') {
                    iconHtml = `<div style="width: 24px; height: 24px; border-radius: 6px; background: rgba(227,0,27,0.1); border: 1px solid rgba(227,0,27,0.3); display: flex; align-items: center; justify-content: center; color: #E3001B;">${svgBus}</div>`;
"""
if "res.tipo === 'bus'" not in content:
    content = content.replace('iconHtml = `<div style="width: 24px; height: 24px; border-radius: 6px; background: rgba(52,182,88,0.1); border: 1px solid rgba(52,182,88,0.3); display: flex; align-items: center; justify-content: center; color: #34b658;">${svgTranvia}</div>`;\n                }', 'iconHtml = `<div style="width: 24px; height: 24px; border-radius: 6px; background: rgba(52,182,88,0.1); border: 1px solid rgba(52,182,88,0.3); display: flex; align-items: center; justify-content: center; color: #34b658;">${svgTranvia}</div>`;\n                }' + icon_mod)

# 7. selection router
sel_mod = """
            } else if (marcadoresBusPorId[id]) {
                if (!busActivo) toggleBus();
                const marker = marcadoresBusPorId[id];
                const estacion = todasLasEstacionesBus.find(e => e.id === id);
                abrirPanelBus(estacion, marker);
"""
if "marcadoresBusPorId[id]" not in content:
    content = content.replace('} else {', sel_mod + '\n            } else {')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("index.html actualizado")
