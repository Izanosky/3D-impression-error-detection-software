# Configuración del sistema
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env.back.template
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.back.template"))

# OctoPrint
OCTOPRINT_URL = os.getenv("OCTOPRINT_URL", "http://localhost")
OCTOPRINT_API_KEY = os.getenv("OCTOPRINT_API_KEY", "")
WEBCAM_SNAPSHOT_URL = os.getenv("WEBCAM_SNAPSHOT_URL", "http://192.168.1.49/webcam/?action=snapshot")

# Modelo local YOLOv8 (reemplaza Roboflow)
# Ruta al modelo entrenado — puede ser .pt o .onnx
LOCAL_MODEL_PATH = os.getenv(
    "MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "model", "best.onnx")
)

# Detección
CONFIDENCE_THRESHOLD = 0.4
