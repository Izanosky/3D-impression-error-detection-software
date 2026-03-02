"""
Benchmark comparativo: Inferencia LOCAL vs API REMOTA
======================================================
Ejecuta 50 inferencias con cada método y genera estadísticas
para una tabla comparativa.

Requisitos:
    pip install inference inference-sdk pillow numpy

Uso:
    python benchmark_inference.py "ruta/a/tu/imagen.png"
"""

import sys
import os
import time
import statistics

# ── Configuración ──────────────────────────────────────────────
MODEL_ID = "3d-printer-error-detection/5"
API_KEY = "PZCqeY4aWL1dSF0Npry5"
NUM_ITERATIONS = 50
# ───────────────────────────────────────────────────────────────


def benchmark_local(img_array, num_iter):
    """Benchmark de inferencia local con la librería inference."""
    from inference import get_model

    print("=" * 60)
    print("  INFERENCIA LOCAL (librería inference)")
    print("=" * 60)

    # Carga del modelo
    print(f"\nCargando modelo...")
    t0 = time.perf_counter()
    model = get_model(model_id=MODEL_ID, api_key=API_KEY)
    t_load = time.perf_counter() - t0
    print(f"Modelo cargado en {t_load:.2f}s")

    # Warmup (1 inferencia que no se cuenta)
    print("Warmup...")
    model.infer(img_array)

    # Benchmark
    times = []
    print(f"\nEjecutando {num_iter} inferencias...")
    for i in range(num_iter):
        t0 = time.perf_counter()
        model.infer(img_array)
        elapsed = time.perf_counter() - t0
        times.append(elapsed)

        # Progreso cada 10 iteraciones
        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{num_iter} completadas...")

    return t_load, times


def benchmark_remote(image_path, num_iter):
    """Benchmark de inferencia remota con la API de Roboflow."""
    from inference_sdk import InferenceHTTPClient

    print("\n" + "=" * 60)
    print("  INFERENCIA REMOTA (API serverless.roboflow.com)")
    print("=" * 60)

    client = InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key=API_KEY
    )

    # Warmup (1 petición que no se cuenta)
    print("\nWarmup...")
    client.infer(image_path, model_id=MODEL_ID)

    # Benchmark
    times = []
    print(f"\nEjecutando {num_iter} peticiones...")
    for i in range(num_iter):
        t0 = time.perf_counter()
        client.infer(image_path, model_id=MODEL_ID)
        elapsed = time.perf_counter() - t0
        times.append(elapsed)

        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{num_iter} completadas...")

    return times


def print_stats(label, times):
    """Imprime estadísticas de una lista de tiempos."""
    avg = statistics.mean(times)
    med = statistics.median(times)
    mn = min(times)
    mx = max(times)
    std = statistics.stdev(times) if len(times) > 1 else 0.0
    p95 = sorted(times)[int(len(times) * 0.95)]

    print(f"\n  {label}")
    print(f"  {'─' * 40}")
    print(f"  Media:        {avg * 1000:>8.1f} ms")
    print(f"  Mediana:      {med * 1000:>8.1f} ms")
    print(f"  Mínimo:       {mn * 1000:>8.1f} ms")
    print(f"  Máximo:       {mx * 1000:>8.1f} ms")
    print(f"  Desv. est.:   {std * 1000:>8.1f} ms")
    print(f"  Percentil 95: {p95 * 1000:>8.1f} ms")

    return {"avg": avg, "med": med, "min": mn, "max": mx, "std": std, "p95": p95}


def main():
    # ── 1. Imagen de entrada ───────────────────────────────────
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("Uso: python benchmark_inference.py <ruta_imagen>")
        sys.exit(1)

    if not os.path.exists(image_path):
        print(f"ERROR: No se encontró la imagen: {image_path}")
        sys.exit(1)

    # Cargar imagen como array (para local)
    from PIL import Image
    import numpy as np
    img_array = np.array(Image.open(image_path).convert("RGB"))

    print(f"Imagen:      {image_path}")
    print(f"Modelo:      {MODEL_ID}")
    print(f"Iteraciones: {NUM_ITERATIONS}")
    print(f"Resolución:  {img_array.shape[1]}x{img_array.shape[0]} px")

    # ── 2. Benchmark LOCAL ─────────────────────────────────────
    t_load, local_times = benchmark_local(img_array, NUM_ITERATIONS)

    # ── 3. Benchmark REMOTO ────────────────────────────────────
    remote_times = benchmark_remote(image_path, NUM_ITERATIONS)

    # ── 4. Resultados ──────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  RESULTADOS  ({} iteraciones)".format(NUM_ITERATIONS))
    print("=" * 60)

    local_stats = print_stats("LOCAL (inference)", local_times)
    remote_stats = print_stats("REMOTO (API cloud)", remote_times)

    # ── 5. Tabla comparativa ───────────────────────────────────
    speedup = remote_stats["avg"] / local_stats["avg"]

    print("\n" + "=" * 60)
    print("  TABLA COMPARATIVA")
    print("=" * 60)
    print()
    print(f"  {'Métrica':<20} {'Local (ms)':>12} {'Remoto (ms)':>12} {'Factor':>8}")
    print(f"  {'─' * 52}")
    print(f"  {'Media':<20} {local_stats['avg']*1000:>12.1f} {remote_stats['avg']*1000:>12.1f} {speedup:>7.1f}x")
    print(f"  {'Mediana':<20} {local_stats['med']*1000:>12.1f} {remote_stats['med']*1000:>12.1f} {remote_stats['med']/local_stats['med']:>7.1f}x")
    print(f"  {'Mínimo':<20} {local_stats['min']*1000:>12.1f} {remote_stats['min']*1000:>12.1f} {remote_stats['min']/local_stats['min']:>7.1f}x")
    print(f"  {'Máximo':<20} {local_stats['max']*1000:>12.1f} {remote_stats['max']*1000:>12.1f} {remote_stats['max']/local_stats['max']:>7.1f}x")
    print(f"  {'Desv. estándar':<20} {local_stats['std']*1000:>12.1f} {remote_stats['std']*1000:>12.1f}")
    print(f"  {'Percentil 95':<20} {local_stats['p95']*1000:>12.1f} {remote_stats['p95']*1000:>12.1f} {remote_stats['p95']/local_stats['p95']:>7.1f}x")
    print()
    print(f"  Carga del modelo local: {t_load:.2f}s (una sola vez al arrancar)")
    print(f"  Speedup medio: la inferencia local es ~{speedup:.0f}x más rápida")
    print()

    # ── 6. Exportar CSV ───────────────────────────────────────
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_results.csv")
    with open(csv_path, "w") as f:
        f.write("iteracion,local_ms,remoto_ms\n")
        for i in range(NUM_ITERATIONS):
            f.write(f"{i+1},{local_times[i]*1000:.2f},{remote_times[i]*1000:.2f}\n")

    print(f"  Datos exportados a: {csv_path}")
    print(f"  (Puedes importar el CSV en Excel/Sheets para hacer gráficas)")


if __name__ == "__main__":
    main()
