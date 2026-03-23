"""
Cliente local para detección de errores usando modelo ONNX sin Ultralytics ni ONNXRuntime.
Utiliza únicamente OpenCV DNN, la librería más compatible y rápida para Raspberry Pi.
"""
import io
import cv2
import numpy as np
from pathlib import Path

from app.config import LOCAL_MODEL_PATH, CONFIDENCE_THRESHOLD


class LocalModelClient:
    def __init__(self):
        self.net = None
        self.confidence = CONFIDENCE_THRESHOLD
        self.input_width = 640
        self.input_height = 640
        self._load_model()

    def _load_model(self):
        """Carga el modelo ONNX usando OpenCV DNN."""
        model_path = Path(LOCAL_MODEL_PATH)
        if not model_path.exists():
            print(f"[LocalModel] ADVERTENCIA: No se encontró el modelo en {model_path}")
            print(f"[LocalModel] Copia tu modelo a: {model_path}")
            return

        print(f"[LocalModel] Cargando modelo ONNX desde: {model_path}")
        try:
            self.net = cv2.dnn.readNetFromONNX(str(model_path))
            print(f"[LocalModel] Modelo ONNX cargado correctamente vía OpenCV")
        except Exception as e:
            print(f"[LocalModel] Error crítico cargando el modelo: {e}")

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
        Detecta errores usando el modelo local mediante OpenCV.
        Devuelve el formato compatible para el frontend:
            {
                "predictions": [
                    {"x": cx, "y": cy, "width": w, "height": h,
                     "class": "Error_0", "confidence": 0.85},
                    ...
                ]
            }
        """
        if self.net is None:
            return {"error": "Modelo no cargado", "predictions": []}

        try:
            # 1. Decodificar la imagen de bytes
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            orig_h, orig_w = img.shape[:2]

            # 2. Generar el Blob para OpenCV (incluye resize a 640x640 y escalado 1/255)
            # YOLOv8 espera RGB, por lo que ponemos swapRB=True para cambiar BGR a RGB automáticamente
            blob = cv2.dnn.blobFromImage(img, 1/255.0, (self.input_width, self.input_height), swapRB=True, crop=False)
            
            # 3. Lanzar inferencia
            self.net.setInput(blob)
            outputs = self.net.forward()

            # YOLOv8 entrega un tensor de (1, 4 + num_clases, 8400)
            output = outputs[0] # Quitar batch: (4 + num_clases, 8400)
            output = output.transpose() # Transponer a: (8400, 4 + num_clases)

            boxes = []
            scores = []
            class_ids = []

            # 4. Procesar detecciones
            for row in output:
                prob = row[4:]
                max_prob = np.max(prob)
                
                if max_prob > self.confidence:
                    class_id = np.argmax(prob)
                    xc, yc, w, h = row[:4]

                    # Mapear de vuelta al tamaño original de la foto
                    xc = (xc / self.input_width) * orig_w
                    yc = (yc / self.input_height) * orig_h
                    w = (w / self.input_width) * orig_w
                    h = (h / self.input_height) * orig_h
                    
                    x1 = xc - (w / 2)
                    y1 = yc - (h / 2)

                    boxes.append([int(x1), int(y1), int(w), int(h)])
                    scores.append(float(max_prob))
                    class_ids.append(int(class_id))

            # 5. Non-Maximum Suppression (borra duplicados)
            indices = cv2.dnn.NMSBoxes(boxes, scores, self.confidence, 0.45)

            predictions = []
            if len(indices) > 0:
                for i in indices.flatten():
                    box = boxes[i]
                    cls_id = class_ids[i]
                    conf = scores[i]
                    
                    x1, y1, w, h = box
                    cx = x1 + (w / 2)
                    cy = y1 + (h / 2)

                    predictions.append({
                        "x": cx,
                        "y": cy,
                        "width": w,
                        "height": h,
                        "class": f"Error_{cls_id}",
                        "confidence": conf
                    })

            return {"predictions": predictions}

        except Exception as e:
            return {"error": str(e), "predictions": []}


# Instancia global del cliente
local_model_client = LocalModelClient()
