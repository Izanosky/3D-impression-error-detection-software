# Configuración del sistema
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env.back.template
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.back.template"))

# OctoPrint
OCTOPRINT_URL = os.getenv("OCTOPRINT_URL", "http://localhost")
OCTOPRINT_API_KEY = os.getenv("OCTOPRINT_API_KEY", "")

# Roboflow (API hosted)
ROBOFLOW_API_URL = "https://detect.roboflow.com"
ROBOFLOW_MODEL_ID = "3d-printer-error-detection/5"
ROBOFLOW_API_KEY = "PZCqeY4aWL1dSF0Npry5"

# Detección
CONFIDENCE_THRESHOLD = 0.5
