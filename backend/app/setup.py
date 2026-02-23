import os
import time
import getpass
import requests
from dotenv import load_dotenv, set_key


class KeyManagement: 
    def __init__(self):
        self.env_path = os.path.join(os.path.dirname(__file__), ".env.back.template")
        load_dotenv(dotenv_path=self.env_path)
        
        self.octoprint_url = os.getenv("OCTOPRINT_URL", "http://localhost")
        self.api_key = os.getenv("OCTOPRINT_API_KEY", "")
        
    def check_octoprint_url(self) -> bool:
        if self.octoprint_url is None or self.octoprint_url == "":
            return False
        return True
    
    def check_api_key(self) -> bool:
        if self.api_key is None or self.api_key == "":
            return False
        return True
    
    def check_conection(self, retries: int = 5, delay: int = 3) -> bool:
        """
        Comprueba la conexión con OctoPrint.
        Reintenta varias veces por si OctoPrint aún está arrancando.
        """
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(
                    f"{self.octoprint_url}/api/version",
                    headers={"X-Api-Key": self.api_key},
                    timeout=5
                )
                if response.status_code == 200:
                    return True
                elif response.status_code == 403:
                    print("API key rechazada. Verifica que sea correcta.")
                    return False
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
                new_url = input("URL de OctoPrint (ej: http://localhost): ").strip()
                if new_url:
                    self.octoprint_url = new_url
                    print("URL de OctoPrint actualizada.")
                    break
                else:
                    print("La URL no puede estar vacía. Inténtalo de nuevo.")
        
        if not self.check_api_key():
            while True:
                new_key = getpass.getpass("API key de OctoPrint (Settings > API): ").strip()
                if new_key:
                    self.api_key = new_key
                    print("API key actualizada.")
                    break
                else:
                    print("La API key no puede estar vacía. Inténtalo de nuevo.")
                    
        print(f"Comprobando conexión con OctoPrint en {self.octoprint_url}...")
        if not self.check_conection():
            print("No se pudo conectar a OctoPrint. Verifica que:")
            print("  1. El servicio esté activo: sudo systemctl status octoprint")
            print("  2. La API key sea correcta (Settings > API en OctoPrint)")
            return False
        print("Conexión con OctoPrint validada correctamente.")
        
        set_key(self.env_path, "OCTOPRINT_URL", self.octoprint_url)
        set_key(self.env_path, "OCTOPRINT_API_KEY", self.api_key)
        
        # Recargar las variables de entorno para que config.py las vea
        load_dotenv(dotenv_path=self.env_path, override=True)
        
        return True
                

keyMangement = KeyManagement()