import os
import re

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_func = """        function abrirPanelBus(estacion, marker, zoomNivel = 17) {
            seleccionarMarcador(marker);
            map.flyTo(marker.getLatLng(), zoomNivel, { duration: 0.5 });
            
            let lineasBadges = estacion.lineas.map(l => `<span style="background: #E3001B; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-right: 4px;">${l}</span>`).join('');
            
            const html = `
                <div style="margin-bottom: 12px;">
                    <div style="font-size: 0.85em; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">BILBOBUS</div>
                    <div style="font-size: 1.3em; font-weight: 600; color: #fff;">${estacion.nombre}</div>
                </div>
                <div class="badge-linea" style="background: rgba(227,0,27,0.1); color: #E3001B; border-color: rgba(227,0,27,0.4); margin-bottom: 0;">
                    ${lineasBadges}
                </div>
                
                <div style="margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-size: 0.9em; color: var(--text-secondary); font-weight: 500;">PRÓXIMAS SALIDAS</span>
                        <button class="btn-recargar" onclick="cargarSalidasBus('${estacion.id}')" title="Recargar Horarios" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 6px; color: var(--text-secondary); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s;">
                            <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
                            Recargar
                        </button>
                    </div>
                    <div id="bus-salidas-${estacion.id}" style="min-height: 50px;">
                        <div style="text-align: center; color: var(--text-secondary); font-size: 0.9em; padding: 10px;">Cargando horarios...</div>
                    </div>
                </div>
            `;
            panelContent.innerHTML = html;
            panelDetalles.classList.add('open');
            cargarSalidasBus(estacion.id);
        }"""

new_func = """        function abrirPanelBus(estacion, marker, zoomNivel = 17) {
            seleccionarMarcador(marker);
            map.flyTo(marker.getLatLng(), zoomNivel, { duration: 0.5 });
            
            panel.style.transform = '';
            panel.classList.add('abierto');
            panel.style.background = 'var(--bg-app)';
            panel.style.borderLeftColor = '#E3001B';
            
            document.getElementById('panel-titulo').innerHTML = `<div style="display: flex; align-items: center; gap: 6px;">${svgBus} <span>${estacion.nombre}</span></div>`;
            
            let lineasBadges = estacion.lineas.map(l => `<span style="background: #E3001B; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-right: 4px; font-size: 0.9em;">${l}</span>`).join('');
            
            const html = `
            <div class="panel-fade-item" style="animation-delay: 0.05s; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div class="badge-linea" style="background: rgba(227,0,27,0.1); color: #E3001B; border-color: rgba(227,0,27,0.4); margin-bottom: 0;">
                    BILBOBUS ${lineasBadges}
                </div>
                <button class="btn-recargar" onclick="cargarSalidasBus('${estacion.id}')" title="Recargar Horarios" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 6px; color: var(--text-secondary); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s;">
                    <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
                    Actualizar
                </button>
            </div>
            
            <div class="panel-fade-item estado-box" style="animation-delay: 0.15s; display: flex; flex-direction: column; gap: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-size: 0.7em; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Estado del servicio</div>
                        <div style="color: #34b658; font-weight: 600; font-size: 1.05em;">Operando con normalidad</div>
                    </div>
                    <div style="background: rgba(52,182,88,0.2); border-radius: 50%; padding: 6px;">
                        <svg viewBox="0 0 24 24" width="20" height="20" stroke="#34b658" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    </div>
                </div>
            </div>
            
            <div class="panel-fade-item" style="animation-delay: 0.25s; margin-top: 20px;">
                <div id="bus-salidas-container-${estacion.id}" style="min-height: 50px;">
                    <div style="text-align: center; color: var(--text-secondary); font-size: 0.9em; padding: 10px;">Cargando horarios...</div>
                </div>
            </div>
            `;
            
            document.getElementById('contenido-parada').innerHTML = html;
            cargarSalidasBus(estacion.id);
        }"""

if old_func in content:
    content = content.replace(old_func, new_func)
    
    # Also update cargarSalidasBus to target the correct ID format
    content = content.replace("const container = document.getElementById(`bus-salidas-${idEstacion}`);", "const container = document.getElementById(`bus-salidas-container-${idEstacion}`);")
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("abrirPanelBus actualizado correctamente al nuevo panel lateral.")
else:
    print("Error: No se encontró abrirPanelBus antiguo.")
