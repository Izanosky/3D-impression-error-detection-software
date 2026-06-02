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

# Estado previo para detectar cuando termina una impresion
_previous_printing = False


# Metodo auxiliar para transformar la respuesta de OctoPrint en un diccionario limpio para el frontend
def _build_status(raw):
    printer = raw.get("printer", {})
    job = raw.get("job", {})

    return {
        # Estado de conexion general con la impresora fisica
        "connected": raw.get("connected", False),
        
        # Estado textual de la impresora (ej: "Operational", "Printing", "Paused")
        "state": printer.get("state", {}).get("text", "Desconocido"),
        
        # Lecturas de temperatura actuales y objetivo
        "temperatures": {
            "bed": printer.get("temperature", {}).get("bed", {}),       # Cama caliente (actual y target)
            "tool0": printer.get("temperature", {}).get("tool0", {}),   # Extrusor principal (actual y target)
        },
        
        # Informacion sobre la impresion en curso
        "job": {
            # Nombre del archivo que se esta imprimiendo
            "file": job.get("job", {}).get("file", {}).get("name", "Sin archivo"),
            # Porcentaje completado (0 a 100)
            "progress": job.get("progress", {}).get("completion", 0),
            # Segundos que lleva imprimiendo
            "time_elapsed": job.get("progress", {}).get("printTime", 0),
            # Segundos estimados que faltan para terminar
            "time_remaining": job.get("progress", {}).get("printTimeLeft", 0),
        },
        
        # Mensaje de error si ha ocurrido algún problema critico
        "error": raw.get("error"),
    }


# Tarea en segundo plano: cada segundo obtiene el estado y lo envia por WebSocket
async def broadcast_updates():
    global _previous_printing

    # Bucle infinito que se ejecuta en segundo plano durante toda la vida de la aplicacion
    while True:
        # Solo consultamos a OctoPrint si hay al menos un cliente (frontend) conectado al WebSocket
        if manager.active_connections:
            try:
                # Obtenemos el bucle de eventos asincrono actual de FastAPI
                loop = asyncio.get_event_loop()
                
                raw = await loop.run_in_executor(None, octoprint_client.obtener_estado_impresora)
                
                # Limpiamos y formateamos los datos
                status = _build_status(raw)

                # Enviamos el estado formateado a todos los clientes web conectados
                await manager.broadcast({
                    "type": "update",
                    "data": {
                        "status": status,
                        "detections": {"has_errors": False, "total_detections": 0, "classes": {}},
                    },
                })

                # Logica para detectar si la impresion acaba de terminar
                # Comprueba si la palabra "print" esta en el estado actual (ej: "Printing")
                currently_printing = "print" in status["state"].lower()
                # Actualizamos la variable global para la siguiente iteracion del bucle
                _previous_printing = currently_printing

            except Exception as e:
                # Capturamos cualquier error (caida de red, timeout) para que el bucle infinito no se rompa y muera
                print(f"Error en broadcast: {e}")

        # Esperamos 1 segundo de forma asincrona antes de volver a consultar
        # Esto permite que FastAPI atienda otras peticiones REST o de WebSockets mientras tanto
        await asyncio.sleep(1)


# ==============================================================================
# GESTIoN DEL CICLO DE VIDA DE LA APLICACIoN (LIFESPAN)
# ==============================================================================
# Basicamente, hace que se ejecute constantemente el bucle de broadcast
# y cuando acaba cierra las conexiones limpiamente
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
        # Ignoramos el error de cancelacion, ya que es el comportamiento esperado
        pass


###########################################
# INICIALIZACIoN DE LA APLICACIoN FASTAPI #
###########################################
app = FastAPI(
    title="3D Printer Monitor API",
    description="API para monitorizacion de impresoras 3D con deteccion de errores",
    version="2.0.0",
    lifespan=lifespan, # Registramos nuestro gestor del ciclo de vida definido arriba
)

# Configuracion del Middleware CORS (Cross-Origin Resource Sharing)
# necesario para que un frontend pueda hacer peticiones HTTP/WebSocket a este backend sin ser bloqueado por el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Permite peticiones desde cualquier origen
    allow_credentials=True,  # Permite envio de cookies y cabeceras de autorizacion
    allow_methods=["*"],     # Permite todos los comandos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],     # Permite todo tipo de cabeceras personalizadas
)


##########################################
# ENDPOINT DE WEBSOCKET                  #
##########################################
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Aceptamos la conexion entrante y la registramos en nuestro ConnectionManager
    await manager.connect(websocket)
    try:
        # Bucle infinito para escuchar los comandos que envia el frontend por este socket
        while True:

            data = await websocket.receive_json()
            # Extraemos la accion solicitada por el usuario
            action = data.get("action")

            loop = asyncio.get_event_loop()
            
            # Obtenemos la accion que vamos a realizar en funcion del comando
            command_map = {
                "pausar": octoprint_client.pausar_impresion,
                "reanudar": octoprint_client.reanudar_impresion,
                "cancelar": octoprint_client.cancelar_impresion,
                "iniciar": octoprint_client.iniciar_impresion,
            }

            # Obtenemos la funcion correspondiente
            handler = command_map.get(action)
            if handler:
                # las ejecutamos con run_in_executor para no bloquear el Event Loop principal
                success = await loop.run_in_executor(None, handler)
                
                # Respondemos al cliente confirmando si el comando se ejecuto con exito
                await websocket.send_json({
                    "type": "command_result",
                    "action": action,
                    "success": success,
                })
    except WebSocketDisconnect:
        # Si el cliente cierra la pestaña del navegador o pierde conexion
        # salta esta excepcion y lo eliminamos de la lista de conexiones activas
        manager.disconnect(websocket)


################################################
# DEFINICIoN DE LOS ENDPOINTS DE NUESTRA API ###
################################################
@app.get("/")
async def root():
    return {"message": "3D Printer Monitor API", "status": "running", "websocket": "/ws"}

# Endpoint para subir archivos gcode a OctoPrint
@app.post("/api/subir")
async def subir_gcode(file: UploadFile):
    if not file.filename.lower().endswith((".gcode", ".gco", ".g")):
        return {"success": False, "error": "El archivo debe ser .gcode, .gco o .g"}

    content = await file.read()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, octoprint_client.subir_gcode, content, file.filename)

# Endpoint que nos proporciona la lista de archivos gcode que hay subidos en OctoPrint
@app.get("/api/archivos")
async def listar_archivos():
    loop = asyncio.get_event_loop()
    files = await loop.run_in_executor(None, octoprint_client.listar_archivos)
    return {"files": files}

# Endpoint que selecciona un archivo para imprimir
@app.post("/api/archivos/seleccionar/{filename}")
async def seleccionar_archivo(filename: str):
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, octoprint_client.seleccionar_archivo, filename)
    return {
        "success": success,
        "message": f"Archivo '{filename}' seleccionado" if success else "Error al seleccionar archivo",
    }

# ############################################
# Ejecucion de la aplicacion                 #
# ############################################
if __name__ == "__main__":
    import sys
    import uvicorn

    try:
        if not key_management.validar_configuracion():
            print("Configuracion no valida. Corrige los errores e intenta de nuevo.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nConfiguracion cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"Error al validar la configuracion: {e}")
        sys.exit(1)


    uvicorn.run(app, host="0.0.0.0", port=8000) # Definimos aqui el run de uvicorn para no tener que ejecutarlo desde la terminal
