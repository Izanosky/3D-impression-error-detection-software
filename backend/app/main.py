import asyncio
from typing import Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect, Response
from fastapi.middleware.cors import CORSMiddleware

from app.octoprint_client import octoprint_client
from app.setup import key_management


class ConnectionManager:
    """Mantiene el conjunto de clientes WebSocket conectados."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message):
        disconnected = set()
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except Exception:
                disconnected.add(conn)
        self.active_connections -= disconnected


manager = ConnectionManager()

# Estado previo para detectar cuándo termina una impresión
_previous_printing = False


def _build_status(raw):
    """Transforma la respuesta de OctoPrint en un dict limpio para el frontend."""
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
    """Tarea en segundo plano: cada segundo obtiene el estado y lo envía por WebSocket."""
    global _previous_printing

    while True:
        if manager.active_connections:
            try:
                loop = asyncio.get_event_loop()
                raw = await loop.run_in_executor(None, octoprint_client.get_printer_status)
                status = _build_status(raw)

                await manager.broadcast({
                    "type": "update",
                    "data": {
                        "status": status,
                        "detections": {"has_errors": False, "total_detections": 0, "classes": {}},
                    },
                })

                # Detectar si la impresión acaba de terminar
                currently_printing = "print" in status["state"].lower()
                _previous_printing = currently_printing

            except Exception as e:
                print(f"Error en broadcast: {e}")

        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(broadcast_updates())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="3D Printer Monitor API",
    description="API para monitorización de impresoras 3D con detección de errores",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

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


# Endpoints REST
@app.get("/")
async def root():
    return {"message": "3D Printer Monitor API", "status": "running", "websocket": "/ws"}


@app.get("/api/status")
async def get_status():
    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(None, octoprint_client.get_printer_status)
    return _build_status(raw)


@app.post("/api/upload")
async def upload_gcode(file: UploadFile):
    if not file.filename.lower().endswith((".gcode", ".gco", ".g")):
        return {"success": False, "error": "El archivo debe ser .gcode, .gco o .g"}

    content = await file.read()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, octoprint_client.upload_gcode, content, file.filename)


@app.get("/api/files")
async def list_files():
    loop = asyncio.get_event_loop()
    files = await loop.run_in_executor(None, octoprint_client.list_files)
    return {"files": files}


@app.post("/api/files/select/{filename}")
async def select_file(filename: str):
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, octoprint_client.select_file, filename)
    return {
        "success": success,
        "message": f"Archivo '{filename}' seleccionado" if success else "Error al seleccionar archivo",
    }


if __name__ == "__main__":
    import sys
    import uvicorn

    if not key_management.validate_configuration():
        print("Configuración no válida. Corrige los errores e intenta de nuevo.")
        sys.exit(1)

    uvicorn.run(app, host="0.0.0.0", port=8000)
