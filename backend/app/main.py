"""
API Principal - FastAPI
Sistema de Monitorización de Impresoras 3D
"""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .octoprint_client import octoprint_client
from .roboflow_client import roboflow_client
from .image_processor import draw_detections, get_detection_summary
from .config import load_settings, save_settings

app = FastAPI(
    title="3D Printer Monitor API",
    description="API para monitorización de impresoras 3D con detección de errores",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el frontend Vue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar el origen exacto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SettingsModel(BaseModel):
    octoprint_url: str
    octoprint_api_key: str
    roboflow_api_key: str | None = None
    confidence_threshold: float | None = None


@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {"message": "3D Printer Monitor API", "status": "running"}


@app.get("/api/settings")
async def get_settings():
    """Obtiene la configuración actual"""
    settings = load_settings()
    # Ocultar parte de la API key por seguridad
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
    
    # Actualizar solo los campos proporcionados
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
    """
    Obtiene el estado actual de la impresora
    
    Returns:
        Estado de la impresora, trabajo actual y detecciones
    """
    status = await octoprint_client.get_printer_status()
    
    # Extraer información relevante
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


@app.get("/api/snapshot")
async def get_snapshot():
    """
    Obtiene la imagen de la cámara con detecciones de errores
    
    Returns:
        Imagen JPEG con bounding boxes dibujados
    """
    # Obtener imagen de OctoPrint
    image_bytes = await octoprint_client.get_snapshot()
    
    if not image_bytes:
        return Response(
            content=b"",
            status_code=503,
            media_type="text/plain"
        )
    
    # Detectar errores con Roboflow
    predictions_result = roboflow_client.detect_errors_from_bytes(image_bytes)
    predictions = predictions_result.get("predictions", [])
    
    # Dibujar detecciones sobre la imagen
    processed_image = draw_detections(image_bytes, predictions)
    
    return Response(
        content=processed_image,
        media_type="image/jpeg"
    )


@app.get("/api/detections")
async def get_detections():
    """
    Obtiene solo la información de detecciones (sin imagen)
    
    Returns:
        Resumen de errores detectados
    """
    image_bytes = await octoprint_client.get_snapshot()
    
    if not image_bytes:
        return {
            "error": "No se pudo obtener imagen",
            "has_errors": False,
            "total_detections": 0
        }
    
    predictions_result = roboflow_client.detect_errors_from_bytes(image_bytes)
    predictions = predictions_result.get("predictions", [])
    
    return get_detection_summary(predictions)


@app.post("/api/pause")
async def pause_print():
    """Pausa la impresión actual"""
    success = await octoprint_client.pause_print()
    return {
        "success": success,
        "message": "Impresión pausada" if success else "Error al pausar"
    }


@app.post("/api/resume")
async def resume_print():
    """Reanuda la impresión pausada"""
    success = await octoprint_client.resume_print()
    return {
        "success": success,
        "message": "Impresión reanudada" if success else "Error al reanudar"
    }
