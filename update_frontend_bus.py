import re

def update_index():
    path = 'app/index.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix limpiarDestinoGTFS
    old_limpiar = """        function limpiarDestinoGTFS(destinoRaw) {
            if (!destinoRaw) return 'Dirección Desconocida';
            let dest = destinoRaw.replace(/\(.*?\)/g, '').trim();
            if (dest.includes('/')) {
                let parts = dest.split('/');
                dest = parts[parts.length - 1].trim();
                if (!dest && parts.length > 1) dest = parts[parts.length - 2].trim();
            }
            dest = dest.replace(/^.*?-\s*/, '');
            if (!dest) dest = destinoRaw.substring(0, 15) + '...';
            return dest.trim();
        }"""
        
    new_limpiar = """        function limpiarDestinoGTFS(destinoRaw) {
            if (!destinoRaw) return 'Dirección Desconocida';
            let dest = destinoRaw;
            
            // Si hay barra, nos quedamos con la última parte
            if (dest.includes('/')) {
                let parts = dest.split('/');
                dest = parts[parts.length - 1].trim();
                if (!dest && parts.length > 1) dest = parts[parts.length - 2].trim();
            }
            
            // Limpiar paréntesis (ej. "(ZORROTZA)" -> "ZORROTZA")
            dest = dest.replace(/[\(\)]/g, '').trim();
            
            // Eliminar prefijos
            dest = dest.replace(/^.*?-\s*/, '').trim();
            
            if (!dest) dest = destinoRaw.substring(0, 15) + '...';
            return dest;
        }"""
    
    if old_limpiar in content:
        content = content.replace(old_limpiar, new_limpiar)
    
    # 2. Add Search Bar Logic (inputBuscador)
    search_logic = """
        const inputBuscador = document.getElementById('buscador-estaciones');
        const divResultados = document.getElementById('resultados-busqueda');

        window.abrirPanelBusDesdeBuscador = function(id) {
            const estacion = todasLasEstacionesBus.find(e => e.id === id);
            const marker = marcadoresBusPorId[id];
            setTimeout(() => {
                if (estacion && marker) {
                    if (!grupoMarcadoresBus.hasLayer(marker)) {
                        grupoMarcadoresBus.addLayer(marker);
                    }
                    abrirPanelBus(estacion, marker, 18);
                    if(inputBuscador) inputBuscador.value = '';
                    if(divResultados) divResultados.style.display = 'none';
                }
            }, 50);
        };

        if (inputBuscador && divResultados) {
            inputBuscador.addEventListener('input', (e) => {
                const q = e.target.value.toLowerCase().trim();
                if (!q) {
                    divResultados.style.display = 'none';
                    return;
                }
                
                let match = [];
                if (typeof todasLasEstaciones !== 'undefined') match = match.concat(todasLasEstaciones);
                if (typeof todasLasEstacionesMetro !== 'undefined') match = match.concat(todasLasEstacionesMetro);
                if (typeof todasLasEstacionesBus !== 'undefined') match = match.concat(todasLasEstacionesBus);
                
                const filtradas = match.filter(est => est.nombre.toLowerCase().includes(q)).slice(0, 8);
                
                if (filtradas.length === 0) {
                    divResultados.innerHTML = '<div style="padding: 10px; color: var(--text-secondary); font-size: 0.9em; text-align: center;">No se encontraron resultados</div>';
                    divResultados.style.display = 'block';
                    return;
                }
                
                let html = '';
                filtradas.forEach(est => {
                    let tipo = 'tranvia';
                    let icon = typeof svgTranvia !== 'undefined' ? svgTranvia : '';
                    let onClickFn = 'seleccionarDesdeBuscador';
                    
                    if (est.id.startsWith('metro_')) {
                        tipo = 'metro';
                        icon = typeof svgMetro !== 'undefined' ? svgMetro : '';
                        onClickFn = 'seleccionarDesdeMetro';
                    } else if (est.id.startsWith('bus_')) {
                        tipo = 'bus';
                        icon = typeof svgBus !== 'undefined' ? svgBus : '';
                        onClickFn = 'abrirPanelBusDesdeBuscador';
                    }
                    
                    html += `
                        <div style="padding: 12px 16px; border-bottom: 1px solid var(--border-color); cursor: pointer; display: flex; align-items: center; gap: 8px; transition: background 0.2s;" onmouseover="this.style.background='var(--hover-bg)'" onmouseout="this.style.background='transparent'" onclick="${onClickFn}('${est.id}')">
                            <span style="flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center;">${icon}</span>
                            <span style="color: var(--text-primary); font-weight: 500;">${est.nombre}</span>
                        </div>
                    `;
                });
                divResultados.innerHTML = html;
                divResultados.style.display = 'block';
            });
        }
    """
    
    # Inject search logic after window.seleccionarDesdeBuscador definition
    target_search = "        window.seleccionarDesdeBuscador = function(id) {"
    if target_search in content and "inputBuscador.addEventListener('input'" not in content:
        content = content.replace(target_search, search_logic + "\n" + target_search)
        
    # 3. Enable Bilbobus filter button
    old_btn = '<button class="modo-btn" disabled>Bilbobus</button>'
    new_btn = '<button class="modo-btn" id="tab-bus" onclick="switchTab(\\\'bus\\\')">Bilbobus</button>'
    if old_btn in content:
        content = content.replace(old_btn, new_btn.replace("\\'", "'"))
        
    # 4. Update switchTab function
    old_switch = """        window.switchTab = function(mode) {
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
        };"""
        
    new_switch = """        window.switchTab = function(mode) {
            const tabs = ['todo', 'tranvia', 'metro', 'bus'];
            tabs.forEach(t => {
                const el = document.getElementById(`tab-${t}`);
                if (el) el.classList.remove('activo');
            });
            const modeEl = document.getElementById(`tab-${mode}`);
            if (modeEl) modeEl.classList.add('activo');
            
            if (mode === 'todo') {
                document.getElementById('card-tranvia').style.display = 'flex';
                document.getElementById('card-metro-l1').style.display = 'flex';
                document.getElementById('card-metro-l2').style.display = 'flex';
                if(document.getElementById('card-bus')) document.getElementById('card-bus').style.display = 'flex';
            } else if (mode === 'tranvia') {
                document.getElementById('card-tranvia').style.display = 'flex';
                document.getElementById('card-metro-l1').style.display = 'none';
                document.getElementById('card-metro-l2').style.display = 'none';
                if(document.getElementById('card-bus')) document.getElementById('card-bus').style.display = 'none';
            } else if (mode === 'metro') {
                document.getElementById('card-tranvia').style.display = 'none';
                document.getElementById('card-metro-l1').style.display = 'flex';
                document.getElementById('card-metro-l2').style.display = 'flex';
                if(document.getElementById('card-bus')) document.getElementById('card-bus').style.display = 'none';
            } else if (mode === 'bus') {
                document.getElementById('card-tranvia').style.display = 'none';
                document.getElementById('card-metro-l1').style.display = 'none';
                document.getElementById('card-metro-l2').style.display = 'none';
                if(document.getElementById('card-bus')) document.getElementById('card-bus').style.display = 'flex';
            }
        };"""
        
    if old_switch in content:
        content = content.replace(old_switch, new_switch)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Done")

if __name__ == '__main__':
    update_index()
