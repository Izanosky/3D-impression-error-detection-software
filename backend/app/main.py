"""
API Principal — FastAPI con WebSockets.
Sistema de Monitorización de Impresoras 3D.

Este módulo define:
  - Un WebSocket bidireccional en /ws para enviar estado en tiempo real
    y recibir comandos (pause, resume, cancel, start).
  - Endpoints REST para consultar estado, subir archivos G-code,
    listar archivos y gestionar timelapses.
  - Una tarea en segundo plano que hace broadcast del estado cada segundo.
"""
import asyncio
from typing import Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect, Response
from fastapi.middleware.cors import CORSMiddleware

from app.octoprint_client import octoprint_client
from app.setup import key_management


# ═══════════════════════════════════════════════════════
#  Gestor de conexiones WebSocket
# ═══════════════════════════════════════════════════════

class ConnectionManager:
    """Mantiene el conjunto de clientes WebSocket conectados."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket):
        """Acepta y registra una nueva conexión WebSocket."""
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket):
        """Elimina una conexión del conjunto."""
        self.active_connections.discard(websocket)

    async def broadcast(self, message):
        """Envía un mensaje JSON a todos los clientes conectados."""
        disconnected = set()
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except Exception:
                disconnected.add(conn)
        self.active_connections -= disconnected


# Instancia global del gestor
manager = ConnectionManager()

# Estado previo para detectar cuándo termina una impresión
_previous_printing = False
_known_timelapses: set = set()


# ═══════════════════════════════════════════════════════
#  Funciones auxiliares de broadcast
# ═══════════════════════════════════════════════════════

def _build_status(raw):
    """
    Transforma la respuesta cruda de OctoPrint en un diccionario
    limpio con solo los campos que necesita el frontend.
    """
    printer = raw.get("printer", {})
    job = raw.get("job", {})

    return {
        "connected": raw.get("connected", False),
        "state": printer.get("state", {}).get("text", "Desconocido"),
        "temperatures": {
            "bed": printer.get("temperature", {}).get("bed", {}),
            "tool0": printer.get("temperature", {}).get("tool0", {}),
        },
        "job": {
            "file": job.get("job", {}).get("file", {}).get("name", "Sin archivo"),
            "progress": job.get("progress", {}).get("completion", 0),
            "time_elapsed": job.get("progress", {}).get("printTime", 0),
            "time_remaining": job.get("progress", {}).get("printTimeLeft", 0),
        },
        "error": raw.get("error"),
    }


async def broadcast_updates():
    """
    Tarea en segundo plano: cada segundo obtiene el estado
    de OctoPrint y lo envía a todos los clientes WebSocket.
    """
    global _previous_printing, _known_timelapses

    while True:
        if manager.active_connections:
            try:
                # Obtener estado de OctoPrint (síncrono → ejecutar en thread)
                loop = asyncio.get_event_loop()
                raw = await loop.run_in_executor(None, octoprint_client.get_printer_status)
                status = _build_status(raw)

                # Enviar actualización a todos los clientes
                await manager.broadcast({
                    "type": "update",
                    "data": {
                        "status": status,
                        "detections": {"has_errors": False, "total_detections": 0, "classes": {}},
                    },
                })

                # Detectar si la impresión acaba de terminar
                currently_printing = "print" in status["state"].lower()
                print_just_ended = _previous_printing and not currently_printing
                _previous_printing = currently_printing

                # Si terminó, buscar timelapses nuevos
                if print_just_ended:
                    print("[Timelapse] Impresión finalizada, buscando timelapse nuevo...")
                    asyncio.create_task(_check_and_notify_timelapse())

            except Exception as e:
                print(f"Error en broadcast: {e}")

        await asyncio.sleep(1)


async def _check_and_notify_timelapse():
    """
    Espera a que OctoPrint renderice el timelapse y notifica
    a los clientes si hay archivos nuevos.
    """
    global _known_timelapses

    # Esperar un poco para que OctoPrint renderice
    await asyncio.sleep(15)
    loop = asyncio.get_event_loop()

    for attempt in range(5):
        try:
            current_files = await loop.run_in_executor(None, octoprint_client.list_timelapses)
            current_names = {f["name"] for f in current_files}

            # Detectar archivos nuevos
            new_files = [f for f in current_files if f["name"] not in _known_timelapses]
            _known_timelapses = current_names

            if new_files:
                print(f"[Timelapse] {len(new_files)} nuevo(s): {[f['name'] for f in new_files]}")
                await manager.broadcast({"type": "timelapse_ready", "files": new_files})
                return

            print(f"[Timelapse] Intento {attempt + 1}/5: sin timelapse nuevo, esperando...")
            await asyncio.sleep(10)
        except Exception as e:
            print(f"[Timelapse] Error: {e}")
            await asyncio.sleep(10)

    print("[Timelapse] No se encontraron timelapses nuevos tras 5 intentos.")


# ═══════════════════════════════════════════════════════
#  Ciclo de vida de la aplicación
# ═══════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicia la tarea de broadcast al arrancar y la detiene al cerrar."""
    global _known_timelapses

    # Cargar timelapses existentes para no notificarlos como "nuevos"
    try:
        existing = octoprint_client.list_timelapses()
        _known_timelapses = {f["name"] for f in existing}
        print(f"[Timelapse] {len(_known_timelapses)} timelapses existentes al inicio.")
    except Exception as e:
        print(f"[Timelapse] No se pudieron cargar timelapses existentes: {e}")

    # Arrancar tarea de broadcast
    task = asyncio.create_task(broadcast_updates())
    yield
    # Parar tarea al cerrar
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


