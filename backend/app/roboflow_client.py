"""
Cliente para comunicación con Roboflow API
Usa llamadas HTTP directas para evitar dependencias pesadas (inference-sdk)
"""
import base64
import requests
from app.config import ROBOFLOW_API_URL, ROBOFLOW_MODEL_ID, ROBOFLOW_API_KEY


class RoboflowClient:
    def __init__(self):
        self.api_url = ROBOFLOW_API_URL
        self.api_key = ROBOFLOW_API_KEY
        self.model_id = ROBOFLOW_MODEL_ID
    
    def _build_url(self) -> str:
        """Construye la URL del endpoint de inferencia"""
        return f"{self.api_url}/{self.model_id}"
    
    def detect_errors(self, image_path: str) -> dict:
        """
        Detecta errores en una imagen de impresión 3D
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            dict con las predicciones del modelo
        """
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            return self.detect_errors_from_bytes(image_bytes)
        except Exception as e:
            return {
                "error": str(e),
                "predictions": []
            }
    
    def detect_errors_from_bytes(self, image_bytes: bytes) -> dict:
        """
        Detecta errores desde bytes de imagen
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            dict con las predicciones del modelo
        """
        try:
            # Codificar imagen en base64
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Llamada HTTP directa a la API de Roboflow
            response = requests.post(
                self._build_url(),
                params={"api_key": self.api_key},
                data=image_b64,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Roboflow API error: {response.status_code} - {response.text[:200]}",
                    "predictions": []
                }
        except Exception as e:
            return {
                "error": str(e),
                "predictions": []
            }


# Instancia global del cliente
roboflow_client = RoboflowClient()
