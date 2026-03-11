"""
API Principal - FastAPI con WebSockets
Sistema de Monitorización de Impresoras 3D
"""
import asyncio
import base64
from typing import Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Response, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.octoprint_client import octoprint_client
from app.roboflow_client import roboflow_client
from app.image_processor import draw_detections, get_detection_summary
from app.setup import keyMangement



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

# Estado previo para detectar transiciones de impresión
_previous_printing = False
_known_timelapses: set = set()


# Tarea en segundo plano para push de datos
async def broadcast_updates():
    global _previous_printing, _known_timelapses
    """Obtiene datos y los envía a todos los clientes cada 3 segundos"""
    while True:
        if manager.active_connections:
            try:
                # Obtener estado de OctoPrint (síncrono, ejecutar en thread)
                loop = asyncio.get_event_loop()
                status_raw = await loop.run_in_executor(
                    None, octoprint_client.get_printer_status
                )
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
                image_bytes = await loop.run_in_executor(
                    None, octoprint_client.get_snapshot
                )
                snapshot_b64 = None
                detections = {"has_errors": False, "total_detections": 0, "classes": {}}
                
                if image_bytes:
                    predictions_result = roboflow_client.detect_errors_from_bytes(image_bytes)
                    predictions = predictions_result.get("predictions", [])
                    detections = get_detection_summary(predictions)
                    
                    # Procesar imagen con bounding boxes
                    processed_image = draw_detections(image_bytes, predictions)
                    snapshot_b64 = base64.b64encode(processed_image).decode('utf-8')
                
                # Cancelación automática si hay errores y está imprimiendo
                auto_cancelled = False
                if detections.get("has_errors", False) and "print" in status["state"].lower():
                    print("[Auto-cancel] Error detectado, cancelando impresión...")
                    await loop.run_in_executor(None, octoprint_client.cancel_print)
                    auto_cancelled = True
                    # Actualizar estado después de cancelar
                    status_raw = await loop.run_in_executor(None, octoprint_client.get_printer_status)
                    printer = status_raw.get("printer", {})
                    status["state"] = printer.get("state", {}).get("text", "Desconocido")

                # Detectar transición de impresión → no-impresión
                currently_printing = "print" in status["state"].lower()
                print_just_ended = _previous_printing and not currently_printing
                _previous_printing = currently_printing
                
                # Enviar a todos los clientes
                await manager.broadcast({
                    "type": "update",
                    "data": {
                        "status": status,
                        "detections": detections,
                        "snapshot": f"data:image/jpeg;base64,{snapshot_b64}" if snapshot_b64 else None,
                        "auto_cancelled": auto_cancelled
                    }
                })

                # Si la impresión acaba de terminar, buscar timelapses nuevos
                if print_just_ended:
                    print("[Timelapse] Impresión finalizada, esperando renderizado del timelapse...")
                    # Lanzar tarea para no bloquear el broadcast
                    asyncio.create_task(_check_and_notify_timelapse())

            except Exception as e:
                print(f"Error en broadcast: {e}")
        
        await asyncio.sleep(1)


async def _check_and_notify_timelapse():
    """
    Espera a que OctoPrint renderice el timelapse y notifica a los clientes
    si hay archivos nuevos disponibles.
    """
    global _known_timelapses

    # Esperar a que OctoPrint renderice el timelapse
    await asyncio.sleep(15)

    loop = asyncio.get_event_loop()

    # Reintentar varias veces por si el renderizado toma más tiempo
    for attempt in range(5):
        try:
            current_files = await loop.run_in_executor(
                None, octoprint_client.list_timelapses
            )
            current_names = {f["name"] for f in current_files}

            # Detectar archivos nuevos
            new_files = [
                f for f in current_files if f["name"] not in _known_timelapses
            ]

            # Actualizar lista conocida
            _known_timelapses = current_names

            if new_files:
                print(f"[Timelapse] {len(new_files)} nuevo(s) encontrado(s): "
                      f"{[f['name'] for f in new_files]}")
                await manager.broadcast({
                    "type": "timelapse_ready",
                    "files": new_files
                })
                return
            else:
                print(f"[Timelapse] Intento {attempt + 1}/5: "
                      "sin timelapse nuevo aún, esperando...")
                await asyncio.sleep(10)
        except Exception as e:
            print(f"[Timelapse] Error al consultar timelapses: {e}")
            await asyncio.sleep(10)

    print("[Timelapse] No se encontraron timelapses nuevos tras 5 intentos.")


