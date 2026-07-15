import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.gestor import GestorRed
from app.enrutamiento import EnrutamientoHibrido

gestor = GestorRed()
gestor.cargar_gtfs("datos")
gestor.cargar_metro_gtfs("datos_metro")

enrutador = EnrutamientoHibrido(gestor)
enrutador.construir_grafo_gtfs()

id_deusto = gestor.l1_stops_ordered[0] if gestor.l1_stops_ordered else None
id_guggenheim = gestor.tranvia_stops_ordered[-1] if gestor.tranvia_stops_ordered else None



print(f"Buscando ruta de {id_deusto} a {id_guggenheim}...")
if id_deusto and id_guggenheim:
    ruta = enrutador.calcular_ruta_a_estrella(id_deusto, id_guggenheim)
    if ruta:
        print(f"¡Ruta encontrada! Tiempo total: {ruta['tiempo_total_s']}s")
        print(f"Tren: {ruta['tiempo_tren_s']}s, Peatonal: {ruta['tiempo_peatonal_s']}s")
        for seg in ruta['segmentos']:
            print(f"- {seg['desde_nombre']} -> {seg['hasta_nombre']} ({seg['detalle']['tipo']})")
    else:
        print("No se encontró ruta multimodal.")
else:
    print("Estaciones no encontradas.")
