import os

# 1. Update gestor.py
gestor_path = 'app/gestor.py'
with open(gestor_path, 'r', encoding='utf-8') as f:
    gestor_content = f.read()

# Add to __init__
init_old = """        self.estaciones_bus = {}         # Bilbobus
        self.bus_edges = set()           # (origen, destino, linea)
        self.datos_bus_cargados = False"""
init_new = """        self.estaciones_bus = {}         # Bilbobus
        self.bus_edges = set()           # (origen, destino, linea)
        self.horarios_bus = {}
        self.trips_info_bus = {}
        self.calendar_bus = {}
        self.calendar_dates_bus = []
        self.datos_bus_cargados = False"""
if "self.horarios_bus = {}" not in gestor_content:
    gestor_content = gestor_content.replace(init_old, init_new)

# Replace cargar_bus_gtfs
cargar_bus_old = gestor_content.split("def cargar_bus_gtfs(self, ruta_carpeta: str):")[1].split("def obtener_linea(self, id_linea: str) -> Linea:")[0]

cargar_bus_new = """
        if self.datos_bus_cargados:
            return
        print(f"Cargando Bilbobus desde {ruta_carpeta}")
        
        ruta_stops = os.path.join(ruta_carpeta, "stops.txt")
        ruta_routes = os.path.join(ruta_carpeta, "routes.txt")
        ruta_trips = os.path.join(ruta_carpeta, "trips.txt")
        ruta_stop_times = os.path.join(ruta_carpeta, "stop_times.txt")
        ruta_calendar = os.path.join(ruta_carpeta, "calendar.txt")
        ruta_calendar_dates = os.path.join(ruta_carpeta, "calendar_dates.txt")
        
        # 1. Leer rutas (route_id -> short_name)
        routes = {}
        if os.path.exists(ruta_routes):
            with open(ruta_routes, mode="r", encoding="utf-8") as f:
                lector = csv.DictReader(f)
                for fila in lector:
                    routes[fila["route_id"]] = fila["route_short_name"]
                
        # Leer calendar
        if os.path.exists(ruta_calendar):
            with open(ruta_calendar, mode="r", encoding="utf-8") as f:
                for fila in csv.DictReader(f):
                    self.calendar_bus[fila["service_id"]] = {
                        'monday': fila['monday'], 'tuesday': fila['tuesday'],
                        'wednesday': fila['wednesday'], 'thursday': fila['thursday'],
                        'friday': fila['friday'], 'saturday': fila['saturday'],
                        'sunday': fila['sunday'], 'start_date': fila['start_date'],
                        'end_date': fila['end_date']
                    }
                    
        if os.path.exists(ruta_calendar_dates):
            with open(ruta_calendar_dates, mode="r", encoding="utf-8") as f:
                for fila in csv.DictReader(f):
                    self.calendar_dates_bus.append({
                        'service_id': fila['service_id'],
                        'date': fila['date'],
                        'exception_type': fila['exception_type']
                    })

        # 2. Leer trips (trip_id -> route_short_name, trip_headsign)
        trips_to_route = {}
        if os.path.exists(ruta_trips):
            with open(ruta_trips, mode="r", encoding="utf-8") as f:
                lector = csv.DictReader(f)
                for fila in lector:
                    headsign = fila.get("trip_headsign", "")
                    r_id = fila["route_id"]
                    r_name = routes.get(r_id, "BUS")
                    trips_to_route[fila["trip_id"]] = r_name
                    self.trips_info_bus[fila["trip_id"]] = {
                        "route": r_name,
                        "headsign": headsign,
                        "service_id": fila["service_id"]
                    }
                
        # 3. Leer paradas base
        if os.path.exists(ruta_stops):
            with open(ruta_stops, mode="r", encoding="utf-8") as f:
                lector = csv.DictReader(f)
                for fila in lector:
                    id_est = fila["stop_id"]
                    nombre = fila["stop_name"].strip()
                    lat = float(fila["stop_lat"].strip())
                    lon = float(fila["stop_lon"].strip())
                    
                    nueva = Estacion(f"bus_{id_est}", nombre, lat, lon)
                    self.estaciones_bus[f"bus_{id_est}"] = nueva
                    self.horarios_bus[f"bus_{id_est}"] = []
                
        # 4. Asignar líneas a cada parada y extraer secuencias y horarios
        stop_lines = { k: set() for k in self.estaciones_bus.keys() }
        trip_stop_seqs = {}
        if os.path.exists(ruta_stop_times):
            with open(ruta_stop_times, mode="r", encoding="utf-8") as f:
                lector = csv.DictReader(f)
                for fila in lector:
                    t_id = fila["trip_id"]
                    s_id = f"bus_{fila['stop_id']}"
                    
                    if t_id in trips_to_route and s_id in stop_lines:
                        stop_lines[s_id].add(trips_to_route[t_id])
                        
                        # Horarios
                        dep_time = fila["departure_time"]
                        h, m, s = map(int, dep_time.split(':'))
                        dep_secs = h * 3600 + m * 60 + s
                        self.horarios_bus[s_id].append((t_id, dep_secs))
                        
                    seq = int(fila["stop_sequence"])
                    if t_id not in trip_stop_seqs:
                        trip_stop_seqs[t_id] = []
                    trip_stop_seqs[t_id].append((seq, s_id))
                    
        for s_id, lineas_set in stop_lines.items():
            for linea in sorted(list(lineas_set)):
                self.estaciones_bus[s_id].agregar_linea(linea)

        # 5. Conectar las paradas secuenciales de autobús para el grafo A*
        for t_id, seqs in trip_stop_seqs.items():
            seqs.sort(key=lambda x: x[0])
            for i in range(len(seqs) - 1):
                origen = seqs[i][1]
                destino = seqs[i+1][1]
                linea = trips_to_route.get(t_id, "BUS")
                self.bus_edges.add((origen, destino, linea))

        for sid in self.horarios_bus:
            self.horarios_bus[sid].sort(key=lambda x: x[1])

        self.datos_bus_cargados = True
        print(f"¡Bilbobus! {len(self.estaciones_bus)} paradas procesadas, {len(self.bus_edges)} conexiones.")
    
    def obtener_proximas_salidas_bus(self, stop_id: str):
        import datetime
        now = datetime.datetime.now()
        current_secs = now.hour * 3600 + now.minute * 60 + now.second
        
        today_str = now.strftime("%Y%m%d")
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        current_day_name = day_names[now.weekday()]
        
        active_services = set()
        # Evaluate standard calendar
        for srv_id, c in self.calendar_bus.items():
            if c["start_date"] <= today_str <= c["end_date"]:
                if c[current_day_name] == "1":
                    active_services.add(srv_id)
                    
        # Evaluate exceptions
        for cd in self.calendar_dates_bus:
            if cd["date"] == today_str:
                if cd["exception_type"] == "1":
                    active_services.add(cd["service_id"])
                elif cd["exception_type"] == "2" and cd["service_id"] in active_services:
                    active_services.remove(cd["service_id"])

        horarios = self.horarios_bus.get(stop_id, [])
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
                    
        return salidas

    """
