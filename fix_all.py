def apply_fixes():
    import re

    # 1. Update gestor.py
    gestor_path = 'app/gestor.py'
    with open(gestor_path, 'r', encoding='utf-8') as f:
        gestor_code = f.read()

    # The current code in gestor.py for bus departures:
    target_bus = """        horarios = self.horarios_bus.get(stop_id, [])
        salidas = []
        for t_id, d_secs in horarios:
            trip_info = self.trips_info_bus.get(t_id)
            if not trip_info: continue
            
            if trip_info["service_id"] not in active_services:
                continue
                
            if d_secs >= current_secs:
                diff_mins = (d_secs - current_secs) // 60
                if diff_mins <= 60:
                    salidas.append({
                        "linea": trip_info["route"],
                        "destino": trip_info["headsign"],
                        "minutos": diff_mins
                    })
                if len(salidas) >= 6:
                    break
                    
        return salidas"""

    replacement_bus = """        horarios = self.horarios_bus.get(stop_id, [])
        
        salidas_por_linea = {}
        for t_id, d_secs in horarios:
            if d_secs < current_secs: continue
            
            trip_info = self.trips_info_bus.get(t_id)
            if not trip_info: continue
            
            if trip_info["service_id"] not in active_services:
                continue
                
            diff_mins = (d_secs - current_secs) // 60
            if diff_mins > 120: continue # Limit to next 2 hours
            
            linea = trip_info["route"]
            destino = trip_info["headsign"]
            clave = f"{linea}_{destino}"
            
            if clave not in salidas_por_linea:
                salidas_por_linea[clave] = {
                    "linea": linea,
                    "destino": destino,
                    "tiempos": []
                }
            
            if len(salidas_por_linea[clave]["tiempos"]) < 3:
                salidas_por_linea[clave]["tiempos"].append(diff_mins)
                
        salidas = []
        for v in salidas_por_linea.values():
            salidas.append({
                "linea": v["linea"],
                "destino": v["destino"],
                "minutos_list": v["tiempos"]
            })
            
        def sort_key(s):
            import re
            m = re.match(r'^\d+', s["linea"])
            return int(m.group(0)) if m else 999
            
        salidas.sort(key=sort_key)
        return salidas"""

    if target_bus in gestor_code:
        gestor_code = gestor_code.replace(target_bus, replacement_bus)
        print("Updated gestor.py")

    with open(gestor_path, 'w', encoding='utf-8') as f:
        f.write(gestor_code)


    # 2. Update index.html
    index_path = 'app/index.html'
    with open(index_path, 'r', encoding='utf-8') as f:
        index_code = f.read()

    # Update flexbox
    index_code = index_code.replace('align-items: flex-start; margin-bottom: 20px; gap: 10px;', 'align-items: center; margin-bottom: 20px; gap: 10px;')

    # Update flyTo
    index_code = index_code.replace('duration: 0.4, easeLinearity: 0.4', 'duration: 0.8, easeLinearity: 0.25')
    index_code = index_code.replace('duration: 0.3', 'duration: 0.8')

    # Update cargarSalidasBus mapping
    target_render = """                    data.salidas.forEach(s => {
                        let textMin = s.minutos === 0 ? 'Ahora' : `${s.minutos} min`;
                        let color = s.minutos <= 3 ? '#E3001B' : (s.minutos <= 10 ? '#f39c12' : '#34b658');
                        
                        html += `
                            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span style="background: #E3001B; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 0.8em; min-width: 32px; text-align: center;">${s.linea}</span>
                                    <span style="color: #eee; font-size: 0.95em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 140px;">${limpiarDestinoGTFS(s.destino)}</span>
                                </div>
                                <div style="font-weight: 600; color: ${color}; font-size: 0.95em;">
                                    ${textMin}
                                </div>
                            </div>
                        `;
                    });"""

    replacement_render = """                    data.salidas.forEach(s => {
                        let tiemposHtml = '';
                        if (s.minutos_list && s.minutos_list.length > 0) {
                            tiemposHtml = s.minutos_list.map((m, idx) => {
                                let textMin = m === 0 ? 'Ahora' : `${m}m`;
                                let color = m <= 3 ? '#E3001B' : (m <= 10 ? '#f39c12' : '#34b658');
                                let isFirst = idx === 0;
                                return `<span style="color: ${color}; font-weight: ${isFirst ? 'bold' : 'normal'}; font-size: ${isFirst ? '1em' : '0.9em'};">${textMin}</span>`;
                            }).join('<span style="color: rgba(255,255,255,0.2); margin: 0 4px;">·</span>');
                        } else if (s.minutos !== undefined) {
                            // Fallback if backend not updated
                            let textMin = s.minutos === 0 ? 'Ahora' : `${s.minutos} min`;
                            let color = s.minutos <= 3 ? '#E3001B' : (s.minutos <= 10 ? '#f39c12' : '#34b658');
                            tiemposHtml = `<span style="color: ${color}; font-weight: bold;">${textMin}</span>`;
                        }
                        
                        html += `
                            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 6px;">
                                <div style="display: flex; align-items: center; gap: 10px; flex: 1; overflow: hidden; padding-right: 10px;">
                                    <span style="background: #E3001B; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 0.8em; min-width: 32px; text-align: center; flex-shrink: 0;">${s.linea}</span>
                                    <span style="color: #eee; font-size: 0.9em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${limpiarDestinoGTFS(s.destino)}</span>
                                </div>
                                <div style="display: flex; align-items: center; justify-content: flex-end; flex-shrink: 0;">
                                    ${tiemposHtml}
                                </div>
                            </div>
                        `;
                    });"""

    if target_render in index_code:
        index_code = index_code.replace(target_render, replacement_render)
        print("Updated index.html render")

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_code)

if __name__ == '__main__':
    apply_fixes()
