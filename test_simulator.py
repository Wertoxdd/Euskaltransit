import sys
import os
import datetime

# Agrega la ruta raíz al sys.path para poder importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.gestor import GestorRed, MonitorTiempoReal

gestor = GestorRed()
gestor.cargar_gtfs("datos")
gestor.cargar_metro_gtfs("datos_metro")

now = datetime.datetime.now()
current_secs = now.hour * 3600 + now.minute * 60 + now.second
days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
current_day = days[now.weekday()]
date_int = int(now.strftime("%Y%m%d"))

active_services_tr = set()
for s_id, cal in gestor.calendar_tranvia.items():
    if cal[current_day] and int(cal["start_date"]) <= date_int <= int(cal["end_date"]):
        active_services_tr.add(s_id)

monitor = MonitorTiempoReal(gestor)
tranvias = monitor._simular_flota(
    gestor.trip_schedules_tranvia,
    gestor.trips_info_tranvia,
    active_services_tr,
    gestor.estaciones_globales,
    current_secs,
    "tranvia"
)

print(f"Hora actual simulada: {now}")
print(f"Segundos actuales: {current_secs}")
print(f"Tranvías activos encontrados: {len(tranvias)}")
if tranvias:
    print("Muestra 3 tranvías:", tranvias[:3])
else:
    print("No hay tranvías activos en este instante. Probando a forzar la hora a las 14:00:00 (50400 secs)")
    tranvias_forced = monitor._simular_flota(
        gestor.trip_schedules_tranvia,
        gestor.trips_info_tranvia,
        active_services_tr,
        gestor.estaciones_globales,
        50400,
        "tranvia"
    )
    print(f"Tranvías a las 14:00: {len(tranvias_forced)}")
    if tranvias_forced:
        print("Muestra 3:", tranvias_forced[:3])
