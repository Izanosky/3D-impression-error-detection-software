"""
Procesamiento de imágenes - Dibujado de bounding boxes
"""
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from app.config import CONFIDENCE_THRESHOLD


def draw_detections(image_bytes: bytes, predictions: list) -> bytes:
    """
    Dibuja bounding boxes sobre la imagen
    
    Args:
        image_bytes: Bytes de la imagen original
        predictions: Lista de predicciones del modelo Roboflow
        
    Returns:
        Bytes de la imagen con las detecciones dibujadas
    """
    # Cargar imagen
    image = Image.open(BytesIO(image_bytes))
    draw = ImageDraw.Draw(image)
    
    # Intentar cargar una fuente, si no usar la por defecto
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    for pred in predictions:
        confidence = pred.get("confidence", 0)
        
        # Filtrar por umbral de confianza
        if confidence < CONFIDENCE_THRESHOLD:
            continue
        
        # Obtener coordenadas (x, y son el centro)
        x = pred.get("x", 0)
        y = pred.get("y", 0)
        width = pred.get("width", 0)
        height = pred.get("height", 0)
        class_name = pred.get("class", "error")
        
        # Calcular esquinas del bounding box
        x1 = x - width / 2
        y1 = y - height / 2
        x2 = x + width / 2
        y2 = y + height / 2
        
        # Color según confianza (rojo más intenso = más confianza)
        red_intensity = int(155 + confidence * 100)
        color = (red_intensity, 50, 50)
        
        # Dibujar rectángulo
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        
        # Dibujar etiqueta
        label = f"{class_name}: {confidence:.1%}"
        
        # Fondo de la etiqueta
        bbox = draw.textbbox((x1, y1 - 20), label, font=font)
        draw.rectangle(bbox, fill=color)
        draw.text((x1, y1 - 20), label, fill="white", font=font)
    
    # Convertir a bytes
    output = BytesIO()
    image.save(output, format="JPEG", quality=85)
    return output.getvalue()


def get_detection_summary(predictions: list) -> dict:
    """
    Genera un resumen de las detecciones
    
    Args:
        predictions: Lista de predicciones
        
    Returns:
        Resumen con conteo por clase y confianza promedio
    """
    filtered = [p for p in predictions if p.get("confidence", 0) >= CONFIDENCE_THRESHOLD]
    
    if not filtered:
        return {
            "total_detections": 0,
            "classes": {},
            "max_confidence": 0,
            "has_errors": False
        }
    
    # Contar por clase
    classes = {}
    for pred in filtered:
        class_name = pred.get("class", "unknown")
        if class_name not in classes:
            classes[class_name] = {"count": 0, "max_confidence": 0}
        classes[class_name]["count"] += 1
        classes[class_name]["max_confidence"] = max(
            classes[class_name]["max_confidence"],
            pred.get("confidence", 0)
        )
    
    return {
        "total_detections": len(filtered),
        "classes": classes,
        "max_confidence": max(p.get("confidence", 0) for p in filtered),
        "has_errors": len(filtered) > 0
    }
