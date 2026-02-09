"""
Cliente para comunicación con Roboflow API
"""
from inference_sdk import InferenceHTTPClient
from .config import ROBOFLOW_API_URL, ROBOFLOW_API_KEY, ROBOFLOW_MODEL_ID


class RoboflowClient:
    def __init__(self):
        self.client = InferenceHTTPClient(
            api_url=ROBOFLOW_API_URL,
            api_key=ROBOFLOW_API_KEY
        )
        self.model_id = ROBOFLOW_MODEL_ID
    
    def detect_errors(self, image_path: str) -> dict:
        """
        Detecta errores en una imagen de impresión 3D
        
        Args:
            image_path: Ruta a la imagen o bytes de la imagen
            
        Returns:
            dict con las predicciones del modelo
        """
        try:
            result = self.client.infer(image_path, model_id=self.model_id)
            return result
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
        import tempfile
        import os
        
        try:
            # Guardar temporalmente la imagen
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            
            # Realizar inferencia
            result = self.client.infer(tmp_path, model_id=self.model_id)
            
            # Limpiar archivo temporal
            os.unlink(tmp_path)
            
            return result
        except Exception as e:
            return {
                "error": str(e),
                "predictions": []
            }


# Instancia global del cliente
roboflow_client = RoboflowClient()
