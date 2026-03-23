"""
Cliente local para detección de errores usando modelo ONNX sin Ultralytics.
Reemplaza a roboflow_client.py — misma interfaz, inferencia local pura y ligera.
"""
import io
import cv2
import numpy as np
import onnxruntime as ort
import ast
from pathlib import Path

from app.config import LOCAL_MODEL_PATH, CONFIDENCE_THRESHOLD


class LocalModelClient:
    def __init__(self):
        self.session = None
        self.confidence = CONFIDENCE_THRESHOLD
        self.input_width = 640
        self.input_height = 640
        self.class_names = {}
        self._load_model()

    def _load_model(self):
        """Carga el modelo ONNX usando onnxruntime nativo."""
        model_path = Path(LOCAL_MODEL_PATH)
        if not model_path.exists():
            print(f"[LocalModel] ADVERTENCIA: No se encontró el modelo en {model_path}")
            print(f"[LocalModel] Copia tu modelo a: {model_path}")
            return

        print(f"[LocalModel] Cargando modelo ONNX desde: {model_path}")
        try:
            self.session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
            
            # Intentar extraer nombres de clases del metadata oculto en el ONNX (compatible ultralytics)
            meta = self.session.get_modelmeta()
            if 'names' in meta.custom_metadata_map:
                self.class_names = ast.literal_eval(meta.custom_metadata_map['names'])
                print(f"[LocalModel] Clases detectadas en el modelo: {self.class_names}")
                
            print(f"[LocalModel] Modelo ONNX cargado correctamente")
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
        Detecta errores usando el modelo local mediante pura matemática (sin torch).
        Devuelve el mismo formato que roboflow_client para compatibilidad:
            {
                "predictions": [
                    {"x": cx, "y": cy, "width": w, "height": h,
                     "class": "Spaghetti", "confidence": 0.85},
                    ...
                ]
            }
        """
        if self.session is None:
            return {"error": "Modelo no cargado", "predictions": []}

        try:
            # 1. Decodificar imagen directamente de los bytes (mucho más rápido que PIL)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            orig_h, orig_w = img.shape[:2]

            # 2. Preprocesado rápido para YOLO (redimensionar, color, normalizar)
            img_resized = cv2.resize(img, (self.input_width, self.input_height))
            img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
            
            input_tensor = img_rgb.astype(np.float32) / 255.0
            input_tensor = input_tensor.transpose(2, 0, 1) # HWC a CHW
            input_tensor = np.expand_dims(input_tensor, axis=0) # Añadir capa batch

            # 3. Inferencia mágica (tarda milisegundos)
            input_name = self.session.get_inputs()[0].name
            outputs = self.session.run(None, {input_name: input_tensor})

            # YOLOv8 entrega un tensor de (1, 4 + num_clases, 8400)
            output = outputs[0][0] # Quitar batch: (4 + num_clases, 8400)
            output = output.transpose() # Transponer a: (8400, 4 + num_clases)

            boxes = []
            scores = []
            class_ids = []

            # 4. Filtrar caja por caja
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

            # 5. Non-Maximum Suppression (borra cajas que se pisan entre sí del mismo objeto)
            indices = cv2.dnn.NMSBoxes(boxes, scores, self.confidence, 0.45)

            predictions = []
            if len(indices) > 0:
                for i in indices.flatten():
                    box = boxes[i]
                    cls_id = class_ids[i]
                    conf = scores[i]
                    
                    # Recuperar el nombre, si no existe poner 'clase_X'
                    cls_name = self.class_names.get(cls_id, self.class_names.get(str(cls_id), f"clase_{cls_id}"))

                    x1, y1, w, h = box
                    cx = x1 + (w / 2)
                    cy = y1 + (h / 2)

                    predictions.append({
                        "x": cx,
                        "y": cy,
                        "width": w,
                        "height": h,
                        "class": cls_name,
                        "confidence": conf
                    })

            return {"predictions": predictions}

        except Exception as e:
            return {"error": str(e), "predictions": []}


# Instancia global del cliente
local_model_client = LocalModelClient()
