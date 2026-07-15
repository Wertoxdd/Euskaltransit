import re

def add_modal_ui():
    path = 'app/index.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # CSS for Modal
    css = """
        /* Modal Horarios Estáticos */
        .modal-overlay {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(8px);
            z-index: 10000;
            display: flex; align-items: center; justify-content: center;
            opacity: 0; pointer-events: none;
            transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .modal-overlay.open { opacity: 1; pointer-events: auto; }
        
        .modal-container {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            width: 90%; max-width: 600px; max-height: 85vh;
            display: flex; flex-direction: column;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            transform: scale(0.95) translateY(20px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .modal-overlay.open .modal-container { transform: scale(1) translateY(0); }
        
        .modal-header {
            padding: 20px 24px;
            border-bottom: 1px solid var(--border-color);
            display: flex; justify-content: space-between; align-items: center;
        }
        .modal-body {
            padding: 24px;
            overflow-y: auto;
            scrollbar-width: thin;
        }
        
        .grid-horas {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
            gap: 8px;
            margin-top: 12px;
        }
        .hora-item {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 6px;
            text-align: center;
            padding: 6px 0;
            font-size: 0.9em;
            color: #eee;
            font-weight: 500;
        }
        .ruta-section { margin-bottom: 24px; }
        .ruta-header {
            display: flex; align-items: center; gap: 10px; margin-bottom: 12px;
        }
"""
    if "/* Modal Horarios Estáticos */" not in content:
        content = content.replace("/* Scrollbar personalizado */", css + "\n        /* Scrollbar personalizado */")
        
    # HTML for Modal
    html_modal = """
    <!-- Modal Horarios Estáticos -->
    <div id="modal-horarios" class="modal-overlay" onclick="if(event.target===this) cerrarModalEstatico()">
        <div class="modal-container">
            <div class="modal-header">
                <div>
                    <h2 id="modal-titulo" style="margin: 0; font-size: 1.3em;">Horarios Estáticos</h2>
                    <p style="margin: 4px 0 0 0; color: var(--text-secondary); font-size: 0.9em;">Horarios programados para el día de hoy</p>
                </div>
                <button onclick="cerrarModalEstatico()" style="background: none; border: none; color: white; cursor: pointer; padding: 4px; border-radius: 4px;">
                    <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
            </div>
            <div id="modal-body" class="modal-body">
                <!-- Contenido dinámico -->
            </div>
        </div>
    </div>
"""
    if 'id="modal-horarios"' not in content:
        content = content.replace('</body>', html_modal + '\n</body>')
        
    # JavaScript logic for Modal
    js_logic = """
        window.cerrarModalEstatico = function() {
            document.getElementById('modal-horarios').classList.remove('open');
        };
        
        window.abrirModalEstatico = function(stop_id, stop_nombre) {
            document.getElementById('modal-titulo').innerText = stop_nombre;
            const body = document.getElementById('modal-body');
            body.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">Cargando horarios programados...</div>';
            document.getElementById('modal-horarios').classList.add('open');
            
            fetch(`/api/horarios_estaticos_bus/${stop_id}`)
                .then(r => r.json())
                .then(data => {
                    if (!data.rutas || data.rutas.length === 0) {
                        body.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px;">No hay horarios programados para esta parada hoy.</div>';
                        return;
                    }
                    
                    let html = '';
                    data.rutas.forEach(ruta => {
                        let destinoLimpio = limpiarDestinoGTFS(ruta.destino);
                        html += `
                            <div class="ruta-section">
                                <div class="ruta-header">
                                    <span style="background: #E3001B; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.9em;">${ruta.linea}</span>
                                    <span style="font-weight: 600; font-size: 1.05em;">${destinoLimpio}</span>
                                </div>
                                <div class="grid-horas">
                                    ${ruta.horas_str.map(h => `<div class="hora-item">${h}</div>`).join('')}
                                </div>
                            </div>
                        `;
                    });
                    body.innerHTML = html;
                })
                .catch(e => {
                    body.innerHTML = '<div style="text-align: center; color: #E3001B; padding: 40px;">Error al cargar horarios.</div>';
                });
        };
"""
    if "window.abrirModalEstatico =" not in content:
        content = content.replace("window.cargarSalidasBus = function(id) {", js_logic + "\n        window.cargarSalidasBus = function(id) {")
        
    # Connect button
    old_btn = """<button class="btn-calendario" onclick="alert('Módulo de horarios estáticos en desarrollo.');" title="Horarios Completos\""""
    new_btn = """<button class="btn-calendario" onclick="abrirModalEstatico('${estacion.id}', '${estacion.nombre}')" title="Horarios Completos\""""
    content = content.replace(old_btn, new_btn)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

add_modal_ui()
print("Frontend actualizado con modal estático.")
