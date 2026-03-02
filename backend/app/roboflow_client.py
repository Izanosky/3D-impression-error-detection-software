"""
Cliente para detección de errores con servidor de inferencia Roboflow local
El servidor corre en localhost:9001 via Docker
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
        """Construye la URL del endpoint de inferencia local"""
        return f"{self.api_url}/infer/object_detection"
    
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
        Detecta errores desde bytes de imagen usando el servidor local
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            dict con las predicciones del modelo
        """
        try:
            # Codificar imagen en base64
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Llamada al servidor de inferencia local
            response = requests.post(
                self._build_url(),
                params={
                    "api_key": self.api_key,
                    "model_id": self.model_id
                },
                data=image_b64,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Inference server error: {response.status_code} - {response.text[:200]}",
                    "predictions": []
                }
        except requests.ConnectionError:
            return {
                "error": "Servidor de inferencia no disponible. Ejecuta: inference server start",
                "predictions": []
            }
        except Exception as e:
            return {
                "error": str(e),
                "predictions": []
            }


# Instancia global del cliente
roboflow_client = RoboflowClient()
