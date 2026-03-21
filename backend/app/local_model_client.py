"""
Cliente local para detección de errores usando YOLOv8 entrenado localmente.
Reemplaza a roboflow_client.py — misma interfaz, inferencia local.
"""
import io
from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from app.config import LOCAL_MODEL_PATH, CONFIDENCE_THRESHOLD


class LocalModelClient:
    def __init__(self):
        self.model = None
        self.confidence = CONFIDENCE_THRESHOLD
        self._load_model()

    def _load_model(self):
        """Carga el modelo YOLOv8 entrenado."""
        model_path = Path(LOCAL_MODEL_PATH)
        if not model_path.exists():
            print(f"[LocalModel] ADVERTENCIA: No se encontró el modelo en {model_path}")
            print(f"[LocalModel] Copia best.pt (o best.onnx) a: {model_path}")
            return

        print(f"[LocalModel] Cargando modelo desde: {model_path}")
        self.model = YOLO(str(model_path))
        print(f"[LocalModel] Modelo cargado correctamente")

    def detect_errors(self, image_path: str) -> dict:
        """Detecta errores en una imagen leyendo desde el disco."""
        try:
            with open(image_path, "rb") as f:
                img = f.read()
            return self.detect_errors_from_bytes(img)
        except Exception as e:
            return {"error": str(e), "predictions": []}

    def detect_errors_from_bytes(self, image_bytes: bytes) -> dict:
        """
        Detecta errores usando el modelo local.
        Devuelve el mismo formato que roboflow_client para compatibilidad
        con image_processor.py:
            {
                "predictions": [
                    {"x": cx, "y": cy, "width": w, "height": h,
                     "class": "FriedNoodles", "confidence": 0.85},
                    ...
                ]
            }
        """
        if self.model is None:
            return {"error": "Modelo no cargado", "predictions": []}

        try:
            # Convertir bytes a imagen PIL
            image = Image.open(io.BytesIO(image_bytes))

            # Ejecutar inferencia
            results = self.model.predict(
                source=image,
                conf=self.confidence,
                verbose=False,
            )

            # Convertir resultados al formato Roboflow (compatible con image_processor)
            predictions = []
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = result.names[cls_id]

                    # Convertir de xyxy a centro + dimensiones (formato Roboflow)
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    w = x2 - x1
                    h = y2 - y1

                    predictions.append({
                        "x": cx,
                        "y": cy,
                        "width": w,
                        "height": h,
                        "class": cls_name,
                        "confidence": conf,
                    })

            return {"predictions": predictions}

        except Exception as e:
            return {"error": str(e), "predictions": []}


# Instancia global del cliente (misma convención que roboflow_client.py)
local_model_client = LocalModelClient()
