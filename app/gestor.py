import csv
import os
import asyncio
import re
import unicodedata
from app.modelos import Estacion, Linea
from app.excepciones import ArchivoGTFSNoEncontradoError

class Singleton(type):
    _instancias = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instancias:
            cls._instancias[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instancias[cls]

def _normalizar(texto):
    """Normaliza un string quitando acentos y pasando a minúsculas."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower().strip())
        if unicodedata.category(c) != 'Mn'
    )

class GestorRed(metaclass=Singleton):
    def __init__(self):
        self.estaciones_globales = {}    # Tranvía
        self.lineas_globales = {}
        self.calendar_tranvia = {}
        self.trips_info_tranvia = {}
        self.horarios_tranvia = {}
        
        self.estaciones_metro = {}       # Metro Bilbao
        self.lineas_metro = {}           # L1, L2 info
        
        self.estaciones_bus = {}         # Bilbobus
        self.bus_edges = set()           # (origen, destino, linea)
        self.horarios_bus = {}
        self.trips_info_bus = {}
        self.calendar_bus = {}
        self.calendar_dates_bus = []
        self.datos_bus_cargados = False
        
        self.datos_cargados = False
        self.datos_metro_cargados = False
    
    # 🚋 CARGA TRANVÍA 🚋───
    def cargar_gtfs(self, ruta_carpeta: str):
        if self.datos_cargados:
            return
        
        print(f"Inicializando lectura de GTFS desde {ruta_carpeta}")

        ruta_stops = os.path.join(ruta_carpeta, "stops.txt")
        ruta_routes = os.path.join(ruta_carpeta, "routes.txt")
        ruta_trips = os.path.join(ruta_carpeta, "trips.txt")
        ruta_stop_times = os.path.join(ruta_carpeta, "stop_times.txt")
        
        id_ruta_tranvia = None
        with open(ruta_routes, mode="r", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                if "tranvia" in fila.get("route_long_name", "").lower() or "tranbía" in fila.get("route_long_name", "").lower() or fila["route_short_name"] == "TR":
                    id_ruta_tranvia = fila["route_id"]
                    nueva_linea = Linea(fila["route_id"], "Tranvía", "#009B48") 
                    self.lineas_globales[fila["route_id"]] = nueva_linea
                    break 
                    
        if not id_ruta_tranvia:
            print("No se encontró el Tranvía en routes.txt")
            return

        trips_tranvia = set()
        with open(ruta_trips, mode="r", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                if fila["route_id"] == id_ruta_tranvia:
                    tid = fila["trip_id"]
                    trips_tranvia.add(tid)
                    self.trips_info_tranvia[tid] = (
                        fila.get("route_id", ""),
                        fila.get("service_id", ""),
                        fila.get("trip_headsign", ""),
                        fila.get("direction_id", "0")
                    )

        # Parse calendar
        ruta_calendar = os.path.join(ruta_carpeta, "calendar.txt")
        if os.path.exists(ruta_calendar):
            with open(ruta_calendar, mode="r", encoding="utf-8") as archivo:
                lector = csv.DictReader(archivo)
                for fila in lector:
                    self.calendar_tranvia[fila["service_id"]] = {
                        "monday": fila["monday"] == "1",
                        "tuesday": fila["tuesday"] == "1",
                        "wednesday": fila["wednesday"] == "1",
                        "thursday": fila["thursday"] == "1",
                        "friday": fila["friday"] == "1",
                        "saturday": fila["saturday"] == "1",
                        "sunday": fila["sunday"] == "1",
                        "start_date": fila["start_date"],
                        "end_date": fila["end_date"]
                    }

        ids_paradas_tranvia = set()
        self.trip_schedules_tranvia = {}
        with open(ruta_stop_times, mode="r", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                tid = fila["trip_id"]
                if tid in trips_tranvia:
                    sid = re.sub(r'_Plataforma_Q\d+', '', fila["stop_id"])
                    ids_paradas_tranvia.add(sid)
                    seq = int(fila.get("stop_sequence", 0))
                    
                    dep = fila.get("departure_time", "")
                    if dep:
                        parts = dep.split(":")
                        if len(parts) >= 3:
                            secs = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                            if sid not in self.horarios_tranvia:
                                self.horarios_tranvia[sid] = []
                            self.horarios_tranvia[sid].append((tid, secs))
                            
                            if tid not in self.trip_schedules_tranvia:
                                self.trip_schedules_tranvia[tid] = []
                            self.trip_schedules_tranvia[tid].append((seq, sid, secs))

        # Sort schedules by time
        for sid in self.horarios_tranvia:
            self.horarios_tranvia[sid].sort(key=lambda x: x[1])
            
        # Sort trip sequences
        for tid in self.trip_schedules_tranvia:
            self.trip_schedules_tranvia[tid].sort(key=lambda x: x[0])

        with open(ruta_stops, mode="r", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                id_estacion = re.sub(r'_Plataforma_Q\d+', '', fila["stop_id"])
                if id_estacion in ids_paradas_tranvia:
                    nombre = fila["stop_name"]
                    latitud = float(fila["stop_lat"])
                    longitud = float(fila["stop_lon"])
                    nueva_estacion = Estacion(id_estacion, nombre, latitud, longitud)
                    self.estaciones_globales[id_estacion] = nueva_estacion

        self.datos_cargados = True
        print(f"¡Tranvía aislado! {len(self.estaciones_globales)} estaciones cargadas.")
    
    # ─── CARGA METRO BILBAO ───
    def cargar_metro_gtfs(self, ruta_carpeta: str):
        if self.datos_metro_cargados:
            return
        
        print(f"Cargando Metro Bilbao desde {ruta_carpeta}")
        
        ruta_stops = os.path.join(ruta_carpeta, "stops.txt")
        ruta_trips = os.path.join(ruta_carpeta, "trips.txt")
        ruta_stop_times = os.path.join(ruta_carpeta, "stop_times.txt")
        
        import re
        # Leer todas las estaciones de Metro
        with open(ruta_stops, mode="r", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                id_est = fila["stop_id"].replace(".0", "")
                nombre = fila["stop_name"].strip()
                
                # Limpiar el nombre: "74 (Berango)" -> "Berango"
                match = re.match(r"^\d+\s*\((.*?)\)$", nombre)
                if match:
                    nombre = match.group(1).strip()
                    
                lat = float(fila["stop_lat"].strip())
                lon = float(fila["stop_lon"].strip())
                nueva = Estacion(f"metro_{id_est}", nombre, lat, lon)
                self.estaciones_metro[f"metro_{id_est}"] = nueva
        
        # Determinar qué estaciones van a L1 y cuáles a L2
        l1_shapes = {"BSR_PLE", "ETX_IBB", "ETX_LAR", "ETX_PLE", "ETX_SOP", "IBB_ETX", "LAR_ETX", "PLE_BSR", "PLE_ETX", "SOP_BSR", "SOP_ETX"}
        l2_shapes = {"ANS_BSR", "BSR_KAB", "BSR_SIN", "ETX_KAB", "KAB_BSR", "SIN_BSR", "SIN_KAB"}
        
        # 1. Parse trips
        self.trips_info = {} # trip_id -> (linea_real, service_id, trip_headsign)
        trip_shapes = {}
        with open(ruta_trips, mode="r", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                tid = fila["trip_id"]
                shape = fila.get("shape_id", "")
                trip_shapes[tid] = shape
                linea_real = "L1" if shape in l1_shapes else ("L2" if shape in l2_shapes else "L1")
                self.trips_info[tid] = (
                    linea_real,
                    fila.get("service_id", ""),
                    fila.get("trip_headsign", ""),
                    fila.get("direction_id", "0")
                )
        
        # 2. Parse calendar
        self.calendar = {} # service_id -> {days, start, end}
        ruta_calendar = os.path.join(ruta_carpeta, "calendar.txt")
        if os.path.exists(ruta_calendar):
            with open(ruta_calendar, mode="r", encoding="utf-8") as archivo:
                lector = csv.DictReader(archivo)
                for fila in lector:
                    self.calendar[fila["service_id"]] = {
                        "monday": fila["monday"] == "1",
                        "tuesday": fila["tuesday"] == "1",
                        "wednesday": fila["wednesday"] == "1",
                        "thursday": fila["thursday"] == "1",
                        "friday": fila["friday"] == "1",
                        "saturday": fila["saturday"] == "1",
                        "sunday": fila["sunday"] == "1",
                        "start_date": fila["start_date"],
                        "end_date": fila["end_date"]
                    }

        # Get ordered stops per shape (use one representative trip per shape)
        shape_trips = {}
        for tid, sid in trip_shapes.items():
            if sid not in shape_trips:
                shape_trips[sid] = tid
        
        # Read stop_times
        self.l1_stops_ordered = []
        self.l2_stops_ordered = []
        self.tranvia_stops_ordered = ["ES:Euskotren:Quay:2674:", "ES:Euskotren:Quay:2673:", "ES:Euskotren:Quay:1468:", "ES:Euskotren:Quay:1473:", "ES:Euskotren:Quay:1480:", "ES:Euskotren:Quay:1471:", "ES:Euskotren:Quay:1478:", "ES:Euskotren:Quay:1469:", "ES:Euskotren:Quay:1476:", "ES:Euskotren:Quay:1475:", "ES:Euskotren:Quay:1479:", "ES:Euskotren:Quay:1474:", "ES:Euskotren:Quay:1470:", "ES:Euskotren:Quay:1472:", "ES:Euskotren:Quay:1481:", "ES:Euskotren:Quay:1477:"]
        self.horarios_metro = {} # stop_id -> [(trip_id, departure_time_seconds), ...]
        self.trip_schedules_metro = {}
        
        trip_stop_seqs = {}
        with open(ruta_stop_times, mode="r", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                tid = fila["trip_id"]
                sid_raw = fila["stop_id"].replace(".0", "")
                sid = f"metro_{sid_raw}"
                seq = int(fila["stop_sequence"])
                
                # Save sequences for topology
                if tid in trip_stop_seqs:
                    trip_stop_seqs[tid].append((seq, sid_raw))
                else:
                    trip_stop_seqs[tid] = [(seq, sid_raw)]
                
                # Save schedule
                dep = fila.get("departure_time", "")
                if dep:
                    parts = dep.split(":")
                    if len(parts) >= 3:
                        secs = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                        if sid not in self.horarios_metro:
                            self.horarios_metro[sid] = []
                        self.horarios_metro[sid].append((tid, secs))
                        
                        if tid not in self.trip_schedules_metro:
                            self.trip_schedules_metro[tid] = []
                        self.trip_schedules_metro[tid].append((seq, sid, secs))
        
        # Sort schedules by time
        for sid in self.horarios_metro:
            self.horarios_metro[sid].sort(key=lambda x: x[1])
            
        for tid in self.trip_schedules_metro:
            self.trip_schedules_metro[tid].sort(key=lambda x: x[0])

        # L1: use ETX_PLE shape (longest L1 route, stops at Etxebarri)
        l1_trip = shape_trips.get("ETX_PLE")
        if l1_trip and l1_trip in trip_stop_seqs:
            stops = sorted(trip_stop_seqs[l1_trip], key=lambda x: x[0])
            self.l1_stops_ordered = [f"metro_{s[1]}" for s in stops]
        
        # L2: use BSR_KAB shape (longest L2 route)
        l2_trip = shape_trips.get("BSR_KAB")
        if l2_trip and l2_trip in trip_stop_seqs:
            stops = sorted(trip_stop_seqs[l2_trip], key=lambda x: x[0])
            self.l2_stops_ordered = [f"metro_{s[1]}" for s in stops]
        
        self.datos_metro_cargados = True
        print(f"¡Metro Bilbao! {len(self.estaciones_metro)} estaciones. L1={len(self.l1_stops_ordered)} paradas, L2={len(self.l2_stops_ordered)} paradas.")
        
    # 🚌 CARGA AUTOBUSES (BILBOBUS) 🚌
    def cargar_bus_gtfs(self, ruta_carpeta: str):
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
        # Evaluate standard calendar (Relaxed date check to show all lines)
        for srv_id, c in self.calendar_bus.items():
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
        return salidas


    def obtener_horarios_estaticos_bus(self, stop_id: str):
        import datetime
        now = datetime.datetime.now()
        
        today_str = now.strftime("%Y%m%d")
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        current_day_name = day_names[now.weekday()]
        
        active_services = set()
        # Evaluate standard calendar (Relaxed date check to show all lines)
        for srv_id, c in self.calendar_bus.items():
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
                
            linea_nombre = trip_info.get("route", "??")
            destino = trip_info.get("headsign", "Desconocido")
            
            # Format time HH:MM handling >24h GTFS times
            h = (d_secs // 3600) % 24
            m = (d_secs % 3600) // 60
            time_str = f"{h:02d}:{m:02d}"
            
            salidas.append({
                "linea": linea_nombre,
                "destino": destino,
                "hora_str": time_str,
                "d_secs": d_secs
            })
            
        # Agrupar por línea y destino
        agrupados = {}
        for s in salidas:
            clave = f"{s['linea']}||{s['destino']}"
            if clave not in agrupados:
                agrupados[clave] = {
                    "linea": s['linea'],
                    "destino": s['destino'],
                    "horarios": []
                }
            agrupados[clave]["horarios"].append(s)
            
        # Sort and clean up
        for k in agrupados:
            agrupados[k]["horarios"].sort(key=lambda x: x["d_secs"])
            # Remove duplicates if any
            unique_horas = []
            for h in agrupados[k]["horarios"]:
                if h["hora_str"] not in unique_horas:
                    unique_horas.append(h["hora_str"])
            agrupados[k]["horas_str"] = unique_horas
            del agrupados[k]["horarios"]
            
        return list(agrupados.values())

    def obtener_linea(self, id_linea: str) -> Linea:
        return self.lineas_globales.get(id_linea)

    def obtener_proximas_salidas(self, stop_id: str):
        import datetime
        now = datetime.datetime.now()
        current_secs = now.hour * 3600 + now.minute * 60 + now.second
        
        # Determine current day of week
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        current_day = days[now.weekday()]
        
        # Active services today
        active_services = set()
        date_int = int(now.strftime("%Y%m%d"))
        for s_id, cal in self.calendar.items():
            if cal[current_day] and int(cal["start_date"]) <= date_int <= int(cal["end_date"]):
                active_services.add(s_id)
        
        # Ensure we only include lines that serve this station
        lineas_estacion = set()
        if stop_id in self.l1_stops_ordered:
            lineas_estacion.add("L1")
        if stop_id in self.l2_stops_ordered:
            lineas_estacion.add("L2")

        salidas = []
        if stop_id in self.horarios_metro:
            for tid, secs in self.horarios_metro[stop_id]:
                if secs < current_secs:
                    continue
                trip_info = self.trips_info.get(tid)
                if not trip_info:
                    continue
                route_id, service_id, headsign, direction_id = trip_info
                
                # Filtrar viajes que no corresponden a la línea de la estación (ej. depot runs de L1 en Basauri)
                if lineas_estacion and route_id not in lineas_estacion:
                    continue
                
                if service_id in active_services:
                    minutos = (secs - current_secs) // 60
                    hora_real = (secs // 3600) % 24
                    hora_str = f"{hora_real:02d}:{(secs % 3600) // 60:02d}"
                    salidas.append({
                        "linea": route_id,
                        "destino": headsign,
                        "minutos": minutos,
                        "hora_exacta": hora_str,
                        "direccion": direction_id
                    })
        return salidas

    def obtener_proximas_salidas_tranvia(self, stop_id: str):
        import datetime
        now = datetime.datetime.now()
        current_secs = now.hour * 3600 + now.minute * 60 + now.second
        
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        current_day = days[now.weekday()]
        
        active_services = set()
        date_int = int(now.strftime("%Y%m%d"))
        for s_id, cal in self.calendar_tranvia.items():
            if cal[current_day] and int(cal["start_date"]) <= date_int <= int(cal["end_date"]):
                active_services.add(s_id)
        
        salidas = []
        if stop_id in self.horarios_tranvia:
            for tid, secs in self.horarios_tranvia[stop_id]:
                if secs < current_secs:
                    continue
                trip_info = self.trips_info_tranvia.get(tid)
                if not trip_info:
                    continue
                route_id, service_id, headsign, direction_id = trip_info
                if service_id in active_services:
                    minutos = (secs - current_secs) // 60
                    hora_real = (secs // 3600) % 24
                    hora_str = f"{hora_real:02d}:{(secs % 3600) // 60:02d}"
                    salidas.append({
                        "linea": route_id,
                        "destino": headsign,
                        "minutos": minutos,
                        "hora_exacta": hora_str,
                        "direccion": direction_id
                    })
        return salidas


# ═══════════════════════════════════
# SIMULADOR TRANVÍA
# ═══════════════════════════════════
# MONITOR EN TIEMPO REAL
# ═══════════════════════════════════
class MonitorTiempoReal:
    def __init__(self, gestor):
        self.gestor = gestor

    async def iniciar_bucle(self, ws_manager):
        import asyncio
        import datetime
        
        while True:
            now = datetime.datetime.now()
            current_secs = now.hour * 3600 + now.minute * 60 + now.second
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            current_day = days[now.weekday()]
            date_int = int(now.strftime("%Y%m%d"))
            
            # Identify active services for Tranvia
            active_services_tr = set()
            for s_id, cal in self.gestor.calendar_tranvia.items():
                if cal[current_day] and int(cal["start_date"]) <= date_int <= int(cal["end_date"]):
                    active_services_tr.add(s_id)
                    
            # Identify active services for Metro
            active_services_m = set()
            for s_id, cal in self.gestor.calendar.items():
                if cal[current_day] and int(cal["start_date"]) <= date_int <= int(cal["end_date"]):
                    active_services_m.add(s_id)
            
            actualizaciones_tranvia = self._simular_flota(
                self.gestor.trip_schedules_tranvia,
                self.gestor.trips_info_tranvia,
                active_services_tr,
                self.gestor.estaciones_globales,
                current_secs,
                "tranvia"
            )
            
            actualizaciones_metro = self._simular_flota(
                self.gestor.trip_schedules_metro,
                self.gestor.trips_info,
                active_services_m,
                self.gestor.estaciones_metro,
                current_secs,
                "metro"
            )

            if actualizaciones_tranvia:
                await ws_manager.broadcast_json({"tipo": "posiciones", "datos": actualizaciones_tranvia})
            else:
                await ws_manager.broadcast_json({"tipo": "posiciones", "datos": []})
                
            if actualizaciones_metro:
                await ws_manager.broadcast_json({"tipo": "posiciones_metro", "datos": actualizaciones_metro})
            else:
                await ws_manager.broadcast_json({"tipo": "posiciones_metro", "datos": []})
            
            await asyncio.sleep(2.0) # Update every 2 seconds for smooth UI animation

    def _simular_flota(self, trip_schedules, trips_info, active_services, estaciones, current_secs, tipo):
        actualizaciones = []
        for tid, schedule in trip_schedules.items():
            if not schedule or len(schedule) < 2:
                continue
                
            info = trips_info.get(tid)
            if not info: continue
            route_id, service_id, headsign, direction_id = info
            
            if service_id not in active_services:
                continue
                
            start_time = schedule[0][2]
            end_time = schedule[-1][2]
            
            if start_time <= current_secs <= end_time:
                for i in range(len(schedule) - 1):
                    _, sid_a, time_a = schedule[i]
                    _, sid_b, time_b = schedule[i+1]
                    
                    if time_a <= current_secs <= time_b:
                        if time_b == time_a:
                            progress = 0
                        else:
                            progress = (current_secs - time_a) / (time_b - time_a)
                            
                        est_a = estaciones.get(sid_a)
                        est_b = estaciones.get(sid_b)
                        
                        if est_a and est_b:
                            lat = est_a.latitud + (est_b.latitud - est_a.latitud) * progress
                            lon = est_a.longitud + (est_b.longitud - est_a.longitud) * progress
                            
                            veh_id = f"{'TR' if tipo == 'tranvia' else 'M'}-{tid[-6:]}"
                            
                            actualizaciones.append({
                                "id": veh_id,
                                "lat": lat,
                                "lon": lon,
                                "estado": "En ruta",
                                "destino": headsign,
                                "tipo": tipo,
                                "linea": route_id if tipo == 'metro' else 'TR'
                            })
                        break
        return actualizaciones