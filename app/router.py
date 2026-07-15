from fastapi import APIRouter
from app.gestor import GestorRed

router = APIRouter()
gestor = GestorRed()

@router.get("/estaciones")
async def obtener_estaciones():
    return list(gestor.estaciones_globales.values())

@router.get("/estaciones_metro")
async def obtener_estaciones_metro():
    return [
        {
            "id": e.id,
            "nombre": e.nombre,
            "latitud": e.latitud,
            "longitud": e.longitud,
            "lineas": _determinar_lineas_estacion(e.id, gestor),
            "orden_l1": gestor.l1_stops_ordered.index(e.id) if e.id in gestor.l1_stops_ordered else 999,
            "orden_l2": gestor.l2_stops_ordered.index(e.id) if e.id in gestor.l2_stops_ordered else 999
        }
        for e in gestor.estaciones_metro.values()
    ]

@router.get("/proximas_salidas_bus/{stop_id}")
async def proximas_salidas_bus(stop_id: str):
    salidas = gestor.obtener_proximas_salidas_bus(stop_id)
    return {"salidas": salidas}

@router.get("/horarios_estaticos_bus/{stop_id}")
async def horarios_estaticos_bus(stop_id: str):
    horarios = gestor.obtener_horarios_estaticos_bus(stop_id)
    return {"rutas": horarios}

@router.get("/estaciones_bus")
async def obtener_estaciones_bus():
    return [
        {
            "id": e.id,
            "nombre": e.nombre,
            "latitud": e.latitud,
            "longitud": e.longitud,
            "lineas": e.lineas
        }
        for e in gestor.estaciones_bus.values()
    ]

def _determinar_lineas_estacion(est_id, gestor):
    lineas = []
    if est_id in gestor.l1_stops_ordered:
        lineas.append("L1")
    if est_id in gestor.l2_stops_ordered:
        lineas.append("L2")
    return lineas

from app.enrutamiento import EnrutamientoHibrido

enrutador = None

def init_enrutador(g):
    global enrutador
    enrutador = EnrutamientoHibrido(g)
    enrutador.construir_grafo_gtfs()

@router.get("/ruta")
async def buscar_ruta(origen: str, destino: str):
    if not enrutador:
        return {"error": "Enrutador no inicializado"}
    
    ruta = enrutador.calcular_ruta_a_estrella(origen, destino)
    if ruta:
        return ruta
    return {"error": "Ruta no encontrada"}

@router.get("/horarios_metro/{stop_id}")
async def obtener_horarios_metro(stop_id: str):
    return gestor.obtener_proximas_salidas(stop_id)

@router.get("/horarios_tranvia/{stop_id}")
async def obtener_horarios_tranvia(stop_id: str):
    return gestor.obtener_proximas_salidas_tranvia(stop_id)