# ═══════════════════════════════════════════════════════
#  Crear aplicación FastAPI
# ═══════════════════════════════════════════════════════

app = FastAPI(
    title="3D Printer Monitor API",
    description="API para monitorización de impresoras 3D con detección de errores",
    version="2.0.0",
    lifespan=lifespan,
)

# Permitir peticiones desde cualquier origen (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════
#  WebSocket
# ═══════════════════════════════════════════════════════

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket bidireccional:
      - Recibe comandos: {"action": "pause|resume|cancel|start"}
      - Envía actualizaciones de estado automáticamente cada segundo
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            # Ejecutar el comando correspondiente en un thread
            loop = asyncio.get_event_loop()
            command_map = {
                "pause": octoprint_client.pause_print,
                "resume": octoprint_client.resume_print,
                "cancel": octoprint_client.cancel_print,
                "start": octoprint_client.start_print,
            }

            handler = command_map.get(action)
            if handler:
                success = await loop.run_in_executor(None, handler)
                await websocket.send_json({
                    "type": "command_result",
                    "action": action,
                    "success": success,
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ═══════════════════════════════════════════════════════
#  Endpoints REST
# ═══════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Endpoint de bienvenida."""
    return {"message": "3D Printer Monitor API", "status": "running", "websocket": "/ws"}


@app.get("/api/status")
async def get_status():
    """Obtiene el estado actual de la impresora (alternativa REST al WebSocket)."""
    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(None, octoprint_client.get_printer_status)
    return _build_status(raw)


@app.post("/api/upload")
async def upload_gcode(file: UploadFile):
    """Sube un archivo G-code a OctoPrint."""
    if not file.filename.lower().endswith((".gcode", ".gco", ".g")):
        return {"success": False, "error": "El archivo debe ser .gcode, .gco o .g"}

    content = await file.read()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, octoprint_client.upload_gcode, content, file.filename)


@app.get("/api/files")
async def list_files():
    """Lista los archivos G-code disponibles en OctoPrint."""
    loop = asyncio.get_event_loop()
    files = await loop.run_in_executor(None, octoprint_client.list_files)
    return {"files": files}


@app.post("/api/files/select/{filename}")
async def select_file(filename: str):
    """Selecciona un archivo G-code para imprimir."""
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, octoprint_client.select_file, filename)
    return {
        "success": success,
        "message": f"Archivo '{filename}' seleccionado" if success else "Error al seleccionar archivo",
    }


# ═══════════════════════════════════════════════════════
#  Endpoints de Timelapse
# ═══════════════════════════════════════════════════════

@app.get("/api/timelapse")
async def list_timelapses():
    """Lista los timelapses disponibles en OctoPrint."""
    loop = asyncio.get_event_loop()
    timelapses = await loop.run_in_executor(None, octoprint_client.list_timelapses)
    return {"files": timelapses}


@app.get("/api/timelapse/download/{filename}")
async def download_timelapse(filename: str):
    """Descarga un timelapse de OctoPrint."""
    loop = asyncio.get_event_loop()
    content = await loop.run_in_executor(None, octoprint_client.download_timelapse, filename)
    if content is None:
        return {"error": "Timelapse no encontrado"}
    return Response(
        content=content,
        media_type="video/mp4",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.delete("/api/timelapse/{filename}")
async def delete_timelapse(filename: str):
    """Elimina un timelapse de OctoPrint."""
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, octoprint_client.delete_timelapse, filename)
    return {
        "success": success,
        "message": f"Timelapse '{filename}' eliminado" if success else "Error al eliminar timelapse",
    }


# ═══════════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import uvicorn

    if not key_management.validate_configuration():
        print("Configuración no válida. Corrige los errores e intenta de nuevo.")
        sys.exit(1)

    uvicorn.run(app, host="0.0.0.0", port=8000)
