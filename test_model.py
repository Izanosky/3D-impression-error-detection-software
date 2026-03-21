"""
Script para probar el modelo YOLOv8 entrenado en imágenes de test.

Uso:
    # Probar en todas las imágenes del dataset de test
    python test_model.py

    # Probar en una imagen específica
    python test_model.py --source path/to/image.jpg

    # Probar desde una URL de cámara (streaming)
    python test_model.py --source "http://192.168.1.100/webcam/?action=snapshot"

    # Evaluar métricas en el dataset de validación
    python test_model.py --val

    # Guardar imágenes con detecciones
    python test_model.py --save
"""
import argparse
import sys
from pathlib import Path

from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prueba el modelo YOLOv8 entrenado para detección de errores 3D"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Ruta al modelo .pt o .onnx (auto-detecta si no se especifica)",
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Imagen, carpeta, o URL de cámara. Si no se especifica, usa test/images",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.5,
        help="Umbral de confianza mínimo (default: 0.5)",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Tamaño de imagen (default: 640)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Guardar imágenes con detecciones dibujadas",
    )
    parser.add_argument(
        "--val",
        action="store_true",
        help="Ejecutar evaluación formal (mAP, precision, recall) en el dataset de validación",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="0",
        help="Dispositivo: '0' para GPU, 'cpu' para CPU (default: '0')",
    )
    return parser.parse_args()


def find_best_model():
    """Busca automáticamente el mejor modelo entrenado."""
    project_root = Path(__file__).parent
    candidates = [
        project_root / "runs" / "detect" / "3d_printer_error_detection" / "weights" / "best.pt",
        project_root / "runs" / "detect" / "train" / "weights" / "best.pt",
    ]
    runs_dir = project_root / "runs"
    if runs_dir.exists():
        for best in runs_dir.rglob("best.pt"):
            candidates.append(best)

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def run_validation(model, args, project_root):
    """Ejecuta evaluación formal en el dataset de validación."""
    data_yaml = project_root / "data_local.yaml"
    if not data_yaml.exists():
        print("ERROR: No se encontró data_local.yaml")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  EVALUACIÓN EN DATASET DE VALIDACIÓN")
    print("=" * 60)

    results = model.val(
        data=str(data_yaml),
        imgsz=args.imgsz,
        conf=args.conf,
        device=args.device,
    )

    print(f"\n  Resultados:")
    print(f"    mAP50      : {results.box.map50:.4f}")
    print(f"    mAP50-95   : {results.box.map:.4f}")
    print(f"    Precision  : {results.box.mp:.4f}")
    print(f"    Recall     : {results.box.mr:.4f}")
    print("=" * 60)


def run_inference(model, args, project_root):
    """Ejecuta inferencia en imágenes."""
    # Determinar fuente
    if args.source:
        source = args.source
    else:
        # Usar imágenes de test del dataset
        test_images = project_root / "3d printer error detection.v1-prueba.yolov8" / "test" / "images"
        if not test_images.exists():
            print(f"ERROR: No se encontró carpeta de test: {test_images}")
            sys.exit(1)
        source = str(test_images)

    print(f"\n  Fuente: {source}")
    print("-" * 60)

    # Ejecutar predicción
    results = model.predict(
        source=source,
        conf=args.conf,
        imgsz=args.imgsz,
        save=args.save,
        device=args.device,
        project=str(project_root / "runs" / "detect"),
        name="test_results",
        exist_ok=True,
    )

    # Mostrar resultados
    total_detections = 0
    for i, result in enumerate(results):
        boxes = result.boxes
        img_name = Path(result.path).name if result.path else f"imagen_{i}"

        if len(boxes) == 0:
            print(f"  [{img_name}] Sin errores detectados ✓")
        else:
            print(f"  [{img_name}] {len(boxes)} error(es) detectado(s) ✗")
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()
                cls_name = result.names[cls_id]
                print(f"    → {cls_name}: {conf:.1%} | bbox: [{xyxy[0]:.0f}, {xyxy[1]:.0f}, {xyxy[2]:.0f}, {xyxy[3]:.0f}]")
                total_detections += 1

    print("-" * 60)
    print(f"  Total: {total_detections} detección(es) en {len(results)} imagen(es)")

    if args.save:
        print(f"\n  Imágenes con detecciones guardadas en:")
        print(f"    {project_root / 'runs' / 'detect' / 'test_results'}")


def main():
    args = parse_args()

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

    project_root = Path(__file__).parent

    print("=" * 60)
    print("  TEST YOLOv8 - Detección de errores 3D")
    print("=" * 60)
    print(f"  Modelo     : {model_path}")
    print(f"  Confianza  : {args.conf:.0%}")
    print(f"  Dispositivo: {'GPU (CUDA)' if args.device != 'cpu' else 'CPU'}")

    # Cargar modelo
    model = YOLO(str(model_path))

    if args.val:
        run_validation(model, args, project_root)
    else:
        run_inference(model, args, project_root)


if __name__ == "__main__":
    main()
