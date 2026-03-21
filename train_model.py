"""
Script de entrenamiento YOLOv8 para detección de errores en impresión 3D.

Uso básico:
    python train_model.py

Uso con opciones:
    python train_model.py --model yolov8s.pt --epochs 150 --batch 16 --imgsz 640

Modelos disponibles (de menor a mayor):
    yolov8n.pt  - Nano   (~3.2M params)  → Mejor para Raspberry Pi
    yolov8s.pt  - Small  (~11.2M params) → Buen balance
    yolov8m.pt  - Medium (~25.9M params) → Mayor precisión

Requisitos:
    pip install -r requirements_training.txt
    CUDA toolkit instalado (para GPU NVIDIA)
"""
import argparse
import sys
from pathlib import Path

from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(
        description="Entrena un modelo YOLOv8 para detección de errores en impresión 3D"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        help="Modelo base preentrenado (default: yolov8n.pt — nano, óptimo para Raspi)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Número de épocas de entrenamiento (default: 100)",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=16,
        help="Tamaño de batch — con 4060 Ti puedes usar 16 o 32 (default: 16)",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Tamaño de imagen de entrada (default: 640)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="0",
        help="Dispositivo: '0' para GPU, 'cpu' para CPU (default: '0')",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="3d_printer_error_detection",
        help="Nombre del experimento (carpeta de salida)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reanudar entrenamiento desde el último checkpoint",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Ruta al dataset config
    project_root = Path(__file__).parent
    data_yaml = project_root / "data_local.yaml"

    if not data_yaml.exists():
        print(f"ERROR: No se encontró {data_yaml}")
        sys.exit(1)

    print("=" * 60)
    print("  ENTRENAMIENTO YOLOv8 - Detección de errores 3D")
    print("=" * 60)
    print(f"  Modelo base  : {args.model}")
    print(f"  Épocas       : {args.epochs}")
    print(f"  Batch size   : {args.batch}")
    print(f"  Imagen size  : {args.imgsz}")
    print(f"  Dispositivo  : {'GPU (CUDA)' if args.device != 'cpu' else 'CPU'}")
    print(f"  Dataset      : {data_yaml}")
    print("=" * 60)

    # Cargar modelo preentrenado
    if args.resume:
        # Reanudar desde último checkpoint
        last_checkpoint = (
            project_root / "runs" / "detect" / args.name / "weights" / "last.pt"
        )
        if not last_checkpoint.exists():
            print(f"ERROR: No se encontró checkpoint para reanudar: {last_checkpoint}")
            sys.exit(1)
        print(f"\nReanudando entrenamiento desde: {last_checkpoint}")
        model = YOLO(str(last_checkpoint))
    else:
        print(f"\nCargando modelo preentrenado: {args.model}")
        model = YOLO(args.model)

    # Entrenar
    results = model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        project=str(project_root / "runs" / "detect"),
        name=args.name,
        exist_ok=True,
        # Hiperparámetros optimizados para dataset pequeño
        patience=20,          # Early stopping: para si no mejora en 20 épocas
        save=True,            # Guardar checkpoints
        save_period=10,       # Guardar cada 10 épocas
        pretrained=True,      # Usar pesos preentrenados
        optimizer="auto",     # Deja que YOLOv8 elija el mejor optimizador
        lr0=0.01,             # Learning rate inicial
        lrf=0.01,             # Learning rate final (fracción del inicial)
        warmup_epochs=5,      # Épocas de warmup
        warmup_momentum=0.8,  # Momentum durante warmup
        cos_lr=True,          # Usar cosine learning rate scheduler
        # Augmentaciones adicionales para compensar dataset pequeño
        hsv_h=0.015,          # Augmentación de hue
        hsv_s=0.7,            # Augmentación de saturación
        hsv_v=0.4,            # Augmentación de brillo
        degrees=10.0,         # Rotación aleatoria ±10°
        translate=0.1,        # Translación aleatoria
        scale=0.5,            # Escala aleatoria
        flipud=0.5,           # Flip vertical
        fliplr=0.5,           # Flip horizontal
        mosaic=1.0,           # Mosaic augmentation (muy útil con pocos datos)
        mixup=0.1,            # Mixup augmentation
    )

    # Resultados
    print("\n" + "=" * 60)
    print("  ENTRENAMIENTO COMPLETADO")
    print("=" * 60)

    best_weights = project_root / "runs" / "detect" / args.name / "weights" / "best.pt"
    print(f"\n  Mejores pesos guardados en:")
    print(f"    {best_weights}")
    print(f"\n  Para usar el modelo:")
    print(f"    python test_model.py --model {best_weights}")
    print(f"\n  Para exportar a ONNX (para Raspi):")
    print(f"    python export_model.py --model {best_weights}")
    print(f"\n  Resultados de entrenamiento en:")
    print(f"    {project_root / 'runs' / 'detect' / args.name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
