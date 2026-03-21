"""
Script para exportar el modelo YOLOv8 entrenado a diferentes formatos.

Formatos disponibles:
    onnx       - ONNX (recomendado para Raspberry Pi con onnxruntime)
    ncnn       - NCNN (optimizado para ARM/móviles)
    tflite     - TensorFlow Lite (alternativa para Raspi)
    engine     - TensorRT (si tienes NVIDIA en la Raspi — Jetson)

Uso:
    python export_model.py
    python export_model.py --model runs/detect/3d_printer_error_detection/weights/best.pt
    python export_model.py --format onnx --imgsz 640
    python export_model.py --format ncnn --half
"""
import argparse
import sys
from pathlib import Path

from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(
        description="Exporta el modelo YOLOv8 entrenado a ONNX u otros formatos"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Ruta al modelo .pt entrenado (auto-detecta si no se especifica)",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="onnx",
        choices=["onnx", "ncnn", "tflite", "engine", "openvino"],
        help="Formato de exportación (default: onnx)",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Tamaño de imagen (default: 640)",
    )
    parser.add_argument(
        "--half",
        action="store_true",
        help="Exportar en FP16 (media precisión — más rápido, ligeramente menos preciso)",
    )
    parser.add_argument(
        "--simplify",
        action="store_true",
        default=True,
        help="Simplificar modelo ONNX (default: True)",
    )
    return parser.parse_args()


def find_best_model():
    """Busca automáticamente el mejor modelo entrenado."""
    project_root = Path(__file__).parent
    candidates = [
        project_root / "runs" / "detect" / "3d_printer_error_detection" / "weights" / "best.pt",
        project_root / "runs" / "detect" / "train" / "weights" / "best.pt",
    ]
    # También buscar cualquier best.pt en runs/
    runs_dir = project_root / "runs"
    if runs_dir.exists():
        for best in runs_dir.rglob("best.pt"):
            candidates.append(best)

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


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

    print("=" * 60)
    print("  EXPORTACIÓN DE MODELO YOLOv8")
    print("=" * 60)
    print(f"  Modelo     : {model_path}")
    print(f"  Formato    : {args.format}")
    print(f"  Imagen size: {args.imgsz}")
    print(f"  FP16 (half): {'Sí' if args.half else 'No'}")
    print("=" * 60)

    # Cargar modelo
    model = YOLO(str(model_path))

    # Exportar
    export_path = model.export(
        format=args.format,
        imgsz=args.imgsz,
        half=args.half,
        simplify=args.simplify if args.format == "onnx" else False,
    )

    print("\n" + "=" * 60)
    print("  EXPORTACIÓN COMPLETADA")
    print("=" * 60)
    print(f"\n  Modelo exportado en: {export_path}")
    print(f"\n  Para usar en la Raspberry Pi:")
    print(f"    1. Copia el archivo exportado a la Raspi")
    print(f"    2. Instala las dependencias necesarias:")
    if args.format == "onnx":
        print(f"       pip install onnxruntime ultralytics")
    elif args.format == "ncnn":
        print(f"       pip install ncnn ultralytics")
    elif args.format == "tflite":
        print(f"       pip install tflite-runtime ultralytics")
    print(f"    3. Usa el modelo con: YOLO('{export_path}')")
    print("=" * 60)


if __name__ == "__main__":
    main()