gestor_content = gestor_content.replace(cargar_bus_old, cargar_bus_new)

with open(gestor_path, 'w', encoding='utf-8') as f:
    f.write(gestor_content)

# 2. Update router.py
router_path = 'app/router.py'
with open(router_path, 'r', encoding='utf-8') as f:
    router_content = f.read()

router_new = """@router.get("/proximas_salidas_bus/{stop_id}")
async def proximas_salidas_bus(stop_id: str):
    salidas = gestor.obtener_proximas_salidas_bus(stop_id)
    return {"salidas": salidas}

@router.get("/estaciones_bus")"""

if "proximas_salidas_bus" not in router_content:
    router_content = router_content.replace('@router.get("/estaciones_bus")', router_new)
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write(router_content)

# 3. Update index.html
html_path = 'app/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Add cargarSalidasBus JS function
js_bus = """
        function abrirPanelBus(estacion, marker, zoomNivel = 17) {
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
        }

        window.cargarSalidasBus = function(id) {
            const container = document.getElementById(`bus-salidas-${id}`);
            if (!container) return;
            container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); font-size: 0.9em; padding: 10px;">Cargando horarios...</div>';
            
            fetch(`/api/proximas_salidas_bus/${id}`)
                .then(r => r.json())
                .then(data => {
                    if (!data.salidas || data.salidas.length === 0) {
                        container.innerHTML = '<div style="color: var(--text-secondary); font-size: 0.9em; text-align: center; padding: 10px;">No hay salidas próximas (1h)</div>';
                        return;
                    }
                    
                    let html = '<div style="display: flex; flex-direction: column; gap: 8px;">';
                    data.salidas.forEach(s => {
                        let textMin = s.minutos === 0 ? 'Ahora' : `${s.minutos} min`;
                        let color = s.minutos <= 3 ? '#E3001B' : (s.minutos <= 10 ? '#f39c12' : '#34b658');
                        
                        html += `
                            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span style="background: #E3001B; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 0.8em; min-width: 32px; text-align: center;">${s.linea}</span>
                                    <span style="color: #eee; font-size: 0.95em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 140px;">${s.destino || 'Dirección Desconocida'}</span>
                                </div>
                                <div style="font-weight: 600; color: ${color}; font-size: 0.95em;">
                                    ${textMin}
                                </div>
                            </div>
                        `;
                    });
                    html += '</div>';
                    container.innerHTML = html;
                })
                .catch(e => {
                    container.innerHTML = '<div style="color: #e74c3c; font-size: 0.9em; text-align: center; padding: 10px;">Error al cargar horarios</div>';
                });
        };
"""

html_old = html_content.split("function abrirPanelBus(estacion, marker, zoomNivel = 17) {")[1].split("window.seleccionarDesdeBuscador = function(id)")[0]
html_content = html_content.replace(html_old, js_bus.split("function abrirPanelBus(estacion, marker, zoomNivel = 17) {")[1] + "\n\n        ")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Todo actualizado correctamente.")
