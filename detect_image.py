"""
Script simple para detectar errores en una imagen y mostrar el resultado visual.

Uso:
    python detect_image.py ruta/a/imagen.jpg
    python detect_image.py ruta/a/imagen.jpg --conf 0.3
    python detect_image.py ruta/a/imagen.jpg --save
    python detect_image.py ruta/a/imagen.jpg --model ruta/a/modelo.pt
"""
import argparse
import sys
from pathlib import Path

import cv2
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(
        description="Detecta errores de impresión 3D en una imagen y muestra el resultado"
    )
    parser.add_argument(
        "image",
        type=str,
        help="Ruta a la imagen a analizar",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Ruta al modelo .pt (auto-detecta si no se especifica)",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.5,
        help="Umbral de confianza mínimo (default: 0.5)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Guardar la imagen resultado además de mostrarla",
    )
    return parser.parse_args()


def find_best_model():
    """Busca automáticamente el mejor modelo entrenado."""
    project_root = Path(__file__).parent
    candidates = [
        project_root / "runs" / "detect" / "3d_printer_error_detection" / "weights" / "best.pt",
        project_root / "runs" / "detect" / "train" / "weights" / "best.pt",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    # Buscar cualquier best.pt en runs/
    runs_dir = project_root / "runs"
    if runs_dir.exists():
        for best in runs_dir.rglob("best.pt"):
            return best
    return None


def main():
    args = parse_args()

    # Verificar que la imagen existe
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"ERROR: No se encontró la imagen: {image_path}")
        sys.exit(1)

    # Encontrar modelo
    if args.model:
        model_path = Path(args.model)
    else:
        model_path = find_best_model()

    if model_path is None or not model_path.exists():
        print("ERROR: No se encontró un modelo entrenado.")
        print("  Entrena primero: python train_model.py")
        print("  O especifica la ruta: --model path/to/best.pt")
        sys.exit(1)

    print(f"Modelo : {model_path}")
    print(f"Imagen : {image_path}")
    print(f"Conf   : {args.conf:.0%}")

    # Cargar modelo y ejecutar predicción
    model = YOLO(str(model_path))
    results = model.predict(
        source=str(image_path),
        conf=args.conf,
        verbose=False,
    )

    result = results[0]

    # Dibujar las detecciones sobre la imagen (YOLO lo hace automáticamente con plot())
    annotated = result.plot()  # Devuelve imagen BGR con bounding boxes dibujados

    # Mostrar info en consola
    boxes = result.boxes
    if len(boxes) == 0:
        print("\n✓ No se detectaron errores en la imagen.")
    else:
        print(f"\n✗ {len(boxes)} error(es) detectado(s):")
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            cls_name = result.names[cls_id]
            xyxy = box.xyxy[0].tolist()
            print(f"  → {cls_name}: {conf:.1%} | bbox: [{xyxy[0]:.0f}, {xyxy[1]:.0f}, {xyxy[2]:.0f}, {xyxy[3]:.0f}]")

    # Guardar si se pidió
    if args.save:
        output_path = image_path.parent / f"{image_path.stem}_deteccion{image_path.suffix}"
        cv2.imwrite(str(output_path), annotated)
        print(f"\nImagen guardada en: {output_path}")

    # Mostrar la imagen con detecciones
    cv2.imshow("Deteccion de errores 3D", annotated)
    print("\nPresiona cualquier tecla en la ventana de la imagen para cerrar...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
