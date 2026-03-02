from inference_sdk import InferenceHTTPClient
import torch
import torchvision
from torchvision.io import read_image
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image
import os
import sys
import time

# Configuración del cliente
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="PZCqeY4aWL1dSF0Npry5"
)

# Imagen a analizar: argumento de línea de comandos o ruta por defecto
if len(sys.argv) > 1:
    image_path = sys.argv[1]
else:
    image_path = r"C:\Users\izanj\OneDrive\Imágenes\Capturas de pantalla\Captura de pantalla 2026-02-10 124930.png"

if not os.path.exists(image_path):
    print(f"ERROR: No se encontró la imagen en: {image_path}")
    exit(1)

print(f"Usando imagen: {image_path}")
print(f"Modelo: 3d-printer-error-detection/5")
print(f"Método: API remota (serverless.roboflow.com)")
print()

try:
    # Realizar la inferencia con medición de tiempo
    print("Ejecutando inferencia remota...")
    t0 = time.perf_counter()
    result = CLIENT.infer(image_path, model_id="3d-printer-error-detection/5")
    t_infer = time.perf_counter() - t0
    print(f"Inferencia completada en {t_infer:.3f}s")
    print()

    # Dibujar bounding boxes sobre la imagen
    predictions = result.get("predictions", [])
    print(f"\nDetecciones encontradas: {len(predictions)}")

    if predictions:
        # Leer imagen como tensor (C, H, W) uint8 — formato requerido por draw_bounding_boxes
        img_tensor = read_image(image_path)

        # Si la imagen tiene 4 canales (RGBA), descartar el canal alfa para convertirla a RGB
        if img_tensor.shape[0] == 4:
            img_tensor = img_tensor[:3, :, :]

        # Construir tensor de bounding boxes [N, 4] en formato (x1, y1, x2, y2)
        boxes = []
        labels = []
        colors = []

        COLOR_PALETTE = [
            "red", "lime", "blue", "orange", "magenta", "cyan", "yellow",
            "deeppink", "springgreen", "dodgerblue",
        ]
        class_color_map = {}
        color_idx = 0

        for pred in predictions:
            x, y = pred["x"], pred["y"]
            w, h = pred["width"], pred["height"]
            confidence = pred["confidence"]
            class_name = pred["class"]

            x1 = x - w / 2
            y1 = y - h / 2
            x2 = x + w / 2
            y2 = y + h / 2

            boxes.append([x1, y1, x2, y2])
            labels.append(f"{class_name} {confidence:.1%}")

            # Asignar color por clase
            if class_name not in class_color_map:
                class_color_map[class_name] = COLOR_PALETTE[color_idx % len(COLOR_PALETTE)]
                color_idx += 1
            colors.append(class_color_map[class_name])

            print(f"  - {class_name}: {confidence:.1%} en ({int(x1)}, {int(y1)}) -> ({int(x2)}, {int(y2)})")

        boxes_tensor = torch.tensor(boxes, dtype=torch.float)

        # Dibujar bounding boxes con torchvision
        result_tensor = draw_bounding_boxes(
            img_tensor,
            boxes=boxes_tensor,
            labels=labels,
            colors=colors,
            width=3
        )

        # Convertir a PIL y guardar
        result_img = to_pil_image(result_tensor)
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, "resultado_deteccion.png")
        result_img.save(output_path)
        print(f"\nImagen con bounding boxes guardada en: {output_path}")

        # Mostrar la imagen
        result_img.show()
    else:
        print("No se detectaron errores en la imagen.")

    # ── Resumen de tiempos ─────────────────────────────────────
    print()
    print("=== Resumen (API remota) ===")
    print(f"  Inferencia (incluye subida + red + respuesta): {t_infer:.3f}s")
    print()
    print("Compara con test_inference_local.py para ver la diferencia de tiempos.")

except Exception as e:
    print(f"\nError durante la inferencia: {e}")
