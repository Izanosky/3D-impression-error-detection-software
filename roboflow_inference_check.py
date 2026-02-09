from inference_sdk import InferenceHTTPClient
import os

# Configuración del cliente (usando la clave proporcionada)
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="PZCqeY4aWL1dSF0Npry5"
)

# Buscar una imagen válida en el directorio actual
# El código original era: result = CLIENT.infer(your_image.jpg, model_id="3d-printer-error-detection/5")
# Asumimos que 'your_image.jpg' se refiere a un archivo de imagen.

image_files = [f for f in os.listdir('.') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
if image_files:
    image_path = image_files[0]
    print(f"Usando imagen encontrada: {image_path}")
else:
    # Si no hay imagen, creamos una imagen negra de prueba para verificar conectividad
    print("No se encontraron imágenes. Intentando usar una imagen de prueba generada...")
    try:
        from PIL import Image
        img = Image.new('RGB', (640, 640), color = 'red')
        image_path = "test_gen_image.jpg"
        img.save(image_path)
        print(f"Imagen de prueba generada: {image_path}")
    except ImportError:
        print("No se encontraron imágenes y PIL no está instalado para generar una.")
        print("Por favor, coloca una imagen .jpg en este directorio.")
        image_path = "test_image.jpg" # Fallback a nombre por defecto

print(f"Iniciando inferencia en {image_path} con el modelo '3d-printer-error-detection/5'...")

try:
    # Realizar la inferencia
    result = CLIENT.infer(image_path, model_id="3d-printer-error-detection/5")
    
    # Mostrar el resultado
    print("\nResultado de la inferencia:")
    print(result)
    
except Exception as e:
    print(f"\nError durante la inferencia: {e}")
