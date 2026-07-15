import re

html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add limpiarDestinoGTFS function before window.cargarSalidasBus
gtfs_func = """        function limpiarDestinoGTFS(destinoRaw) {
            if (!destinoRaw) return 'Dirección Desconocida';
            let dest = destinoRaw;
            // Eliminar códigos y quedarse con lo último tras la barra "/"
            if (dest.includes('/')) {
                dest = dest.split('/').pop();
            }
            // Eliminar textos entre paréntesis tipo (SA) o (PT)
            dest = dest.replace(/\\(.*?\\)/g, '');
            // Eliminar prefijos de línea si aún quedan (ej: "01 - San Inazio")
            dest = dest.replace(/^\\d{2}\\s*-\\s*/, '');
            return dest.trim();
        }

        window.cargarSalidasBus = function(id) {"""
content = content.replace("        window.cargarSalidasBus = function(id) {", gtfs_func)

# 2. Use limpiarDestinoGTFS in cargarSalidasBus
old_destino = "${s.destino || 'Direccin Desconocida'}"
# Fallback in case encoding character was parsed differently by python
old_destino_regex = r"\$\{s\.destino\s*\|\|\s*'[^']+'\}"
content = re.sub(old_destino_regex, "${limpiarDestinoGTFS(s.destino)}", content)


# 3. Refactor the header layout in abrirPanelBus
# We want to replace the whole <div class="panel-fade-item"> up to the ${correspondenciasHtml}
old_panel_header_regex = r'(<div class="panel-fade-item" style="animation-delay: 0\.05s; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; gap: 10px;">[\s\S]*?</button>\s*</div>)'

new_panel_header = """<div class="panel-fade-item" style="animation-delay: 0.05s; display: flex; justify-content: space-between; align-items: stretch; margin-bottom: 20px; gap: 10px;">
                <div class="badge-linea" style="background: rgba(227,0,27,0.1); color: #E3001B; border-color: rgba(227,0,27,0.4); margin-bottom: 0; display: flex; gap: 8px; align-items: center; flex: 1; padding: 10px 12px; border-radius: 8px;">
                    <div style="font-weight: bold; align-self: flex-start; padding-top: 2px;">BILBOBUS</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 4px; flex: 1;">${lineasBadges}</div>
                </div>
                
                <div style="display: flex; gap: 6px; align-items: stretch; flex-shrink: 0;">
                    <button class="btn-calendario" onclick="alert('Módulo de horarios estáticos en desarrollo.');" title="Horarios Completos" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 0 12px; border-radius: 8px; color: var(--text-secondary); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s;">
                        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                    </button>
                    <button class="btn-recargar" onclick="cargarSalidasBus('${estacion.id}')" title="Recargar Horarios" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 0 14px; border-radius: 8px; color: var(--text-secondary); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; font-size: 0.9em;">
                        <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
                        Actualizar
                    </button>
                </div>
            </div>"""

content = re.sub(old_panel_header_regex, new_panel_header, content)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Refactorización GTFS y UI aplicada correctamente.")
