# Configuración del sistema
import os
import json
from pathlib import Path

# Ruta del archivo de configuración persistente
CONFIG_FILE = Path(__file__).parent.parent / "settings.json"

# Valores por defecto
DEFAULT_SETTINGS = {
    "octoprint_url": "http://localhost:5000",
    "octoprint_api_key": "",
    "roboflow_api_key": "PZCqeY4aWL1dSF0Npry5",
    "confidence_threshold": 0.5
}


def load_settings() -> dict:
    """Carga la configuración desde el archivo JSON"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                # Combinar con defaults para incluir nuevas opciones
                return {**DEFAULT_SETTINGS, **saved}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> bool:
    """Guarda la configuración en el archivo JSON"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def get_setting(key: str):
    """Obtiene un valor de configuración"""
    settings = load_settings()
    return settings.get(key, DEFAULT_SETTINGS.get(key))


# Roboflow (fijos)
ROBOFLOW_API_URL = "https://serverless.roboflow.com"
ROBOFLOW_MODEL_ID = "3d-printer-error-detection/5"

# Propiedades dinámicas (se leen del archivo)
@property
def OCTOPRINT_URL():
    return get_setting("octoprint_url")

@property
def OCTOPRINT_API_KEY():
    return get_setting("octoprint_api_key")

@property
def ROBOFLOW_API_KEY():
    return get_setting("roboflow_api_key")

@property
def CONFIDENCE_THRESHOLD():
    return get_setting("confidence_threshold")
