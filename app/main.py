from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.router import router as api_router, gestor, init_enrutador
from app.gestor import MonitorTiempoReal
from app.ws_manager import manager
import asyncio
from app.overpass_client import OverpassClient

app = FastAPI(title="EuskalTransit API")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    # Usar el gestor global del router
    gestor.cargar_gtfs("datos/")
    gestor.cargar_metro_gtfs("datos_metro/")
    gestor.cargar_bus_gtfs("datos_bus/")
    
    # Iniciar Enrutador Híbrido
    init_enrutador(gestor)
    
    # Integrar topología peatonal para la estación intermodal de Abando
    # (Lat, Lon) de Abando
    print("Integrando topología de andenes de Abando...")
    from app.router import enrutador
    overpass_client = OverpassClient()
    # Desactivamos Overpass temporalmente para evitar 504 Gateway Timeouts que bloquean el frontend
    # enrutador.integrar_topologia_peatonal(overpass_client, 43.2608, -2.9275, 100)
    
    # Real-time monitor (Disabled for now as per user request)
    monitor_rt = MonitorTiempoReal(gestor)
    # asyncio.create_task(monitor_rt.iniciar_bucle(manager))

@app.get("/")
async def read_index():
    return FileResponse('app/index.html')

@app.websocket("/ws/posiciones")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)