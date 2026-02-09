"""
API Principal - FastAPI con WebSockets
Sistema de Monitorización de Impresoras 3D
"""
import asyncio
import base64
from typing import Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .octoprint_client import octoprint_client
from .roboflow_client import roboflow_client
from .image_processor import draw_detections, get_detection_summary
from .config import load_settings, save_settings


# Gestión de clientes WebSocket conectados
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
    
    async def broadcast(self, message: dict):
        """Envía mensaje a todos los clientes conectados"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        # Eliminar conexiones muertas
        self.active_connections -= disconnected


manager = ConnectionManager()


# Tarea en segundo plano para push de datos
async def broadcast_updates():
    """Obtiene datos y los envía a todos los clientes cada 3 segundos"""
    while True:
        if manager.active_connections:
            try:
                # Obtener estado de OctoPrint
                status_raw = await octoprint_client.get_printer_status()
                printer = status_raw.get("printer", {})
                job = status_raw.get("job", {})
                
                status = {
                    "connected": status_raw.get("connected", False),
                    "state": printer.get("state", {}).get("text", "Desconocido"),
                    "temperatures": {
                        "bed": printer.get("temperature", {}).get("bed", {}),
                        "tool0": printer.get("temperature", {}).get("tool0", {})
                    },
                    "job": {
                        "file": job.get("job", {}).get("file", {}).get("name", "Sin archivo"),
                        "progress": job.get("progress", {}).get("completion", 0),
                        "time_elapsed": job.get("progress", {}).get("printTime", 0),
                        "time_remaining": job.get("progress", {}).get("printTimeLeft", 0)
                    },
                    "error": status_raw.get("error")
                }
                
                # Obtener imagen y detecciones
                image_bytes = await octoprint_client.get_snapshot()
                snapshot_b64 = None
                detections = {"has_errors": False, "total_detections": 0, "classes": {}}
                
                if image_bytes:
                    predictions_result = roboflow_client.detect_errors_from_bytes(image_bytes)
                    predictions = predictions_result.get("predictions", [])
                    detections = get_detection_summary(predictions)
                    
                    # Procesar imagen con bounding boxes
                    processed_image = draw_detections(image_bytes, predictions)
                    snapshot_b64 = base64.b64encode(processed_image).decode('utf-8')
                
                # Enviar a todos los clientes
                await manager.broadcast({
                    "type": "update",
                    "data": {
                        "status": status,
                        "detections": detections,
                        "snapshot": f"data:image/jpeg;base64,{snapshot_b64}" if snapshot_b64 else None
                    }
                })
            except Exception as e:
                print(f"Error en broadcast: {e}")
        
        await asyncio.sleep(3)


# Lifecycle para iniciar/parar tarea de broadcast
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Iniciar tarea de broadcast
    task = asyncio.create_task(broadcast_updates())
    yield
    # Parar tarea al cerrar
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="3D Printer Monitor API",
    description="API para monitorización de impresoras 3D con detección de errores",
    version="2.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SettingsModel(BaseModel):
    octoprint_url: str
    octoprint_api_key: str
    roboflow_api_key: str | None = None
    confidence_threshold: float | None = None


# ==================== WebSocket ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket para comunicación bidireccional.
    - Recibe comandos: {"action": "pause"} o {"action": "resume"}
    - Envía actualizaciones automáticamente cada 3 segundos
    """
    await manager.connect(websocket)
    try:
        while True:
            # Recibir comandos del cliente
            data = await websocket.receive_json()
            action = data.get("action")
            
            if action == "pause":
                success = await octoprint_client.pause_print()
                await websocket.send_json({
                    "type": "command_result",
                    "action": "pause",
                    "success": success
                })
            elif action == "resume":
                success = await octoprint_client.resume_print()
                await websocket.send_json({
                    "type": "command_result",
                    "action": "resume",
                    "success": success
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ==================== REST Endpoints ====================

@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {"message": "3D Printer Monitor API", "status": "running", "websocket": "/ws"}


@app.get("/api/settings")
async def get_settings():
    """Obtiene la configuración actual"""
    settings = load_settings()
    if settings.get("octoprint_api_key"):
        key = settings["octoprint_api_key"]
        if len(key) > 8:
            settings["octoprint_api_key_masked"] = key[:4] + "****" + key[-4:]
        else:
            settings["octoprint_api_key_masked"] = "****"
    return settings


@app.post("/api/settings")
async def update_settings(new_settings: SettingsModel):
    """Actualiza la configuración"""
    current = load_settings()
    current["octoprint_url"] = new_settings.octoprint_url
    current["octoprint_api_key"] = new_settings.octoprint_api_key
    
    if new_settings.roboflow_api_key:
        current["roboflow_api_key"] = new_settings.roboflow_api_key
    if new_settings.confidence_threshold is not None:
        current["confidence_threshold"] = new_settings.confidence_threshold
    
    success = save_settings(current)
    return {
        "success": success,
        "message": "Configuración guardada" if success else "Error al guardar"
    }


@app.get("/api/status")
async def get_status():
    """Obtiene el estado actual (también disponible vía WebSocket)"""
    status = await octoprint_client.get_printer_status()
    printer = status.get("printer", {})
    job = status.get("job", {})
    
    return {
        "connected": status.get("connected", False),
        "state": printer.get("state", {}).get("text", "Desconocido"),
        "temperatures": {
            "bed": printer.get("temperature", {}).get("bed", {}),
            "tool0": printer.get("temperature", {}).get("tool0", {})
        },
        "job": {
            "file": job.get("job", {}).get("file", {}).get("name", "Sin archivo"),
            "progress": job.get("progress", {}).get("completion", 0),
            "time_elapsed": job.get("progress", {}).get("printTime", 0),
            "time_remaining": job.get("progress", {}).get("printTimeLeft", 0)
        },
        "error": status.get("error")
    }
