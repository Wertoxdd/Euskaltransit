import os

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Call cargarEstacionesBus() before fetching other stations
if "cargarEstacionesBus();" not in content:
    content = content.replace(
        "fetch('/api/estaciones').then(r => r.json()),",
        "cargarEstacionesBus();\n            fetch('/api/estaciones').then(r => r.json()),"
    )

# 2. Add window.seleccionarDesdeBus function
js_seleccionar_bus = """
        window.seleccionarDesdeBus = function(id) {
            if (!busActivo) toggleBus(); // Auto-activar si estaba apagado
            
            const estacion = todasLasEstacionesBus.find(e => e.id === id);
            const marker = marcadoresBusPorId[id];
            
            setTimeout(() => {
                if (estacion && marker) {
                    abrirPanelBus(estacion, marker, 18);
                    const divResultados = document.getElementById('resultados-busqueda');
                    const inputBuscador = document.getElementById('busqueda-input');
                    if (inputBuscador) inputBuscador.value = '';
                    if (divResultados) divResultados.style.display = 'none';
                }
            }, 50);
        };
"""
if "window.seleccionarDesdeBus =" not in content:
    content = content.replace(
        "window.seleccionarDesdeBuscador = function(id) {",
        js_seleccionar_bus + "\n        window.seleccionarDesdeBuscador = function(id) {"
    )

# 3. Update inputBuscador event listener to include Bus
search_old = """
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
"""

search_new = """
            const resTranvia = todasLasEstaciones.filter(e => e.nombre.toLowerCase().includes(query)).map(e => ({
                id: e.id, nombre: e.nombre, tipo: 'tranvia'
            }));
            const resMetro = todasLasEstacionesMetro.filter(e => e.nombre.toLowerCase().includes(query)).map(e => ({
                id: e.id, nombre: e.nombre, tipo: 'metro'
            }));
            const resBus = (typeof todasLasEstacionesBus !== 'undefined' ? todasLasEstacionesBus : []).filter(e => e.nombre.toLowerCase().includes(query)).map(e => ({
                id: e.id, nombre: e.nombre, tipo: 'bus'
            }));
            const resultados = [...resTranvia, ...resMetro, ...resBus];
            
            if (resultados.length > 0) {
                divResultados.innerHTML = resultados.map(e => {
                    if (e.tipo === 'metro') {
                        return `<div class="resultado-item" onclick="seleccionarDesdeMetro('${e.id}')">${svgMetro}${e.nombre}</div>`;
                    } else if (e.tipo === 'bus') {
                        return `<div class="resultado-item" onclick="seleccionarDesdeBus('${e.id}')">${typeof svgBus !== 'undefined' ? svgBus : ''}${e.nombre}</div>`;
                    }
                    return `<div class="resultado-item" onclick="seleccionarDesdeBuscador('${e.id}')">${svgTranvia}${e.nombre}</div>`;
                }).join('');
"""

if "resBus =" not in content:
    content = content.replace(search_old.strip(), search_new.strip())

# 4. Update the calculator routing dropdown to include Bus
calc_old = """
                let todas = [...todasLasEstacionesMetro.map(e => ({...e, tipo: 'metro'})), ...todasLasEstaciones.map(e => ({...e, tipo: 'tranvia'}))];
                
                // Removed filtering so users can see all networks regardless of origin
                
                const filtradas = todas.filter(e => e.nombre.toLowerCase().includes(query));
                
                filtradas.forEach(e => {
                    const opt = document.createElement('div');
                    opt.className = 'c-option';
                    const icon = e.tipo === 'metro' ? svgMetro : svgTranvia;
                    const isTranvia = e.tipo === 'tranvia';
                    opt.innerHTML = icon + ' ' + e.nombre;
                    opt.onclick = () => seleccionarEstacionTarifa(tipo, e.id, e.nombre, isTranvia);
"""

calc_new = """
                let todas = [
                    ...todasLasEstacionesMetro.map(e => ({...e, tipo: 'metro'})), 
                    ...todasLasEstaciones.map(e => ({...e, tipo: 'tranvia'})),
                    ...(typeof todasLasEstacionesBus !== 'undefined' ? todasLasEstacionesBus.map(e => ({...e, tipo: 'bus'})) : [])
                ];
                
                // Removed filtering so users can see all networks regardless of origin
                
                const filtradas = todas.filter(e => e.nombre.toLowerCase().includes(query));
                
                filtradas.forEach(e => {
                    const opt = document.createElement('div');
                    opt.className = 'c-option';
                    const icon = e.tipo === 'metro' ? svgMetro : (e.tipo === 'tranvia' ? svgTranvia : (typeof svgBus !== 'undefined' ? svgBus : ''));
                    const isTranvia = e.tipo === 'tranvia';
                    opt.innerHTML = icon + ' ' + e.nombre;
                    opt.onclick = () => seleccionarEstacionTarifa(tipo, e.id, e.nombre, isTranvia);
"""

if "todasLasEstacionesBus.map" not in content:
    content = content.replace(calc_old.strip(), calc_new.strip())

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("index.html arreglado e inyectado correctamente.")
