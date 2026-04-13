"""
Configuración del sistema.

Carga las variables de entorno desde el archivo .env.back.template
y las expone como constantes para el resto de la aplicación.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo de plantilla
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.back.template"))

# Dirección base de OctoPrint (ej: http://192.168.1.49)
OCTOPRINT_URL = os.getenv("OCTOPRINT_URL", "http://localhost")

# Clave API de OctoPrint (se obtiene en Settings > API)
OCTOPRINT_API_KEY = os.getenv("OCTOPRINT_API_KEY", "")

# URL directa para capturar una imagen de la cámara
WEBCAM_SNAPSHOT_URL = os.getenv("WEBCAM_SNAPSHOT_URL", "http://192.168.1.49/webcam/?action=snapshot")
