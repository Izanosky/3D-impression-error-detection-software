import os
import time
import requests
from dotenv import load_dotenv, set_key


class KeyManagement: 
    def __init__(self):
        self.env_path = os.path.join(os.path.dirname(__file__), ".env.back.template")
        load_dotenv(dotenv_path=self.env_path)
        
        self.octoprint_url = os.getenv("OCTOPRINT_URL", "http://localhost:5000")
        
    def check_octoprint_url(self) -> bool:
        if self.octoprint_url is None or self.octoprint_url == "":
            return False
        return True
    
    def check_conection(self, retries: int = 5, delay: int = 3) -> bool:
        """
        Comprueba la conexión con OctoPrint.
        Reintenta varias veces por si OctoPrint aún está arrancando.
        """
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(f"{self.octoprint_url}/api/version", timeout=5)
                if response.status_code == 200:
                    return True
            except requests.ConnectionError:
                print(f"Intento {attempt}/{retries}: OctoPrint no disponible, reintentando en {delay}s...")
            except Exception as e:
                print(f"Intento {attempt}/{retries}: Error al conectar con OctoPrint: {e}")
            
            if attempt < retries:
                time.sleep(delay)
        
        return False
    
    def validate_configuration(self) -> bool:
        if not self.check_octoprint_url():
            while True:
                new_url = input("URL/IP de OctoPrint no configurada (ej: http://localhost:5000): ").strip()
                if new_url:
                    self.octoprint_url = new_url
                    print("URL de OctoPrint actualizada.")
                    break
                else:
                    print("La URL no puede estar vacía. Inténtalo de nuevo.")
                    
        print(f"Comprobando conexión con OctoPrint en {self.octoprint_url}...")
        if not self.check_conection():
            print("No se pudo conectar a OctoPrint. Verifica que el servicio esté activo:")
            print("  sudo systemctl status octoprint")
            print("  sudo systemctl start octoprint")
            return False
        print("Conexión con OctoPrint validada correctamente.")
        
        set_key(self.env_path, "OCTOPRINT_URL", self.octoprint_url)
        
        # Recargar las variables de entorno para que config.py las vea
        load_dotenv(dotenv_path=self.env_path, override=True)
        
        return True
                

keyMangement = KeyManagement()