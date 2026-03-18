"""
Cliente para detección de errores usando la API hosted de Roboflow.
Envía las imágenes por HTTP y recibe las predicciones en formato JSON.
"""
import requests

from app.config import ROBOFLOW_API_URL, ROBOFLOW_MODEL_ID, ROBOFLOW_API_KEY, CONFIDENCE_THRESHOLD


class RoboflowClient:
    def __init__(self):
        self.api_url = ROBOFLOW_API_URL
        self.model_id = ROBOFLOW_MODEL_ID
        self.api_key = ROBOFLOW_API_KEY
        self.confidence = CONFIDENCE_THRESHOLD

    def _build_url(self) -> str:
        """Construye la URL del endpoint de detección."""
        return (
            f"{self.api_url}/{self.model_id}"
            f"?api_key={self.api_key}"
            f"&confidence={self.confidence}"
        )

    def detect_errors(self, image_path: str) -> dict:
        """Detecta errores en una imagen leyendo desde el disco."""
        try:
            with open(image_path, "rb") as f:
                img = f.read()
            return self.detect_errors_from_bytes(img)
        except Exception as e:
            return {"error": str(e), "predictions": []}

    def detect_errors_from_bytes(self, image_bytes: bytes) -> dict:
        """Detecta errores enviando los bytes de la imagen a la API de Roboflow."""
        try:
            url = self._build_url()
            response = requests.post(
                url,
                data=image_bytes,
                headers={"Content-Type": "application/octet-stream"},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "predictions": []}


# Instancia global del cliente
roboflow_client = RoboflowClient()
