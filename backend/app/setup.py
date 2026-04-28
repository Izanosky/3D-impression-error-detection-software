import os
import time
import getpass
import requests
from dotenv import load_dotenv, set_key


class KeyManagement:
    """Gestiona la configuración de conexión con OctoPrint."""

    def __init__(self):
        self.env_path = os.path.join(os.path.dirname(__file__), ".env.back.template")
        load_dotenv(dotenv_path=self.env_path)
        self.octoprint_url = os.getenv("OCTOPRINT_URL", "http://localhost")
        self.api_key = os.getenv("OCTOPRINT_API_KEY", "")

    def check_octoprint_url(self):
        return bool(self.octoprint_url)

    def check_api_key(self):
        return bool(self.api_key)

    def check_connection(self, retries=5, delay=3):
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(
                    f"{self.octoprint_url}/api/version",
                    headers={"X-Api-Key": self.api_key},
                    timeout=5,
                )
                if response.status_code == 200:
                    return True
                if response.status_code == 403:
                    print("API key rechazada. Verifica que sea correcta.")
                    return False
            except requests.ConnectionError:
                print(f"Intento {attempt}/{retries}: OctoPrint no disponible, reintentando en {delay}s...")
            except Exception as e:
                print(f"Intento {attempt}/{retries}: Error al conectar con OctoPrint: {e}")

            if attempt < retries:
                time.sleep(delay)

        return False

    def validate_configuration(self):
        """Valida URL, API key y conexión. Pide datos por consola si faltan."""
        if not self.check_octoprint_url():
            while True:
                new_url = input("URL de OctoPrint (ej: http://localhost): ").strip()
                if new_url:
                    self.octoprint_url = new_url
                    break
                print("La URL no puede estar vacía.")

        if not self.check_api_key():
            while True:
                new_key = getpass.getpass("API key de OctoPrint (Settings > API): ").strip()
                if new_key:
                    self.api_key = new_key
                    break
                print("La API key no puede estar vacía.")

        print(f"Comprobando conexión con OctoPrint en {self.octoprint_url}...")
        if not self.check_connection():
            print("No se pudo conectar a OctoPrint. Verifica que:")
            print("  1. El servicio esté activo: sudo systemctl status octoprint")
            print("  2. La API key sea correcta (Settings > API en OctoPrint)")
            return False

        print("Conexión con OctoPrint validada correctamente.")

        set_key(self.env_path, "OCTOPRINT_URL", self.octoprint_url)
        set_key(self.env_path, "OCTOPRINT_API_KEY", self.api_key)
        load_dotenv(dotenv_path=self.env_path, override=True)

        return True


key_management = KeyManagement()