"""
Cliente para detección de errores usando el modelo local descargado
con la librería `inference`. Los pesos se obtienen automáticamente la
primera vez que se instancia el modelo; quedan en caché para no
volver a descargarlos en ejecuciones posteriores.
"""
from inference import get_model

from app.config import ROBOFLOW_MODEL_ID, ROBOFLOW_API_KEY


class RoboflowClient:
    def __init__(self):
        self.model = None
        self.model_id = ROBOFLOW_MODEL_ID
        self.api_key = ROBOFLOW_API_KEY

    def _load_model(self):
        """Devuelve el modelo local, descargándolo si es la primera vez."""
        if self.model is None:
            # la función get_model se encarga de cachear pesos automáticamente
            self.model = get_model(model_id=self.model_id, api_key=self.api_key)
        return self.model

    def detect_errors(self, image_path: str) -> dict:
        """Detecta errores en una imagen leyendo desde el disco."""
        try:
            with open(image_path, "rb") as f:
                img = f.read()
            return self.detect_errors_from_bytes(img)
        except Exception as e:
            return {"error": str(e), "predictions": []}

    def detect_errors_from_bytes(self, image_bytes: bytes) -> dict:
        """Detecta errores a partir de bytes usando el modelo cargado."""
        try:
            model = self._load_model()
            result = model.infer(image_bytes)
            return result
        except Exception as e:
            return {"error": str(e), "predictions": []}


# Instancia global del cliente
roboflow_client = RoboflowClient()
