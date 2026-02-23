import os
import requests
from dotenv import load_dotenv, set_key


class KeyManagement: 
    def __init__(self):
        self.env_path = os.path.join(os.path.dirname(__file__), ".env.back.template")
        load_dotenv(dotenv_path=self.env_path)
        
        self.octoprint_url = os.getenv("OCTOPRINT_URL", "")
        
    def check_octoprint_url(self) -> bool:
        if self.octoprint_url is None or self.octoprint_url == "":
            return False
        return True
    
    def check_conection(self) -> bool:
        try:
            # Usar /api/version porque /api/printer devuelve 409 si la
            # impresora no está conectada físicamente al dispositivo
            response = requests.get(f"{self.octoprint_url}/api/version", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Error al conectar con OctoPrint: {e}")
            return False
    
    def validate_configuration(self) -> bool:
        if not self.check_octoprint_url():
            while True:
                new_url = input("URL/IP de OctoPrint no configurada (ej: http://192.168.1.100): ").strip()
                if new_url:
                    self.octoprint_url = new_url
                    print("URL de OctoPrint actualizada.")
                    break
                else:
                    print("La URL no puede estar vacía. Inténtalo de nuevo.")
                    
        if not self.check_conection():
            print("No se pudo conectar a OctoPrint con la IP/URL actual. Por favor verifica que el dispositivo esté encendido y accesible.")
            return False
        print("Conexión con OctoPrint validada correctamente.")
        
        set_key(self.env_path, "OCTOPRINT_URL", self.octoprint_url)
        
        # Recargar las variables de entorno para que config.py las vea
        load_dotenv(dotenv_path=self.env_path, override=True)
        
        return True
                

keyMangement = KeyManagement()