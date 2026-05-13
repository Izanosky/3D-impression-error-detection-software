import asyncio
from typing import Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.octoprint_client import octoprint_client
from app.setup import key_management

# Clase por convenio, es una clase que se utiliza para gestionar los clientes WebSocket conectados
class ConnectionManager:

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


# Metodo auxiliar para transformar la respuesta de OctoPrint en un diccionario limpio para el frontend
def _build_status(raw):
    # Extraemos de forma segura los subdiccionarios principales usando .get() para evitar KeyError si no existen
    printer = raw.get("printer", {})
    job = raw.get("job", {})

    return {
        # Estado de conexión general con la impresora física
        "connected": raw.get("connected", False),
        
        # Estado textual de la impresora (ej: "Operational", "Printing", "Paused")
        "state": printer.get("state", {}).get("text", "Desconocido"),
        
        # Lecturas de temperatura actuales y objetivo
        "temperatures": {
            "bed": printer.get("temperature", {}).get("bed", {}),       # Cama caliente (actual y target)
            "tool0": printer.get("temperature", {}).get("tool0", {}),   # Extrusor principal (actual y target)
        },
        
        # Información sobre la impresión en curso
        "job": {
            # Nombre del archivo que se está imprimiendo
            "file": job.get("job", {}).get("file", {}).get("name", "Sin archivo"),
            # Porcentaje completado (0 a 100)
            "progress": job.get("progress", {}).get("completion", 0),
            # Segundos que lleva imprimiendo
            "time_elapsed": job.get("progress", {}).get("printTime", 0),
            # Segundos estimados que faltan para terminar
            "time_remaining": job.get("progress", {}).get("printTimeLeft", 0),
        },
        
        # Mensaje de error si ha ocurrido algún problema crítico
        "error": raw.get("error"),
    }


# Tarea en segundo plano: cada segundo obtiene el estado y lo envía por WebSocket
async def broadcast_updates():
    global _previous_printing

    # Bucle infinito que se ejecuta en segundo plano durante toda la vida de la aplicación
    while True:
        # Solo consultamos a OctoPrint si hay al menos un cliente (frontend) conectado al WebSocket
        if manager.active_connections:
            try:
                # Obtenemos el bucle de eventos asíncrono actual de FastAPI
                loop = asyncio.get_event_loop()
                
                # CRÍTICO: get_printer_status de requests es una función SÍNCRONA (bloqueante).
                # Si la llamáramos directamente, congelaría todo FastAPI mientras espera la respuesta.
                # run_in_executor(None, ...) la ejecuta en un hilo secundario (Threadpool) para no bloquear el servidor.
                raw = await loop.run_in_executor(None, octoprint_client.get_printer_status)
                
                # Limpiamos y formateamos los datos
                status = _build_status(raw)

                # Enviamos el estado formateado a todos los clientes web conectados
                await manager.broadcast({
                    "type": "update",
                    "data": {
                        "status": status,
                        # Aquí se integrarán las detecciones de errores de visión artificial en el futuro
                        "detections": {"has_errors": False, "total_detections": 0, "classes": {}},
                    },
                })

                # Lógica para detectar si la impresión acaba de terminar
                # Comprueba si la palabra "print" está en el estado actual (ej: "Printing")
                currently_printing = "print" in status["state"].lower()
                # Actualizamos la variable global para la siguiente iteración del bucle
                _previous_printing = currently_printing

            except Exception as e:
                # Capturamos cualquier error (caída de red, timeout) para que el bucle infinito no se rompa y muera
                print(f"Error en broadcast: {e}")

        # Esperamos 1 segundo de forma asíncrona antes de volver a consultar
        # Esto permite que FastAPI atienda otras peticiones REST o de WebSockets mientras tanto
        await asyncio.sleep(1)


# ==============================================================================
# GESTIÓN DEL CICLO DE VIDA DE LA APLICACIÓN (LIFESPAN)
# ==============================================================================
# El gestor de contexto 'lifespan' permite definir código que se ejecuta al arrancar
# y al apagar el servidor FastAPI, reemplazando a los antiguos eventos @app.on_event.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- FASE DE INICIO ---
    # Lanzamos la tarea infinita de broadcast en segundo plano de forma concurrente
    task = asyncio.create_task(broadcast_updates())
    
    # 'yield' marca el punto donde FastAPI arranca y empieza a recibir peticiones de usuarios
    yield
    
    # --- FASE DE APAGADO ---
    # Cuando el servidor se detiene (ej: Ctrl+C), cancelamos la tarea de fondo limpiamente
    task.cancel()
    try:
        # Esperamos a que la tarea termine de cerrarse
        await task
    except asyncio.CancelledError:
        # Ignoramos el error de cancelación, ya que es el comportamiento esperado
        pass


