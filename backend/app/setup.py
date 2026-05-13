"""
Clase que gestiona las claves y la url para la conexión con OctoPrint
"""

import os
import time
import getpass
import requests

# Biblioteca auxliar que nos ayuda con la carga de los ficheros .env y las variables contenidas en el mismo
from dotenv import load_dotenv, set_key 


class KeyManagement:
    def __init__(self):

        """
        Para su correcto funcionamiento, debe existir un archivo .env.back.template en el directorio app
        con las variables OCTOPRINT_URL y OCTOPRINT_API_KEY
        """

        self.env_path = os.path.join(os.path.dirname(__file__), ".env.back.template") # Ruta del archivo .env.back.template
        load_dotenv(dotenv_path=self.env_path) # Carga las variables del archivo .env.back.template
        self.octoprint_url = os.getenv("OCTOPRINT_URL", "http://localhost") # Obtenemos la URL de OctoPrint
        self.api_key = os.getenv("OCTOPRINT_API_KEY", "") # Obtenemos la API key de OctoPrint


    # Metodos auxiliares para verificar la URL y la API key
    def check_octoprint_url(self):
        return bool(self.octoprint_url)

    def check_api_key(self):
        return bool(self.api_key)

    # -----------------------------------------------------

    # Este metodo lo utilizamos para comprobar si, con las claves introducidas, se puede establecer conexión con OctoPrint correctamente
    def check_connection(self, retries=5, delay=3):
        for intento in range(1, retries + 1):
            try:
                
                # Utilizamos uno de los endpoints proporcionados por OctoPrint para verificar la conexión, concretamente el de version
                response = requests.get(
                    f"{self.octoprint_url}/api/version",
                    headers={"X-Api-Key": self.api_key},
                    timeout=5,
                )

                # Si nos devuelve 200, significa que la conexión es correcta
                if response.status_code == 200:
                    return True

                # Si nos devuelve 403, significa que la API key es incorrecta y nos da un error de login
                if response.status_code == 403:
                    print("API key rechazada. Verifica que sea correcta.")
                    return False

            except requests.ConnectionError:
                print(f"Intento {intento}/{retries}: OctoPrint no disponible, reintentando en {delay}s...")
            except Exception as e:
                print(f"Intento {intento}/{retries}: Error al conectar con OctoPrint: {e}")

            if intento < retries:
                time.sleep(delay)

        return False

    # Este metodo lo utilizamos para validar que la configuración introducida es correcta
    # Y de no ser así, nos pedirá por consola que introduzcamos los datos correctos
    def validate_configuration(self):

        # Comprobamos si no hay una url ya y pedimos que la introduzca el usuario
        if not self.check_octoprint_url():
            while True:
                new_url = input("URL de OctoPrint (ej: http://localhost): ").strip()
                if new_url:
                    self.octoprint_url = new_url
                    break
                print("La URL no puede estar vacía.")

        # Lo mismo pero con la API Key
        if not self.check_api_key():
            while True:
                new_key = getpass.getpass("API key de OctoPrint (Settings > API): ").strip()
                if new_key:
                    self.api_key = new_key
                    break
                print("La API key no puede estar vacía.")

        # Utilizamos el método de antes para comprobar si los datos introducidos son correctos
        print(f"Comprobando conexión con OctoPrint en {self.octoprint_url}...")
        if not self.check_connection():
            print("No se pudo conectar a OctoPrint. Verifica que:")
            print("  1. El servicio esté activo: sudo systemctl status octoprint")
            print("  2. La API key sea correcta (Settings > API en OctoPrint)")
            return False

        print("Conexión con OctoPrint validada correctamente.")

        # En caso de qeu esten bien, los guardamos en las variables correspodientes de nuestro fichero .env
        set_key(self.env_path, "OCTOPRINT_URL", self.octoprint_url)
        set_key(self.env_path, "OCTOPRINT_API_KEY", self.api_key)
        load_dotenv(dotenv_path=self.env_path, override=True)

        return True

# Creamos la instancia de la clase KeyManagement para poder utilizarla en los demas módulos
key_management = KeyManagement()