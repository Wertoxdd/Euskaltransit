import re

def update_gestor():
    path = 'app/gestor.py'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_func = """
    def obtener_horarios_estaticos_bus(self, stop_id: str):
        import datetime
        now = datetime.datetime.now()
        
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

    def obtener_linea(self"""
    content = content.replace("    def obtener_linea(self", new_func)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_router():
    path = 'app/router.py'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_route = """async def proximas_salidas_bus(stop_id: str):
    salidas = gestor.obtener_proximas_salidas_bus(stop_id)
    return {"salidas": salidas}

@router.get("/horarios_estaticos_bus/{stop_id}")
async def horarios_estaticos_bus(stop_id: str):
    horarios = gestor.obtener_horarios_estaticos_bus(stop_id)
    return {"rutas": horarios}"""
    content = content.replace("""async def proximas_salidas_bus(stop_id: str):
    salidas = gestor.obtener_proximas_salidas_bus(stop_id)
    return {"salidas": salidas}""", new_route)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

update_gestor()
update_router()
print("Backend actualizado con los nuevos endpoints de horarios estáticos.")
