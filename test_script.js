
        window.switchTab = function(mode) {
            const tabs = ['todo', 'tranvia', 'metro'];
            tabs.forEach(t => document.getElementById(`tab-${t}`).classList.remove('activo'));
            document.getElementById(`tab-${mode}`).classList.add('activo');
            
            if (mode === 'todo') {
                document.getElementById('card-tranvia').style.display = 'flex';
                document.getElementById('card-metro-l1').style.display = 'flex';
                document.getElementById('card-metro-l2').style.display = 'flex';
            } else if (mode === 'tranvia') {
                document.getElementById('card-tranvia').style.display = 'flex';
                document.getElementById('card-metro-l1').style.display = 'none';
                document.getElementById('card-metro-l2').style.display = 'none';
            } else if (mode === 'metro') {
                document.getElementById('card-tranvia').style.display = 'none';
                document.getElementById('card-metro-l1').style.display = 'flex';
                document.getElementById('card-metro-l2').style.display = 'flex';
            }
        };

        window.toggleCalculadora = function(show) {
            if (show) {
                document.getElementById('menu-principal').style.display = 'none';
                document.getElementById('panel-calculadora').style.display = 'block';
            } else {
                document.getElementById('menu-principal').style.display = 'block';
                document.getElementById('panel-calculadora').style.display = 'none';
            }
        };

        window.enfocarVehiculoReal = function(stopId, tipoVehiculo = 'tranvia') {
            // Placeholder: Buscar el primer vehículo real de la red correspondiente.
            // Cuando tengamos la API final conectada, cruzaremos el stopId con la ruta del vehículo.
            if (!window.vehiculosMarkers) {
                alert("Aún no se han recibido datos en tiempo real de los vehículos.");
                return;
            }
            
            let vehicles = Object.values(window.vehiculosMarkers).filter(m => m.vehiculoData && m.vehiculoData.tipo === tipoVehiculo);
            
            if (vehicles.length > 0) {
                // Hacemos flyTo al primer vehículo en ruta
                map.flyTo(vehicles[0].getLatLng(), 16, { duration: 1.5 });
            } else {
                alert(`Esperando datos de la red de geolocalización de ${tipoVehiculo === 'metro' ? 'Metro Bilbao' : 'Euskotren'}...`);
            }
        };

        // ═══════════════════════════════════
        // Lógica de arrastre (Draggable Window)
        // ═══════════════════════════════════
        const svgTranvia = `<img src="/static/euskotren.svg" style="width: 1.2em; height: 1.2em; vertical-align: text-bottom; margin-right: 6px; object-fit: contain;" alt="Euskotren">`;
        const panel = document.getElementById('panel-info');
        const header = document.getElementById('panel-header');
        
        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;
        let xOffset = 0;
        let yOffset = 0;

        header.addEventListener('mousedown', dragStart);
        document.addEventListener('mouseup', dragEnd);
        document.addEventListener('mousemove', drag);

        function dragStart(e) {
            initialX = e.clientX - xOffset;
            initialY = e.clientY - yOffset;
            if (e.target === header || e.target.id === 'panel-titulo' || e.target.closest('#panel-header')) {
                isDragging = true;
                document.body.style.userSelect = 'none';
            }
        }
        function dragEnd(e) {
            initialX = currentX;
            initialY = currentY;
            isDragging = false;
            document.body.style.userSelect = '';
        }
        function drag(e) {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
                xOffset = currentX;
                yOffset = currentY;
                
                // Aplicamos la posición de arrastre
                // Se usa position absolute, así que modificamos transform.
                // Como tenemos clases que manejan transform, usamos estilo inline
                panel.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
            }
        }

        // ═══════════════════════════════════
        // 1. Inicialización del Mapa
        // ═══════════════════════════════════
        
        // Función matemática: proyectar punto en un segmento (Snapping)
        window.proyectarPuntoEnSegmento = function(p, a, b) {
            const atob = [b[0] - a[0], b[1] - a[1]];
            const atop = [p[0] - a[0], p[1] - a[1]];
            const len2 = atob[0]*atob[0] + atob[1]*atob[1];
            if (len2 === 0) return a;
            let t = Math.max(0, Math.min(1, (atop[0]*atob[0] + atop[1]*atob[1]) / len2));
            return [a[0] + atob[0]*t, a[1] + atob[1]*t];
        };

        const map = L.map('mapa', {
            zoomAnimation: true,
            markerZoomAnimation: true,
            zoomControl: false // Quitamos el control de zoom por defecto para reubicarlo
        }).setView([43.2627, -2.9253], 14);

        // Control de zoom abajo a la derecha
        L.control.zoom({ position: 'bottomright' }).addTo(map);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            className: 'mapa-tiles'
        }).addTo(map);

        let marcadorSeleccionado = null;
        const todosLosMarcadores = [];
        const marcadoresPorId = {};
        let todasLasEstaciones = [];
        
        // Capas para poder ocultar/mostrar
        const grupoMarcadores = L.featureGroup();
        const grupoLinea = L.featureGroup();
        const grupoMarcadoresMetro = L.featureGroup();
        const grupoLineaMetro = L.featureGroup();
        let metroL1Activo = false;
        let metroL2Activo = false;
        let todasLasEstacionesMetro = [];
        const marcadoresMetroPorId = {};
        const todosLosMarcadoresMetro = [];
        let tranviaActivo = false;
        
        window.toggleTranvia = function() {
            const card = document.getElementById('card-tranvia');
            const estadoSpan = card.querySelector('.linea-info span');
            tranviaActivo = !tranviaActivo;
            
            if (tranviaActivo) {
                map.addLayer(grupoLinea);
                map.addLayer(grupoMarcadores);
                card.classList.add('activa');
                estadoSpan.innerText = 'Mostrando en el mapa';
                
                if (Object.keys(grupoLinea._layers).length > 0) {
                    map.flyToBounds(grupoLinea.getBounds(), { padding: [50, 50], duration: 1 });
                }
            } else {
                map.removeLayer(grupoLinea);
                map.removeLayer(grupoMarcadores);
                card.classList.remove('activa');
                estadoSpan.innerText = 'Haz clic para mostrar';
                cerrarPanel();
            }
            
            // Actualizar visibilidad de vehículos tranvía
            for (let vid in vehiculosMarkers) {
                if (vid.startsWith('metro_')) continue;
                const marker = vehiculosMarkers[vid];
                if (tranviaActivo) {
                    if (!map.hasLayer(marker)) map.addLayer(marker);
                } else {
                    if (map.hasLayer(marker)) map.removeLayer(marker);
                }
            }
        };

        const svgMetro = `<img src="/static/img/logo_metro.svg" style="width: 1.2em; height: 1.2em; vertical-align: text-bottom; margin-right: 6px; object-fit: contain;" alt="Metro">`;

        window.toggleMetro = function(linea) {
            if (linea === 'L1') {
                metroL1Activo = !metroL1Activo;
                const card = document.getElementById('card-metro-l1');
                const estadoSpan = card.querySelector('.linea-info span');
                if (metroL1Activo) {
                    card.classList.add('activa-metro-l1');
                    estadoSpan.innerText = 'Mostrando en el mapa';
                } else {
                    card.classList.remove('activa-metro-l1');
                    estadoSpan.innerText = 'Haz clic para mostrar';
                }
            } else if (linea === 'L2') {
                metroL2Activo = !metroL2Activo;
                const card = document.getElementById('card-metro-l2');
                const estadoSpan = card.querySelector('.linea-info span');
                if (metroL2Activo) {
                    card.classList.add('activa-metro-l2');
                    estadoSpan.innerText = 'Mostrando en el mapa';
                } else {
                    card.classList.remove('activa-metro-l2');
                    estadoSpan.innerText = 'Haz clic para mostrar';
                }
            }
            
            // Actualizar Marcadores
            if (todasLasEstacionesMetro) {
                todasLasEstacionesMetro.forEach(estacion => {
                    const marker = marcadoresMetroPorId[estacion.id];
                    if (!marker) return;
                    const showL1 = (estacion.lineas || []).includes('L1') && metroL1Activo;
                    const showL2 = (estacion.lineas || []).includes('L2') && metroL2Activo;
                    if (showL1 || showL2) {
                        if (!map.hasLayer(marker)) map.addLayer(marker);
                    } else {
                        if (map.hasLayer(marker)) map.removeLayer(marker);
                    }
                });
            }
            
            // Actualizar Líneas
            if (window.capasLineasMetro) {
                let bounds = L.latLngBounds();
                let hasBounds = false;
                window.capasLineasMetro.forEach(capa => {
                    const show = (capa.isL1 && metroL1Activo) || (capa.isL2 && metroL2Activo);
                    if (show) {
                        if (!map.hasLayer(capa.glow)) map.addLayer(capa.glow);
                        if (!map.hasLayer(capa.line)) map.addLayer(capa.line);
                        bounds.extend(capa.line.getBounds());
                        hasBounds = true;
                    } else {
                        if (map.hasLayer(capa.glow)) map.removeLayer(capa.glow);
                        if (map.hasLayer(capa.line)) map.removeLayer(capa.line);
                    }
                });
                if (hasBounds && linea !== 'UPDATE') {
                    map.flyToBounds(bounds, { padding: [50, 50], duration: 1 });
                }
            }

            // Actualizar Vehículos
            for (let vid in vehiculosMarkers) {
                if (!vid.startsWith('metro_')) continue;
                const marker = vehiculosMarkers[vid];
                if (marker.vehiculoData) {
                    const v = marker.vehiculoData;
                    const show = (v.linea === 'L1' && metroL1Activo) || (v.linea === 'L2' && metroL2Activo);
                    if (show) {
                        if (!map.hasLayer(marker)) map.addLayer(marker);
                    } else {
                        if (map.hasLayer(marker)) map.removeLayer(marker);
                    }
                }
            }
            
            if (!metroL1Activo && !metroL2Activo) {
                cerrarPanel();
            }
        };

        function crearIconoEstacionMetro(nombre, lineas) {
            const isL2Only = lineas && lineas.includes('L2') && !lineas.includes('L1');
            const extraClass = isL2Only ? 'l2' : '';
            return L.divIcon({
                className: '', iconSize: [16, 16], iconAnchor: [8, 8],
                html: `
                    <div class="estacion-marker estacion-marker-metro ${extraClass}">
                        <img src="/static/img/logo_metro.svg" class="punto-svg" alt="Metro">
                        <div class="tooltip-estacion">${svgMetro}${nombre}</div>
                    </div>
                `
            });
        }

        function abrirPanelMetro(estacion, marker, zoomNivel = 16) {
            seleccionarMarcador(marker);
            map.flyTo([estacion.latitud, estacion.longitud], zoomNivel, { duration: 0.8, easeLinearity: 0.4 });
            xOffset = 0; yOffset = 0;
            panel.style.transform = '';
            panel.classList.add('abierto');
            
            document.getElementById('panel-titulo').innerHTML = `${svgMetro}${estacion.nombre}`;

            const lineasEstacion = estacion.lineas || [];
            const lineaPrincipal = lineasEstacion[0] || 'L1';
            
            if (lineaPrincipal === 'L2') {
                panel.style.background = 'linear-gradient(145deg, rgba(40, 40, 40, 0.95) 0%, rgba(20, 20, 20, 0.98) 100%)';
                panel.style.borderColor = 'rgba(136,136,136,0.3)';
            } else {
                panel.style.background = 'linear-gradient(145deg, rgba(60, 15, 15, 0.95) 0%, rgba(25, 5, 5, 0.98) 100%)';
                panel.style.borderColor = 'rgba(227,0,27,0.3)';
            }
            
            // Get ordered stations for ALL appropriate lines
            const ORDEN_L1 = ["Etxebarri", "Bolueta", "Basarrate", "Santutxu", "Casco Viejo", "Abando", "Eliptikoa", "Indautxu", "San Mam", "Deustu", "Sarriko", "San Ignazio", "Lutxana", "Erandio", "Astrabudua", "Leioa", "Lamiako", "Areeta", "Gobela", "Neguri", "Aiboa", "Algorta", "Bidezabal", "Ibarbengoa", "Berango", "Larrabasterra", "Sopela", "Urduliz", "Plentzia"];
            const ORDEN_L2 = ["Basauri", "Ariz", "Etxebarri", "Bolueta", "Basarrate", "Santutxu", "Casco Viejo", "Abando", "Eliptikoa", "Indautxu", "San Mam", "Deustu", "Sarriko", "San Ignazio", "Cruces", "Ansio", "Barakaldo", "Bagatza", "Urbinaga", "Sestao", "Abatxolo", "Portugalete", "Pe", "Santurtzi", "Kabiezes"];
            const getOrder = (nombre, arr) => {
                const idx = arr.findIndex(n => nombre.includes(n));
                return idx === -1 ? 999 : idx;
            };

            const prevEstacionesMap = new Map();
            const nextEstacionesMap = new Map();

            lineasEstacion.forEach(linea => {
                if (linea !== 'L1' && linea !== 'L2') return;
                const ordenActual = linea === 'L1' ? ORDEN_L1 : ORDEN_L2;
                const prop = linea === 'L1' ? 'orden_l1' : 'orden_l2';
                
                const estacionesLinea = todasLasEstacionesMetro.filter(e => (e.lineas || []).includes(linea));
                estacionesLinea.sort((a, b) => {
                    let oa = a[prop] !== undefined && a[prop] < 999 ? a[prop] : getOrder(a.nombre, ordenActual);
                    let ob = b[prop] !== undefined && b[prop] < 999 ? b[prop] : getOrder(b.nombre, ordenActual);
                    return oa - ob;
                });
                
                const currentIndex = estacionesLinea.findIndex(e => e.id === estacion.id);
                if (currentIndex > 0) {
                    const prev = estacionesLinea[currentIndex - 1];
                    prevEstacionesMap.set(prev.id, prev);
                }
                if (currentIndex !== -1 && currentIndex < estacionesLinea.length - 1) {
                    const next = estacionesLinea[currentIndex + 1];
                    nextEstacionesMap.set(next.id, next);
                }
            });

            const prevList = Array.from(prevEstacionesMap.values());
            const nextList = Array.from(nextEstacionesMap.values());

            let colores = {
                bgHover: lineaPrincipal === 'L2' ? 'rgba(136,136,136,0.3)' : 'rgba(227,0,27,0.3)',
                bgNormal: lineaPrincipal === 'L2' ? 'rgba(40,40,40,0.5)' : 'rgba(50,30,15,0.5)',
                border: lineaPrincipal === 'L2' ? 'rgba(136,136,136,0.25)' : 'rgba(227,0,27,0.25)'
            };

            let botonesHtml = '<div class="panel-fade-item" style="animation-delay: 0.3s; display: flex; gap: 8px; margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.06); align-items: stretch;">';
            
            const getBadges = (stationLines) => {
                return (stationLines || []).map(l => `<span style="background: ${l === 'L2' ? 'rgba(136,136,136,0.3)' : 'rgba(227,0,27,0.3)'}; color: ${l === 'L2' ? '#aaa' : '#ff4d4d'}; padding: 2px 6px; border-radius: 6px; font-size: 0.75em; font-weight: 700; margin-left: 6px;">${l}</span>`).join('');
            };

            // Left column (previous)
            botonesHtml += '<div style="display: flex; flex-direction: column; gap: 8px; flex: 1;">';
            if (prevList.length > 0) {
                prevList.forEach(p => {
                    botonesHtml += `<button onclick="seleccionarDesdeMetro('${p.id}')" onmouseover="this.style.background='${colores.bgHover}'" onmouseout="this.style.background='${colores.bgNormal}'" style="flex: 1; background: ${colores.bgNormal}; border: 1px solid ${colores.border}; color: #eee; padding: 10px; border-radius: 8px; cursor: pointer; transition: 0.2s; font-family: 'Inter'; font-size: 0.85em; text-align: left; display: flex; align-items: center; justify-content: space-between;"><span>&larr; ${p.nombre}</span> <div>${getBadges(p.lineas)}</div></button>`;
                });
            } else {
                botonesHtml += '<div style="flex: 1;"></div>';
            }
            botonesHtml += '</div>';

            // Right column (next)
            botonesHtml += '<div style="display: flex; flex-direction: column; gap: 8px; flex: 1;">';
            if (nextList.length > 0) {
                nextList.forEach(n => {
                    botonesHtml += `<button onclick="seleccionarDesdeMetro('${n.id}')" onmouseover="this.style.background='${colores.bgHover}'" onmouseout="this.style.background='${colores.bgNormal}'" style="flex: 1; background: ${colores.bgNormal}; border: 1px solid ${colores.border}; color: #eee; padding: 10px; border-radius: 8px; cursor: pointer; transition: 0.2s; font-family: 'Inter'; font-size: 0.85em; text-align: right; display: flex; align-items: center; justify-content: space-between;"><div>${getBadges(n.lineas)}</div> <span>${n.nombre} &rarr;</span></button>`;
                });
            } else {
                botonesHtml += '<div style="flex: 1;"></div>';
            }
            botonesHtml += '</div>';

            botonesHtml += '</div>';

            const now = new Date();
            const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const nivelesConcurrencia = [
                { texto: 'Poco concurrido', color: '#34b658', icon: '\uD83D\uDC64' },
                { texto: 'Normal', color: '#ffb74d', icon: '\uD83D\uDC65' },
                { texto: 'Muy concurrido', color: '#ff4757', icon: '\uD83D\uDE23' }
            ];
            const nivel = nivelesConcurrencia[estacion.nombre.length % 3];
            
            let colorInsignia = lineaPrincipal === 'L2' ? '#888888' : '#E3001B';
            let bgInsignia = lineaPrincipal === 'L2' ? 'rgba(136,136,136,0.12)' : 'rgba(227,0,27,0.12)';
            
            const lineasBadges = lineasEstacion.map(l => `<span style="background: ${l === 'L2' ? 'rgba(136,136,136,0.2)' : 'rgba(227,0,27,0.2)'}; color: ${l === 'L2' ? '#888888' : '#E3001B'}; padding: 2px 8px; border-radius: 10px; font-size: 0.7em; font-weight: 700;">${l}</span>`).join(' ');

            document.getElementById('contenido-parada').innerHTML = `
            <div class="panel-fade-item" style="animation-delay: 0.05s;">
                <div class="badge-linea" style="background: ${bgInsignia}; color: ${colorInsignia};">
                    METRO BILBAO ${lineasBadges}
                </div>
            </div>

            <div class="panel-fade-item estado-box" style="animation-delay: 0.15s; display: flex; flex-direction: column; gap: 12px; background: linear-gradient(135deg, rgba(20, 75, 45, 0.4) 0%, rgba(10, 45, 25, 0.2) 100%); border-color: rgba(52,182,88,0.25);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-size: 0.7em; color: #777; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Estado del servicio</div>
                        <div style="color: #34b658; font-weight: 600; font-size: 1.05em;">Operando con normalidad</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.7em; color: #777; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Actualizado</div>
                        <div style="color: #aaa; font-size: 0.85em; font-variant-numeric: tabular-nums;">Hoy, ${timeString}</div>
                    </div>
                </div>
                <div style="height: 1px; background: rgba(255,255,255,0.06); width: 100%; display: none;"></div>
                <div style="display: none;">
                    <div style="font-size: 0.7em; color: #777; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">Afluencia actual</div>
                    <div style="display: flex; align-items: center; gap: 8px; color: ${nivel.color}; font-size: 0.9em; font-weight: 600;">
                        <span style="font-size: 1.2em;">${nivel.icon}</span> ${nivel.texto}
                    </div>
                </div>
            </div>

            <div class="panel-fade-item" style="animation-delay: 0.25s;">
            <div class="panel-fade-item" style="animation-delay: 0.25s;">
                <div id="horarios-metro-container">
                    <h3 style="font-size: 0.85em; color: #fff; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px 0;">Próximas salidas</h3>
                    <div style="color: #aaa; font-size: 0.85em; font-style: italic;">Cargando horarios...</div>
                </div>
            </div>
            ${botonesHtml}
            `;

            fetch('/api/horarios_metro/' + estacion.id)
                .then(res => res.json())
                .then(salidas => {
                    const container = document.getElementById('horarios-metro-container');
                    if (!container) return; // Panel closed before fetch finished
                    if (!salidas || salidas.length === 0) {
                        container.innerHTML = '<h3 style="font-size: 0.85em; color: #fff; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px 0;">Próximas salidas</h3><div style="color: #aaa; font-size: 0.85em;">No hay salidas programadas para hoy.</div>';
                        return;
                    }
                    
                    window.salidasMetroCache = salidas;
                    
                    // Contenedor principal con buscador
                    const btnToggle = `<button onclick="document.body.classList.toggle('mostrar-hora')" style="background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.15); color: #ccc; padding: 6px 12px; border-radius: 20px; font-size: 0.75em; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer; transition: all 0.2s ease;" onmouseover="this.style.background='rgba(255,255,255,0.1)'; this.style.color='#fff'; this.style.borderColor='rgba(255,255,255,0.3)';" onmouseout="this.style.background='rgba(0,0,0,0.25)'; this.style.color='#ccc'; this.style.borderColor='rgba(255,255,255,0.15)';"><svg viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px; margin-top: -2px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>FORMATO</button>`;
                    const searchBar = `<input type="text" id="buscador-horarios-metro" placeholder="Buscar hora (ej. 16:05)..." onkeyup="renderHorariosMetro(this.value)" style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.2); color: #fff; margin-bottom: 12px; font-family: 'Inter'; font-size: 0.85em; box-sizing: border-box;">`;
                    
                    container.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center; margin: 0 0 12px 0;">
                            <h3 style="font-size: 0.85em; color: #fff; text-transform: uppercase; letter-spacing: 1px; margin: 0;">Horarios</h3>
                            ${btnToggle}
                        </div>
                        ${searchBar}
                        <div id="horarios-metro-list"></div>
                        <div style="margin-top: 16px;">
                        </div>
                    `;
                    
                    window.renderHorariosMetro();
                })
                .catch(err => {
                    console.error("Error fetching metro schedules", err);
                    const container = document.getElementById('horarios-metro-container');
                    if (container) container.innerHTML = '<h3 style="font-size: 0.85em; color: #fff; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px 0;">Próximas salidas</h3><div style="color: #ff4757; font-size: 0.85em;">Error al cargar horarios.</div>';
                });
        }
        
        window.renderHorariosMetro = function(query = '') {
            const listContainer = document.getElementById('horarios-metro-list');
            if (!listContainer || !window.salidasMetroCache) return;
            
            const salidas = window.salidasMetroCache;
            const q = query.trim().toLowerCase();
            const filtered = q ? salidas.filter(s => s.hora_exacta.includes(q)) : salidas;
            
            const renderGrupo = (grupoSalidas) => {
                return grupoSalidas.map(s => {
                    let claseColor = s.minutos <= 3 ? 'inminente' : (s.minutos <= 10 ? 'proximo' : 'lejano');
                    let styleColor = s.minutos <= 3 ? 'color: #e2231a;' : '';
                    let badgeLinea = `<div style="display: inline-flex; align-items: center; justify-content: center; width: 1.8em; height: 1.8em; background: #e2231a; color: white; border-radius: 50%; font-weight: bold; font-size: 0.85em; letter-spacing: -0.5px;">L1</div>`;
                    let colorLinea = '#e2231a';
                    let nombreLinea = 'Línea 1';
                    
                    if (s.linea === 'L2') {
                        badgeLinea = `<div style="display: inline-flex; align-items: center; justify-content: center; width: 1.8em; height: 1.8em; background: #222222; color: white; border-radius: 50%; font-weight: bold; font-size: 0.85em; letter-spacing: -0.5px;">L2</div>`;
                        colorLinea = '#888888';
                        nombreLinea = 'Línea 2';
                    } else {
                        badgeLinea = `<div style="display: inline-flex; align-items: center; justify-content: center; width: 1.8em; height: 1.8em; background: #e2231a; color: white; border-radius: 50%; font-weight: bold; font-size: 0.85em; letter-spacing: -0.5px;">L1</div>`;
                        colorLinea = '#e2231a';
                        nombreLinea = 'Línea 1';
                    }

                    return `
                    <div class="horario-item">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="width: 4px; height: 28px; border-radius: 2px; background: ${colorLinea};"></div>
                            <div>
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    ${badgeLinea}
                                    <span style="font-weight: 600; font-size: 0.9em; color:#fff;">${nombreLinea}</span>
                                </div>
                                <div style="font-size: 0.75em; color: #aaa; margin-top: 4px;">Hacia ${s.destino}</div>
                            </div>
                        </div>
                        <span class="tiempo-llegada ${claseColor}" style="${styleColor}">
                            <span class="solo-minutos">${s.minutos} min</span>
                            <span class="solo-hora">${s.hora_exacta || '--:--'}</span>
                        </span>
                    </div>
                    `;
                }).join('');
            };

            const salidas0 = filtered.filter(s => s.direccion === "0");
            const salidas1 = filtered.filter(s => s.direccion === "1");

            let htmlFinal = '';
            if (salidas0.length > 0) {
                htmlFinal += '<div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px; margin-bottom: 16px; border: 1px solid rgba(255,255,255,0.05); box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);">';
                htmlFinal += '<h3 style="font-size: 0.75em; color: #888; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">Próximas salidas</h3>';
                htmlFinal += '<div style="max-height: 180px; overflow-y: auto; padding-right: 8px; display: flex; flex-direction: column; gap: 8px;">' + renderGrupo(salidas0) + '</div>';
                htmlFinal += '</div>';
            }
            if (salidas1.length > 0) {
                htmlFinal += '<div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px; margin-bottom: 16px; border: 1px solid rgba(255,255,255,0.05); box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);">';
                htmlFinal += '<h3 style="font-size: 0.75em; color: #888; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">Próximas llegadas</h3>';
                htmlFinal += '<div style="max-height: 180px; overflow-y: auto; padding-right: 8px; display: flex; flex-direction: column; gap: 8px;">' + renderGrupo(salidas1) + '</div>';
                htmlFinal += '</div>';
            }
            if (salidas0.length === 0 && salidas1.length === 0) {
                htmlFinal = '<div style="color: #aaa; font-size: 0.85em; padding: 12px 0;">No se encontraron horarios para esa búsqueda.</div>';
            }

            listContainer.innerHTML = htmlFinal;
        };

        window.seleccionarDesdeMetro = function(id) {
            if (!metroL1Activo && !metroL2Activo) toggleMetro('L1');
            const estacion = todasLasEstacionesMetro.find(e => e.id === id);
            const marker = marcadoresMetroPorId[id];
            setTimeout(() => {
                if (estacion && marker) abrirPanelMetro(estacion, marker, 18);
            }, 50);
        };

        function crearIconoEstacion(nombre) {
            return L.divIcon({
                className: '', iconSize: [16, 16], iconAnchor: [8, 8],
                html: `
                    <div class="estacion-marker">
                        <div class="pulso"></div>
                        <div class="pulso2"></div>
                        <img src="/static/euskotren.svg" class="punto-svg" alt="Stop">
                        <div class="tooltip-estacion">${svgTranvia}${nombre}</div>
                    </div>
                `
            });
        }

        function seleccionarMarcador(marker) {
            if (marcadorSeleccionado) {
                const prevEl = marcadorSeleccionado.getElement();
                if (prevEl) prevEl.querySelector('.estacion-marker')?.classList.remove('seleccionado');
            }
            marcadorSeleccionado = marker;
            const el = marker.getElement();
            if (el) el.querySelector('.estacion-marker')?.classList.add('seleccionado');
        }

        function deseleccionarTodos() {
            if (marcadorSeleccionado) {
                const el = marcadorSeleccionado.getElement();
                if (el) el.querySelector('.estacion-marker')?.classList.remove('seleccionado');
                marcadorSeleccionado = null;
            }
        }

        function abrirPanel(estacion, marker, zoomNivel = 18) {
            seleccionarMarcador(marker);

            // Centrado suave
            map.flyTo([estacion.latitud, estacion.longitud], zoomNivel, { duration: 0.8, easeLinearity: 0.4 });

            // Reiniciamos posición si estaba arrastrado
            xOffset = 0; yOffset = 0;
            panel.style.transform = '';
            
            panel.style.background = 'linear-gradient(145deg, rgba(16, 42, 28, 0.85) 0%, rgba(10, 22, 16, 0.9) 100%)';
            panel.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            
            panel.classList.add('abierto');
            
            document.getElementById('panel-titulo').innerHTML = `${svgTranvia}${estacion.nombre}`;

            const currentIndex = todasLasEstaciones.findIndex(e => e.id === estacion.id);
            const prevEstacion = currentIndex > 0 ? todasLasEstaciones[currentIndex - 1] : null;
            const nextEstacion = currentIndex < todasLasEstaciones.length - 1 ? todasLasEstaciones[currentIndex + 1] : null;

            let botonesHtml = '<div class="panel-fade-item" style="animation-delay: 0.3s; display: flex; gap: 8px; margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.06);">';
            if (prevEstacion) {
                botonesHtml += `<button onclick="seleccionarDesdeBuscador('${prevEstacion.id}')" onmouseover="this.style.background='rgba(52,182,88,0.3)'" onmouseout="this.style.background='rgba(20,50,30,0.5)'" style="flex: 1; background: rgba(20,50,30,0.5); border: 1px solid rgba(52,182,88,0.25); color: #eee; padding: 10px; border-radius: 8px; cursor: pointer; transition: 0.2s; font-family: 'Inter'; font-size: 0.85em; text-align: left; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">&larr; ${prevEstacion.nombre}</button>`;
            } else {
                botonesHtml += `<div style="flex: 1;"></div>`;
            }
            if (nextEstacion) {
                botonesHtml += `<button onclick="seleccionarDesdeBuscador('${nextEstacion.id}')" onmouseover="this.style.background='rgba(52,182,88,0.3)'" onmouseout="this.style.background='rgba(20,50,30,0.5)'" style="flex: 1; background: rgba(20,50,30,0.5); border: 1px solid rgba(52,182,88,0.25); color: #eee; padding: 10px; border-radius: 8px; cursor: pointer; transition: 0.2s; font-family: 'Inter'; font-size: 0.85em; text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${nextEstacion.nombre} &rarr;</button>`;
            } else {
                botonesHtml += `<div style="flex: 1;"></div>`;
            }
            botonesHtml += '</div>';

            const now = new Date();
            const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            const nivelesConcurrencia = [
                { texto: 'Poco concurrido', color: '#34b658', icon: '<svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: text-bottom; margin-right: 4px;"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>' },
                { texto: 'Normal', color: '#ffb74d', icon: '<svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: text-bottom; margin-right: 4px;"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>' },
                { texto: 'Muy concurrido', color: '#ff4757', icon: '<svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: text-bottom; margin-right: 4px;"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>' }
            ];
            const nivel = nivelesConcurrencia[estacion.nombre.length % 3];

            document.getElementById('contenido-parada').innerHTML = `
            <div class="panel-fade-item" style="animation-delay: 0.05s;">
                <div class="badge-linea">
                    ${svgTranvia}
                    TRANVÍA BILBAO
                </div>
            </div>

            <div class="panel-fade-item estado-box" style="animation-delay: 0.15s; display: flex; flex-direction: column; gap: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-size: 0.7em; color: #777; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Estado del servicio</div>
                        <div style="color: #34b658; font-weight: 600; font-size: 1.05em;">Operando con normalidad</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.7em; color: #777; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Actualizado</div>
                        <div style="color: #aaa; font-size: 0.85em; font-variant-numeric: tabular-nums;">Hoy, ${timeString}</div>
                    </div>
                </div>
                
                <div style="height: 1px; background: rgba(255,255,255,0.06); width: 100%; display: none;"></div>
                <div style="display: none;">
                    <div style="font-size: 0.7em; color: #777; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">Afluencia actual</div>
                    <div style="display: flex; align-items: center; gap: 8px; color: ${nivel.color}; font-size: 0.9em; font-weight: 600;">
                        <span style="font-size: 1.2em;">${nivel.icon}</span> ${nivel.texto}
                    </div>
                </div>
            </div>

            <!-- Próximas salidas -->
            <div class="panel-fade-item" style="animation-delay: 0.25s;">
                <div id="horarios-tranvia-container">
                    <h3 style="font-size: 0.85em; color: #fff; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px 0;">Horarios</h3>
                    <div style="color: #aaa; font-size: 0.85em; font-style: italic;">Cargando horarios...</div>
                </div>
            </div>
            ${botonesHtml}
            `;

            fetch('/api/horarios_tranvia/' + estacion.id)
                .then(res => res.json())
                .then(salidas => {
                    const container = document.getElementById('horarios-tranvia-container');
                    if (!container) return; // Panel closed before fetch finished
                    if (!salidas || salidas.length === 0) {
                        container.innerHTML = '<h3 style="font-size: 0.85em; color: #fff; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px 0;">Horarios</h3><div style="color: #aaa; font-size: 0.85em;">No hay salidas programadas para hoy.</div>';
                        return;
                    }
                    
                    window.salidasTranviaCache = salidas;
                    
                    const btnToggle = `<button onclick="document.body.classList.toggle('mostrar-hora')" style="background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.15); color: #ccc; padding: 6px 12px; border-radius: 20px; font-size: 0.75em; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer; transition: all 0.2s ease;" onmouseover="this.style.background='rgba(255,255,255,0.1)'; this.style.color='#fff'; this.style.borderColor='rgba(255,255,255,0.3)';" onmouseout="this.style.background='rgba(0,0,0,0.25)'; this.style.color='#ccc'; this.style.borderColor='rgba(255,255,255,0.15)';"><svg viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px; margin-top: -2px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>FORMATO</button>`;
                    const searchBar = `<input type="text" id="buscador-horarios-tranvia" placeholder="Buscar hora (ej. 16:05)..." onkeyup="renderHorariosTranvia(this.value)" style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.2); color: #fff; margin-bottom: 12px; font-family: 'Inter'; font-size: 0.85em; box-sizing: border-box;">`;
                    
                    container.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center; margin: 0 0 12px 0;">
                            <h3 style="font-size: 0.85em; color: #fff; text-transform: uppercase; letter-spacing: 1px; margin: 0;">Horarios</h3>
                            ${btnToggle}
                        </div>
                        ${searchBar}
                        <div id="horarios-tranvia-list"></div>
                        <div style="margin-top: 16px;">
                        </div>
                    `;
                    
                    window.renderHorariosTranvia();
                })
                .catch(err => {
                    console.error("Error fetching tranvia schedules", err);
                    const container = document.getElementById('horarios-tranvia-container');
                    if (container) container.innerHTML = '<h3 style="font-size: 0.85em; color: #fff; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px 0;">Horarios</h3><div style="color: #ff4757; font-size: 0.85em;">Error al cargar horarios.</div>';
                });
        }
        
        window.renderHorariosTranvia = function(query = '') {
            const listContainer = document.getElementById('horarios-tranvia-list');
            if (!listContainer || !window.salidasTranviaCache) return;
            
            const salidas = window.salidasTranviaCache;
            const q = query.trim().toLowerCase();
            const filtered = q ? salidas.filter(s => s.hora_exacta.includes(q)) : salidas;
            
            const renderGrupo = (grupoSalidas) => {
                return grupoSalidas.map(s => {
                    let claseColor = s.minutos <= 3 ? 'inminente' : (s.minutos <= 10 ? 'proximo' : 'lejano');
                    let styleColor = s.minutos <= 3 ? 'color: #34b658;' : '';
                    let colorLinea = '#34b658';
                    let nombreLinea = 'Línea TR';
                    
                    return `
                    <div class="horario-item">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="width: 4px; height: 28px; border-radius: 2px; background: ${colorLinea};"></div>
                            <div>
                                <div style="font-weight: 600; font-size: 0.9em; color:#fff;">${nombreLinea}</div>
                                <div style="font-size: 0.75em; color: #aaa;">Hacia ${s.destino}</div>
                            </div>
                        </div>
                        <span class="tiempo-llegada ${claseColor}" style="${styleColor}">
                            <span class="solo-minutos">${s.minutos} min</span>
                            <span class="solo-hora">${s.hora_exacta || '--:--'}</span>
                        </span>
                    </div>
                    `;
                }).join('');
            };

            const salidas0 = filtered.filter(s => s.direccion === "0");
            const salidas1 = filtered.filter(s => s.direccion === "1");

            let htmlFinal = '';
            if (salidas0.length > 0) {
                htmlFinal += '<div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px; margin-bottom: 16px; border: 1px solid rgba(255,255,255,0.05); box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);">';
                htmlFinal += '<h3 style="font-size: 0.75em; color: #888; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">Próximas salidas</h3>';
                htmlFinal += '<div style="max-height: 180px; overflow-y: auto; padding-right: 8px; display: flex; flex-direction: column; gap: 8px;">' + renderGrupo(salidas0) + '</div>';
                htmlFinal += '</div>';
            }
            if (salidas1.length > 0) {
                htmlFinal += '<div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 12px; margin-bottom: 16px; border: 1px solid rgba(255,255,255,0.05); box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);">';
                htmlFinal += '<h3 style="font-size: 0.75em; color: #888; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">Próximas llegadas</h3>';
                htmlFinal += '<div style="max-height: 180px; overflow-y: auto; padding-right: 8px; display: flex; flex-direction: column; gap: 8px;">' + renderGrupo(salidas1) + '</div>';
                htmlFinal += '</div>';
            }
            if (salidas0.length === 0 && salidas1.length === 0) {
                htmlFinal = '<div style="color: #aaa; font-size: 0.85em; padding: 12px 0;">No se encontraron horarios para esa búsqueda.</div>';
            }

            listContainer.innerHTML = htmlFinal;
        }

        function cerrarPanel() {
            panel.classList.remove('abierto');
            deseleccionarTodos();
            
            // Retornamos el panel a su posición original suavemente
            setTimeout(() => {
                xOffset = 0; yOffset = 0;
                panel.style.transform = '';
            }, 300);
        }

        // ═══════════════════════════════════
        // 5. Buscador de Estaciones
        // ═══════════════════════════════════
        const inputBuscador = document.getElementById('buscador-estaciones');
        const divResultados = document.getElementById('resultados-busqueda');

        inputBuscador.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            if (query.length < 2) { divResultados.style.display = 'none'; return; }
            
            const resTranvia = todasLasEstaciones.filter(e => e.nombre.toLowerCase().includes(query)).map(e => ({
                id: e.id, nombre: e.nombre, tipo: 'tranvia'
            }));
            const resMetro = todasLasEstacionesMetro.filter(e => e.nombre.toLowerCase().includes(query)).map(e => ({
                id: e.id, nombre: e.nombre, tipo: 'metro'
            }));
            const resultados = [...resTranvia, ...resMetro];
            
            if (resultados.length > 0) {
                divResultados.innerHTML = resultados.map(e => {
                    if (e.tipo === 'metro') {
                        return `<div class="resultado-item" onclick="seleccionarDesdeMetro('${e.id}')">${svgMetro}${e.nombre}</div>`;
                    }
                    return `<div class="resultado-item" onclick="seleccionarDesdeBuscador('${e.id}')">${svgTranvia}${e.nombre}</div>`;
                }).join('');
                divResultados.style.display = 'block';
            } else {
                divResultados.style.display = 'none';
            }
        });

        window.seleccionarDesdeBuscador = function(id) {
            if (!tranviaActivo) toggleTranvia(); // Auto-activar si estaba apagado
            
            const estacion = todasLasEstaciones.find(e => e.id === id);
            const marker = marcadoresPorId[id];
            
            setTimeout(() => {
                if (estacion && marker) {
                    abrirPanel(estacion, marker, 18); // Mayor zoom desde el buscador
                    inputBuscador.value = '';
                    divResultados.style.display = 'none';
                }
            }, 50);
        };

        // Cerrar resultados si se hace click fuera
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.seccion-buscador')) {
                divResultados.style.display = 'none';
            }
        });

        // ═══════════════════════════════════
        // 6. Carga de datos y "Snapping" matemático
        // ═══════════════════════════════════
        Promise.all([
            fetch('/api/estaciones').then(r => r.json()),
            fetch('/static/tranviabilbao.geojson').then(r => r.json())
        ]).then(([estaciones, datosGeojson]) => {
            
            // 1. Cargar Línea
            const capaGlow = L.geoJSON(datosGeojson, { style: { color: '#34b658', weight: 10, opacity: 0.15, lineJoin: 'round', lineCap: 'round' } });
            const capaLinea = L.geoJSON(datosGeojson, { style: { color: '#34b658', weight: 4, opacity: 0.9, lineJoin: 'round', lineCap: 'round' } });
            grupoLinea.addLayer(capaGlow);
            grupoLinea.addLayer(capaLinea);
            window.tramosVias = [];
            datosGeojson.features.forEach(feature => {
                if (feature.geometry.type === 'LineString') {
                    window.tramosVias.push(feature.geometry.coordinates);
                } else if (feature.geometry.type === 'MultiLineString') {
                    feature.geometry.coordinates.forEach(c => window.tramosVias.push(c));
                }
            });

            // 2. Limpiar duplicados y ajustar a la vía completa (107 tramos)
            const unicas = new Map();
            estaciones.forEach(e => {
                if (!unicas.has(e.nombre)) {
                    const p = [e.longitud, e.latitud];
                    let mejorPunto = p;
                    let minimaDistSq = Infinity;
                    
                    datosGeojson.features.forEach(feature => {
                        let lineas = [];
                        if (feature.geometry.type === 'LineString') {
                            lineas = [feature.geometry.coordinates];
                        } else if (feature.geometry.type === 'MultiLineString') {
                            lineas = feature.geometry.coordinates;
                        }
                        
                        lineas.forEach(coords => {
                            for(let i = 0; i < coords.length - 1; i++) {
                                const proj = window.proyectarPuntoEnSegmento(p, coords[i], coords[i+1]);
                                const distSq = (p[0]-proj[0])**2 + (p[1]-proj[1])**2;
                                if (distSq < minimaDistSq) {
                                    minimaDistSq = distSq;
                                    mejorPunto = proj;
                                }
                            }
                        });
                    });
                    
                    // Actualizamos coordenadas con precisión milimétrica
                    e.longitud = mejorPunto[0];
                    e.latitud = mejorPunto[1];
                    
                    unicas.set(e.nombre, e);
                }
            });

            const ORDEN_ESTACIONES = [
                "Bolueta", "Abusu", "Atxuri", "Ribera", "Arriaga", 
                "Abando", "Pío Baroja", "Pio Baroja", "Uribitarte", "Guggenheim", "Abandoibarra", "Euskalduna", 
                "Sabino Arana", "San Mamés", "San Mames", "Ospitalea", "Basurto", "La Casilla"
            ];
            
            todasLasEstaciones = Array.from(unicas.values());
            todasLasEstaciones.sort((a, b) => {
                const norm = (s) => s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
                const getIndex = (nombre) => {
                    let n1 = norm(nombre);
                    let idx = ORDEN_ESTACIONES.findIndex(n => norm(n) === n1);
                    if (idx !== -1) return idx;
                    idx = ORDEN_ESTACIONES.findIndex(n => {
                        let n2 = norm(n);
                        if (n2 === "abando" && n1.includes("abandoibarra")) return false;
                        return n1.includes(n2);
                    });
                    return idx !== -1 ? idx : 999;
                };
                return getIndex(a.nombre) - getIndex(b.nombre);
            });

            // 3. Crear los marcadores
            todasLasEstaciones.forEach(estacion => {
                const icono = crearIconoEstacion(estacion.nombre);
                const marker = L.marker([estacion.latitud, estacion.longitud], { icon: icono })
                    .on('click', (ev) => {
                        L.DomEvent.stopPropagation(ev);
                        abrirPanel(estacion, marker);
                    });
                todosLosMarcadores.push(marker);
                marcadoresPorId[estacion.id] = marker;
                grupoMarcadores.addLayer(marker);
            });
            
            // 4. Iniciar WebSockets
            // initWebSockets();
        });

        // ═══════════════════════════════════
        // 7. Carga de datos Metro Bilbao
        // ═══════════════════════════════════
        Promise.all([
            fetch('/api/estaciones_metro').then(r => r.json()),
            fetch('/static/metrobilbao.geojson').then(r => r.json())
        ]).then(([estacionesMetro, datosGeojsonMetro]) => {
            
            // 1. Cargar Líneas Metro
            window.capasLineasMetro = [];
            datosGeojsonMetro.features.forEach(feature => {
                const isL1 = feature.properties.name.includes('L1');
                const glow = L.geoJSON(feature, { 
                    style: { color: feature.properties.color, weight: 10, opacity: 0.15, lineJoin: 'round', lineCap: 'round' }
                });
                const line = L.geoJSON(feature, { 
                    style: { color: feature.properties.color, weight: 4, opacity: 0.9, lineJoin: 'round', lineCap: 'round' }
                });
                window.capasLineasMetro.push({ feature, glow, line, isL1, isL2: !isL1 });
            });

            // Store tramos for snapping
            window.tramosViasMetro = [];
            datosGeojsonMetro.features.forEach(feature => {
                if (feature.geometry.type === 'LineString') {
                    window.tramosViasMetro.push(feature.geometry.coordinates);
                } else if (feature.geometry.type === 'MultiLineString') {
                    feature.geometry.coordinates.forEach(c => window.tramosViasMetro.push(c));
                }
            });

            // 2. Snap stations to lines and deduplicate
            const unicasMetro = new Map();
            estacionesMetro.forEach(e => {
                if (!unicasMetro.has(e.nombre)) {
                    const p = [e.longitud, e.latitud];
                    let mejorPunto = p;
                    let minimaDistSq = Infinity;
                    window.tramosViasMetro.forEach(coords => {
                        for(let i = 0; i < coords.length - 1; i++) {
                            const proj = window.proyectarPuntoEnSegmento(p, coords[i], coords[i+1]);
                            const distSq = (p[0]-proj[0])**2 + (p[1]-proj[1])**2;
                            if (distSq < minimaDistSq) { minimaDistSq = distSq; mejorPunto = proj; }
                        }
                    });
                    e.longitud = mejorPunto[0];
                    e.latitud = mejorPunto[1];
                    unicasMetro.set(e.nombre, e);
                } else {
                    const existente = unicasMetro.get(e.nombre);
                    if (e.lineas && Array.isArray(e.lineas)) {
                        e.lineas.forEach(l => {
                            if (!existente.lineas.includes(l)) existente.lineas.push(l);
                        });
                    }
                    if (e.orden_l1 < 999) existente.orden_l1 = e.orden_l1;
                    if (e.orden_l2 < 999) existente.orden_l2 = e.orden_l2;
                }
            });

            todasLasEstacionesMetro = Array.from(unicasMetro.values());
            todasLasEstacionesMetro.sort((a, b) => a.nombre.localeCompare(b.nombre, 'es', { sensitivity: 'base' }));

            // 3. Create markers
            todasLasEstacionesMetro.forEach(estacion => {
                const icono = crearIconoEstacionMetro(estacion.nombre, estacion.lineas);
                const marker = L.marker([estacion.latitud, estacion.longitud], { icon: icono })
                    .on('click', (ev) => {
                        L.DomEvent.stopPropagation(ev);
                        abrirPanelMetro(estacion, marker);
                    });
                todosLosMarcadoresMetro.push(marker);
                marcadoresMetroPorId[estacion.id] = marker;
            });
            
            // Trigger visibility
            window.toggleMetro('UPDATE');

            // --- CALCULADORA DE TARIFAS ---
            let tarifaOrigen = null;
            let tarifaDestino = null;
            let tarjetaSel = 'creditrans';

            const getZona = (nombre) => {
                const z3 = ['Sopela', 'Urduliz', 'Plentzia'];
                const z1 = ['Bolueta', 'Basarrate', 'Santutxu', 'Casco Viejo', 'Abando', 'Moyua', 'Indautxu', 'San Mamés', 'Deusto', 'Sarriko', 'San Inazio'];
                if (z3.some(z => nombre.includes(z))) return 3;
                if (z1.some(z => nombre.includes(z))) return 1;
                return 2; // Default for everything else (Zone 2)
            };

            window.toggleCustomSelect = function(id) {
                const sel = document.getElementById('c-' + id);
                const isOpen = sel.classList.contains('open');
                document.querySelectorAll('.c-select').forEach(el => el.classList.remove('open'));
                if (!isOpen) {
                    sel.classList.add('open');
                    const searchInput = document.getElementById('c-' + id + '-search');
                    if(searchInput) searchInput.focus();
                }
            };
            
            window.seleccionarTarjeta = function(val, nombre, img) {
                tarjetaSel = val;
                document.getElementById('c-tarjeta-val').innerHTML = `<img src="${img}" style="height:14px; vertical-align: middle; margin-right:6px">${nombre}`;
                document.getElementById('c-tarjeta').classList.remove('open');
                calcularTarifa();
            };
            
            const seleccionarEstacionTarifa = (tipo, id, nombre, esTranvia) => {
                if (tipo === 'origen') {
                    tarifaOrigen = { id, nombre, esTranvia, zona: getZona(nombre) };
                    document.getElementById('c-origen-val').innerHTML = (esTranvia ? svgTranvia : svgMetro) + ' ' + nombre;
                } else {
                    tarifaDestino = { id, nombre, esTranvia, zona: getZona(nombre) };
                    document.getElementById('c-destino-val').innerHTML = (esTranvia ? svgTranvia : svgMetro) + ' ' + nombre;
                }
                document.getElementById('c-' + tipo).classList.remove('open');
                calcularTarifa();
            };

            const renderCustomOptions = (tipo, query = '') => {
                const list = document.getElementById(`c-${tipo}-list`);
                if (!list) return;
                list.innerHTML = '';
                
                const filtradas = todasLasEstaciones.filter(e => e.nombre.toLowerCase().includes(query));
                
                filtradas.forEach(e => {
                    const opt = document.createElement('div');
                    opt.className = 'c-option';
                    const icon = e.id.startsWith('metro_') ? svgMetro : svgTranvia;
                    const isTranvia = !e.id.startsWith('metro_');
                    opt.innerHTML = icon + ' ' + e.nombre;
                    opt.onclick = () => seleccionarEstacionTarifa(tipo, e.id, e.nombre, isTranvia);
                    list.appendChild(opt);
                });
            };
            
            document.getElementById('c-origen-search')?.addEventListener('input', e => renderCustomOptions('origen', e.target.value.toLowerCase()));
            document.getElementById('c-destino-search')?.addEventListener('input', e => renderCustomOptions('destino', e.target.value.toLowerCase()));
            
            // Initial render
            setTimeout(() => {
                renderCustomOptions('origen');
                renderCustomOptions('destino');
            }, 1000);

            // Close on click outside
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.c-select')) {
                    document.querySelectorAll('.c-select').forEach(el => el.classList.remove('open'));
                }
            });

            const calcularTarifa = () => {
                const resultadoDiv = document.getElementById('tarifa-resultado');
                const precioEl = document.getElementById('tarifa-precio');
                const zonasEl = document.getElementById('tarifa-zonas');

                if (!tarifaOrigen || !tarifaDestino) {
                    resultadoDiv.style.display = 'none';
                    return;
                }

                let precio = 0;
                
                // Si ambos son del tranvía (o alguno) y es un recorrido solo tranvía, o simplemente si hay tranvía involucrado
                // Según la política solicitada: Tarifa plana tranvía
                if (tarifaOrigen.esTranvia || tarifaDestino.esTranvia) {
                    if (tarjetaSel === 'ocasional') precio = 2.00;
                    else if (tarjetaSel === 'creditrans') precio = 0.74;
                    else if (tarjetaSel === 'gizatrans') precio = 0.42;
                    
                    precioEl.textContent = precio.toFixed(2) + ' €';
                    zonasEl.textContent = 'Tarifa Plana (Tranvía)';
                    resultadoDiv.style.display = 'block';
                    return;
                }

                let saltos = Math.abs(tarifaDestino.zona - tarifaOrigen.zona);
                let numZonas = saltos + 1;

                if (tarjetaSel === 'ocasional') {
                    if (numZonas === 1) precio = 1.70;
                    else if (numZonas === 2) precio = 1.90;
                    else precio = 1.95;
                } else if (tarjetaSel === 'creditrans') {
                    if (numZonas === 1) precio = 0.48;
                    else if (numZonas === 2) precio = 0.57;
                    else precio = 0.61;
                } else if (tarjetaSel === 'gizatrans') {
                    precio = 0.35;
                }

                precioEl.textContent = precio.toFixed(2) + ' €';
                zonasEl.textContent = numZonas === 1 ? '1 Zona' : numZonas + ' Zonas';
                resultadoDiv.style.display = 'block';
            };

                // --- ENRUTAMIENTO MICROROUTING ---
                const btnRuta = document.getElementById('btn-buscar-ruta');
                btnRuta.addEventListener('click', () => {
                    if (!tarifaOrigen || !tarifaDestino) {
                        alert("Por favor, selecciona origen y destino primero.");
                        return;
                    }
                    
                    const idOrigen = tarifaOrigen.id;
                    const idDestino = tarifaDestino.id;

                    if (!idOrigen || !idDestino) return;

                    btnRuta.textContent = "CALCULANDO...";
                    fetch(`/api/ruta?origen=${idOrigen}&destino=${idDestino}`)
                        .then(res => res.json())
                        .then(data => {
                            btnRuta.textContent = "CALCULAR RUTA MICROROUTING";
                            if (data.error) {
                                alert("Error: " + data.error);
                                return;
                            }
                            
                            document.getElementById('ruta-resultado').style.display = 'block';
                            document.getElementById('rt-tren').textContent = Math.round(data.tiempo_tren_s / 60) + " min";
                            document.getElementById('rt-pie').textContent = Math.round(data.tiempo_peatonal_s / 60) + " min";
                            
                            const stepsDiv = document.getElementById('ruta-steps');
                            stepsDiv.innerHTML = '';
                            
                            let tiempoTotalPieS = 0;
                            let tiempoTotalTrenS = 0;
                            
                            data.segmentos.forEach((seg, i) => {
                                const el = document.createElement('div');
                                el.style.marginBottom = '6px';
                                el.style.paddingBottom = '6px';
                                el.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
                                
                                let action = '';
                                if (seg.detalle.tipo === 'tren') {
                                    action = `<span style="color: #34b658">🚆 Tren (${seg.detalle.linea})</span>: ${Math.round(seg.detalle.tiempo/60)} min`;
                                    tiempoTotalTrenS += seg.detalle.tiempo;
                                } else if (seg.detalle.tipo === 'peatonal') {
                                    action = `<span style="color: #f39c12">🚶 Pie</span>: ${Math.round(seg.detalle.tiempo)} segs ${seg.detalle.is_steps ? '(Escaleras/Pendiente)' : ''}`;
                                    tiempoTotalPieS += seg.detalle.tiempo;
                                } else {
                                    action = `<span style="color: #3498db">🔗 Enlace</span>: ${Math.round(seg.detalle.tiempo)} segs`;
                                    tiempoTotalPieS += seg.detalle.tiempo;
                                }
                                
                                const rutaText = `<div style="color: #a4b0be; font-size: 0.9em; margin-top: 4px;">${seg.desde_nombre} &rarr; ${seg.hasta_nombre}</div>`;
                                el.innerHTML = `<strong>Paso ${i+1}:</strong> ${action}${rutaText}`;
                                stepsDiv.appendChild(el);
                            });
                            
                            document.getElementById('rt-tren').textContent = Math.round(tiempoTotalTrenS / 60) + " min";
                            document.getElementById('rt-pie').textContent = Math.round(tiempoTotalPieS / 60) + " min";
                        })
                        .catch(err => {
                            btnRuta.textContent = "CALCULAR RUTA MICROROUTING";
                            console.error(err);
                            alert("Error de conexión con el enrutador híbrido.");
                        });
                });
            
        });

        window.vehiculosMarkers = {};
        function initWebSockets() {
            const wsUrl = (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws/posiciones';
            const socket = new WebSocket(wsUrl);

            socket.onmessage = function(event) {
                const mensaje = JSON.parse(event.data);
                if (mensaje.tipo === 'posiciones') {
                    mensaje.datos.forEach(vehiculo => {
                        let p = [vehiculo.lon, vehiculo.lat];
                        let mejorPunto = p;
                        
                        // Snapping a las vías para los tranvías simulados
                        if (window.tramosVias && window.proyectarPuntoEnSegmento) {
                            let minimaDistSq = Infinity;
                            window.tramosVias.forEach(coords => {
                                for(let i = 0; i < coords.length - 1; i++) {
                                    const proj = window.proyectarPuntoEnSegmento(p, coords[i], coords[i+1]);
                                    const distSq = (p[0]-proj[0])**2 + (p[1]-proj[1])**2;
                                    if (distSq < minimaDistSq) {
                                        minimaDistSq = distSq;
                                        mejorPunto = proj;
                                    }
                                }
                            });
                        }
                        
                        let vehLat = mejorPunto[1];
                        let vehLon = mejorPunto[0];

                        if (!vehiculosMarkers[vehiculo.id]) {
                            const vehiculoIcon = L.divIcon({
                                className: 'vehiculo-marker',
                                html: `<div class="vehiculo-punto"></div>
                                       <div class="vehiculo-tooltip">${vehiculo.id}<br><span style="font-size:0.8em;color:#aaa;">→ ${vehiculo.destino}</span></div>`,
                                iconSize: [16, 16],
                                iconAnchor: [8, 8]
                            });
                            const marker = L.marker([vehLat, vehLon], { icon: vehiculoIcon, zIndexOffset: 1000 });
                            marker.vehiculoData = vehiculo;
                            vehiculosMarkers[vehiculo.id] = marker;
                            
                            if (tranviaActivo) marker.addTo(map);
                        } else {
                            const marker = vehiculosMarkers[vehiculo.id];
                            marker.vehiculoData = vehiculo;
                            marker.setLatLng([vehLat, vehLon]);
                            marker.getElement().querySelector('.vehiculo-tooltip').innerHTML = `${vehiculo.id}<br><span style="font-size:0.8em;color:#aaa;">→ ${vehiculo.destino}</span>`;
                            
                            if (tranviaActivo && !map.hasLayer(marker)) map.addLayer(marker);
                            if (!tranviaActivo && map.hasLayer(marker)) map.removeLayer(marker);
                        }
                    });
                }
                if (mensaje.tipo === 'posiciones_metro') {
                    mensaje.datos.forEach(vehiculo => {
                        let p = [vehiculo.lon, vehiculo.lat];
                        let mejorPunto = p;
                        
                        if (window.tramosViasMetro && window.proyectarPuntoEnSegmento) {
                            let minimaDistSq = Infinity;
                            window.tramosViasMetro.forEach(coords => {
                                for(let i = 0; i < coords.length - 1; i++) {
                                    const proj = window.proyectarPuntoEnSegmento(p, coords[i], coords[i+1]);
                                    const distSq = (p[0]-proj[0])**2 + (p[1]-proj[1])**2;
                                    if (distSq < minimaDistSq) { minimaDistSq = distSq; mejorPunto = proj; }
                                }
                            });
                        }
                        let vehLat = mejorPunto[1];
                        let vehLon = mejorPunto[0];

                        if (!vehiculosMarkers[vehiculo.id]) {
                            const claseLinea = vehiculo.linea === 'L2' ? 'l2' : 'l1';
                            const vehiculoIcon = L.divIcon({
                                className: 'vehiculo-marker',
                                html: `<div class="vehiculo-punto-metro ${claseLinea}"></div>
                                       <div class="vehiculo-tooltip">${vehiculo.id}<br><span style="font-size:0.8em;color:#aaa;">→ ${vehiculo.destino}</span></div>`,
                                iconSize: [16, 16],
                                iconAnchor: [8, 8]
                            });
                            const marker = L.marker([vehLat, vehLon], { icon: vehiculoIcon, zIndexOffset: 1000 });
                            marker.vehiculoData = vehiculo;
                            vehiculosMarkers[vehiculo.id] = marker;
                            
                            const show = (vehiculo.linea === 'L1' && metroL1Activo) || (vehiculo.linea === 'L2' && metroL2Activo);
                            if (show) marker.addTo(map);
                        } else {
                            const marker = vehiculosMarkers[vehiculo.id];
                            marker.vehiculoData = vehiculo;
                            marker.setLatLng([vehLat, vehLon]);
                            marker.getElement().querySelector('.vehiculo-tooltip').innerHTML = `${vehiculo.id}<br><span style="font-size:0.8em;color:#aaa;">→ ${vehiculo.destino}</span>`;
                            
                            const show = (vehiculo.linea === 'L1' && metroL1Activo) || (vehiculo.linea === 'L2' && metroL2Activo);
                            if (show && !map.hasLayer(marker)) map.addLayer(marker);
                            if (!show && map.hasLayer(marker)) map.removeLayer(marker);
                        }
                    });
                }
            };

            socket.onclose = function() {
                setTimeout(initWebSockets, 3000);
            };
        }

        map.on('click', () => { cerrarPanel(); });
    