"""
Test de inferencia LOCAL sin Docker
====================================
Usa la librería 'inference' directamente en Python, sin necesidad de
levantar un contenedor Docker ni un servidor HTTP.

Requisitos:
    pip install inference pillow

Uso:
    python test_inference_local.py                          # usa imagen de ejemplo
    python test_inference_local.py ruta/a/tu/imagen.png     # usa tu imagen
"""

import sys
import os
import time

# ── Configuración ──────────────────────────────────────────────
MODEL_ID = "3d-printer-error-detection/5"
API_KEY = "PZCqeY4aWL1dSF0Npry5"
# ───────────────────────────────────────────────────────────────


def main():
    # ── 1. Determinar imagen de entrada ────────────────────────
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Buscar cualquier imagen en el directorio actual como fallback
        for f in os.listdir("."):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp")):
                image_path = f
                break
        else:
            print("Uso: python test_inference_local.py <ruta_imagen>")
            print("No se encontró ninguna imagen en el directorio actual.")
            sys.exit(1)

    if not os.path.exists(image_path):
        print(f"ERROR: No se encontró la imagen: {image_path}")
        sys.exit(1)

    print(f"Imagen: {image_path}")
    print(f"Modelo: {MODEL_ID}")
    print()

    # ── 2. Cargar modelo local con inference ───────────────────
    print("Cargando modelo (primera vez descarga los pesos)...")
    t0 = time.perf_counter()

    try:
        from inference import get_model
    except ImportError:
        print("ERROR: La librería 'inference' no está instalada.")
        print("Instálala con:  pip install inference")
        sys.exit(1)

    model = get_model(model_id=MODEL_ID, api_key=API_KEY)
    t_load = time.perf_counter() - t0
    print(f"Modelo cargado en {t_load:.2f}s")
    print()

    # ── 3. Ejecutar inferencia ─────────────────────────────────
    print("Ejecutando inferencia...")
    # Cargar con Pillow para evitar fallos de OpenCV con rutas no-ASCII (tildes, ñ, etc.)
    from PIL import Image as PILImage
    import numpy as np
    img_input = np.array(PILImage.open(image_path).convert("RGB"))

    t0 = time.perf_counter()
    results = model.infer(img_input)
    t_infer = time.perf_counter() - t0
    print(f"Inferencia completada en {t_infer:.3f}s")
    print()

    # ── 4. Procesar resultados ─────────────────────────────────
    # inference puede devolver una lista o un solo objeto
    if isinstance(results, list):
        result = results[0] if results else {}
    else:
        result = results

    # Acceder a predicciones (puede ser dict o objeto con atributo)
    if hasattr(result, "predictions"):
        predictions = result.predictions
    elif isinstance(result, dict):
        predictions = result.get("predictions", [])
    else:
        predictions = []

    print(f"Detecciones totales: {len(predictions)}")
    print()

    if not predictions:
        print("No se detectaron errores en la imagen.")
        return

    # ── 5. Mostrar TODAS las detecciones ───────────────────────
    for i, pred in enumerate(predictions, 1):
        if hasattr(pred, "class_name"):
            cls = pred.class_name
            conf = pred.confidence
            x, y = pred.x, pred.y
            w, h = pred.width, pred.height
        else:
            cls = pred.get("class", pred.get("class_name", "?"))
            conf = pred.get("confidence", 0)
            x, y = pred.get("x", 0), pred.get("y", 0)
            w, h = pred.get("width", 0), pred.get("height", 0)

        x1, y1 = int(x - w / 2), int(y - h / 2)
        x2, y2 = int(x + w / 2), int(y + h / 2)
        print(f"  {i}. {cls}: {conf:.1%}  [{x1},{y1} -> {x2},{y2}]")

    # ── 6. Dibujar bounding boxes (con Pillow, sin torch) ──────
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("\nInstala Pillow para ver la imagen con bounding boxes: pip install pillow")
        return

    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    COLORS = ["red", "lime", "blue", "orange", "magenta", "cyan", "yellow", "deeppink"]
    class_colors = {}
    ci = 0

    for pred in predictions:
        if hasattr(pred, "class_name"):
            cls = pred.class_name
            conf = pred.confidence
            x, y = pred.x, pred.y
            w, h = pred.width, pred.height
        else:
            cls = pred.get("class", pred.get("class_name", "?"))
            conf = pred.get("confidence", 0)
            x, y = pred.get("x", 0), pred.get("y", 0)
            w, h = pred.get("width", 0), pred.get("height", 0)

        if cls not in class_colors:
            class_colors[cls] = COLORS[ci % len(COLORS)]
            ci += 1
        color = class_colors[cls]

        x1, y1 = x - w / 2, y - h / 2
        x2, y2 = x + w / 2, y + h / 2
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        label = f"{cls} {conf:.1%}"
        draw.text((x1 + 4, y1 + 2), label, fill=color)

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultado_inference_local.png")
    img.save(output_path)
    print(f"\nImagen guardada en: {output_path}")
    img.show()

    # ── 7. Resumen de tiempos ──────────────────────────────────
    print()
    print("=== Resumen ===")
    print(f"  Carga del modelo: {t_load:.2f}s")
    print(f"  Inferencia:       {t_infer:.3f}s")
    print(f"  Total:            {t_load + t_infer:.2f}s")


if __name__ == "__main__":
    main()