# Lifecycle para iniciar/parar tarea de broadcast
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _known_timelapses

    # cargar modelo local en background para que los pesos se descarguen
    try:
        roboflow_client._load_model()
    except Exception as e:
        print(f"[Inference] aviso: error al precargar modelo: {e}")

    # Inicializar lista de timelapses conocidos
    try:
        existing = octoprint_client.list_timelapses()
        _known_timelapses = {f["name"] for f in existing}
        print(f"[Timelapse] {len(_known_timelapses)} timelapses existentes al inicio.")
    except Exception as e:
        print(f"[Timelapse] No se pudieron cargar timelapses existentes: {e}")

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
            
            loop = asyncio.get_event_loop()
            
            if action == "pause":
                success = await loop.run_in_executor(
                    None, octoprint_client.pause_print
                )
                await websocket.send_json({
                    "type": "command_result",
                    "action": "pause",
                    "success": success
                })
            elif action == "resume":
                success = await loop.run_in_executor(
                    None, octoprint_client.resume_print
                )
                await websocket.send_json({
                    "type": "command_result",
                    "action": "resume",
                    "success": success
                })
            elif action == "cancel":
                success = await loop.run_in_executor(
                    None, octoprint_client.cancel_print
                )
                await websocket.send_json({
                    "type": "command_result",
                    "action": "cancel",
                    "success": success
                })
            elif action == "start":
                success = await loop.run_in_executor(
                    None, octoprint_client.start_print
                )
                await websocket.send_json({
                    "type": "command_result",
                    "action": "start",
                    "success": success
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ==================== REST Endpoints ====================

@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {"message": "3D Printer Monitor API", "status": "running", "websocket": "/ws"}


@app.get("/api/status")
async def get_status():
    """Obtiene el estado actual (también disponible vía WebSocket)"""
    loop = asyncio.get_event_loop()
    status = await loop.run_in_executor(
        None, octoprint_client.get_printer_status
    )
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


@app.post("/api/upload")
async def upload_gcode(file: UploadFile = File(...)):
    """Sube un archivo G-code a OctoPrint"""
    if not file.filename.lower().endswith(('.gcode', '.gco', '.g')):
        return {"success": False, "error": "El archivo debe ser .gcode, .gco o .g"}
    
    content = await file.read()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, octoprint_client.upload_gcode, content, file.filename
    )
    return result


@app.get("/api/files")
async def list_files():
    """Lista los archivos G-code disponibles en OctoPrint"""
    loop = asyncio.get_event_loop()
    files = await loop.run_in_executor(
        None, octoprint_client.list_files
    )
    return {"files": files}


@app.post("/api/files/select/{filename}")
async def select_file(filename: str):
    """Selecciona un archivo G-code para imprimir"""
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(
        None, octoprint_client.select_file, filename
    )
    return {
        "success": success,
        "message": f"Archivo '{filename}' seleccionado" if success else "Error al seleccionar archivo"
    }


# ==================== Timelapse Endpoints ====================

@app.get("/api/timelapse")
async def list_timelapses():
    """Lista los timelapses disponibles en OctoPrint"""
    loop = asyncio.get_event_loop()
    timelapses = await loop.run_in_executor(
        None, octoprint_client.list_timelapses
    )
    return {"files": timelapses}


@app.get("/api/timelapse/download/{filename}")
async def download_timelapse(filename: str):
    """Descarga un timelapse de OctoPrint"""
    loop = asyncio.get_event_loop()
    content = await loop.run_in_executor(
        None, octoprint_client.download_timelapse, filename
    )
    if content is None:
        return {"error": "Timelapse no encontrado"}
    return Response(
        content=content,
        media_type="video/mp4",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.delete("/api/timelapse/{filename}")
async def delete_timelapse(filename: str):
    """Elimina un timelapse de OctoPrint"""
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(
        None, octoprint_client.delete_timelapse, filename
    )
    return {
        "success": success,
        "message": f"Timelapse '{filename}' eliminado" if success else "Error al eliminar timelapse"
    }


# Entry point para ejecutar el servidor directamente
if __name__ == "__main__":
    import sys
    import uvicorn

    if not keyMangement.validate_configuration():
        print("Configuración de OctoPrint no válida. Por favor corrige los errores e intenta de nuevo.")
        sys.exit(1)

    uvicorn.run(app, host="0.0.0.0", port=8000)