###########################################
# INICIALIZACIÓN DE LA APLICACIÓN FASTAPI #
###########################################
app = FastAPI(
    title="3D Printer Monitor API",
    description="API para monitorización de impresoras 3D con detección de errores",
    version="2.0.0",
    lifespan=lifespan, # Registramos nuestro gestor del ciclo de vida definido arriba
)

# Configuración del Middleware CORS (Cross-Origin Resource Sharing)
# Es imprescindible para que un frontend (ej: Vue, React) alojado en otro puerto/dominio
# pueda hacer peticiones HTTP/WebSocket a este backend sin ser bloqueado por el navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Permite peticiones desde cualquier origen (en producción se suele limitar)
    allow_credentials=True,  # Permite envío de cookies y cabeceras de autorización
    allow_methods=["*"],     # Permite todos los verbos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],     # Permite todo tipo de cabeceras personalizadas
)


##########################################
# ENDPOINT DE WEBSOCKET (COMUNICACIÓN    #
# BIDIRECCIONAL EN TIEMPO REAL)          #
##########################################
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Aceptamos la conexión entrante y la registramos en nuestro ConnectionManager
    await manager.connect(websocket)
    try:
        # Bucle infinito para escuchar los comandos que envía el frontend por este socket
        while True:
            # Esperamos de forma asíncrona a recibir un mensaje JSON del cliente
            data = await websocket.receive_json()
            # Extraemos la acción solicitada (ej: {"action": "pause"})
            action = data.get("action")

            loop = asyncio.get_event_loop()
            
            # Mapeamos los strings de acción a sus funciones reales en el cliente de OctoPrint
            command_map = {
                "pause": octoprint_client.pause_print,
                "resume": octoprint_client.resume_print,
                "cancel": octoprint_client.cancel_print,
                "start": octoprint_client.start_print,
            }

            # Obtenemos la función correspondiente
            handler = command_map.get(action)
            if handler:
                # Al igual que antes, las funciones de control de OctoPrint son SÍNCRONAS.
                # Las ejecutamos con run_in_executor para no bloquear el Event Loop principal.
                success = await loop.run_in_executor(None, handler)
                
                # Respondemos al cliente confirmando si el comando se ejecutó con éxito
                await websocket.send_json({
                    "type": "command_result",
                    "action": action,
                    "success": success,
                })
    except WebSocketDisconnect:
        # Si el cliente cierra la pestaña del navegador o pierde conexión,
        # salta esta excepción y lo eliminamos de la lista de conexiones activas.
        manager.disconnect(websocket)


################################################
# DEFINICIÓN DE LOS ENDPOINTS DE NUESTRA API ###
################################################
@app.get("/")
async def root():
    return {"message": "3D Printer Monitor API", "status": "running", "websocket": "/ws"}

# Endpoint que nos proporciona el estado actual de la impresora
@app.get("/api/status")
async def get_status():
    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(None, octoprint_client.get_printer_status)
    return _build_status(raw)

# Endpoint para subir archivos gcode a OctoPrint
@app.post("/api/upload")
async def upload_gcode(file: UploadFile):
    if not file.filename.lower().endswith((".gcode", ".gco", ".g")):
        return {"success": False, "error": "El archivo debe ser .gcode, .gco o .g"}

    content = await file.read()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, octoprint_client.upload_gcode, content, file.filename)

# Endpoint que nos proporciona la lista de archivos gcode que hay subidos en OctoPrint
@app.get("/api/files")
async def list_files():
    loop = asyncio.get_event_loop()
    files = await loop.run_in_executor(None, octoprint_client.list_files)
    return {"files": files}

# Endpoint que selecciona un archivo para imprimir
@app.post("/api/files/select/{filename}")
async def select_file(filename: str):
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, octoprint_client.select_file, filename)
    return {
        "success": success,
        "message": f"Archivo '{filename}' seleccionado" if success else "Error al seleccionar archivo",
    }

# ============================================
# Ejecución de la aplicación
# ============================================
if __name__ == "__main__":
    import sys
    import uvicorn

    if not key_management.validate_configuration():
        print("Configuración no válida. Corrige los errores e intenta de nuevo.")
        sys.exit(1)

    uvicorn.run(app, host="0.0.0.0", port=8000) # Definimos aqui el run de uvicorn para no tener que ejecutarlo desde la terminal
