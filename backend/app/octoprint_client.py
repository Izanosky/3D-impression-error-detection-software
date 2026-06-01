"""
Clase para la gestion de las llamadas a la API de OctoPrint
"""

import os
import requests


class OctoPrintClient:

    # Metodo que nos devuelve la url de la API de OctoPrint almacenada en el archivo .env
    def _get_url(self):
        return os.getenv("OCTOPRINT_URL", "http://localhost")

    # Metodo que nos devuelve las cabeceras necesarias para la API de OctoPrint, incluyendo la API key
    def _get_headers(self):
        return {
            "X-Api-Key": os.getenv("OCTOPRINT_API_KEY", ""),
            "Content-Type": "application/json",
        }

    # Funcion auxiliar para hacer peticiones a OctoPrint, concretamente al endpoint especificado en los argumentos
    def _request(self, method, endpoint, **kwargs):
        url = f"{self._get_url()}{endpoint}"
        headers = self._get_headers()
        timeout = kwargs.pop("timeout", 10)

        try:
            return requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
        except Exception as e:
            print(f"[OctoPrint] Error en {method} {endpoint}: {e}")
            return None

    # Metodo que nos devuelve el estado de la impresora
    def obtener_estado_impresora(self):

        # Consultamos los dos endpoints de OctoPrint que necesitamos:
        printer_resp = self._request("GET", "/api/printer")  # Estado fisico: temperaturas, estado de la impresora
        job_resp = self._request("GET", "/api/job")           # Estado del trabajo: archivo, progreso, tiempo restante

        # Comprobamos que la respuesta no sea None (fallo de red) y que el codigo HTTP sea 200 (exito)
        printer_ok = printer_resp and printer_resp.status_code == 200
        job_ok = job_resp and job_resp.status_code == 200

        return {
            # Si la peticion fue correcta parseamos el JSON, si no devolvemos un diccionario vacio
            "printer": printer_resp.json() if printer_ok else {},
            "job": job_resp.json() if job_ok else {},
            # Usamos printer_ok como indicador de si la impresora esta conectada y accesible
            "connected": printer_ok,
        }
    
    #####################################################################################################
    # Funciones para el control de la impresion --------------------------------------------------------#
    #####################################################################################################
    
    # Metodo que pausa la impresion
    def pausar_impresion(self):
        resp = self._request("POST", "/api/job", json={"command": "pause", "action": "pause"})
        return resp is not None and resp.status_code == 204

    # Metodo que reanuda la impresion
    def reanudar_impresion(self):
        resp = self._request("POST", "/api/job", json={"command": "pause", "action": "resume"})
        return resp is not None and resp.status_code == 204

    # Metodo que inicia la impresion
    def iniciar_impresion(self):
        resp = self._request("POST", "/api/job", json={"command": "start"})
        return resp is not None and resp.status_code in (200, 204)

    # Metodo que cancela la impresion
    def cancelar_impresion(self):
        resp = self._request("POST", "/api/job", json={"command": "cancel"})
        return resp is not None and resp.status_code == 204

    #####################################################################################################
    # Funciones para la subida y gestion de archivos G-code ------------------------------------------------
    #####################################################################################################

    # Metodo que sube un archivo G-code a OctoPrint
    def subir_gcode(self, file_content, filename):
        api_key = os.getenv("OCTOPRINT_API_KEY", "")
        try:
            # Hacemos la llamada al endpoint /api/files/local de OctoPrint, pasando como argumentos:
            # - api_key: la clave API de OctoPrint
            # - files: el archivo G-code a subir
            # - data: la seleccion del archivo
            response = requests.post(
                f"{self._get_url()}/api/files/local",
                headers={"X-Api-Key": api_key},
                files={"file": (filename, file_content, "application/octet-stream")},
                data={"select": "true"},
                timeout=30,
            )

            # Comprobamos que la respuesta no sea None y que el codigo HTTP sea 201 (creado)
            if response.status_code == 201:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Metodo que obtiene la lista de los archivos gcode que hay subidos en OctoPrint
    def listar_archivos(self):
        resp = self._request("GET", "/api/files") # Hacemos la llamada al endpoint /api/files de OctoPrint
        
        if resp is None or resp.status_code != 200:
            return []

        # Obtenemos los archivos de la respuesta
        data = resp.json()

        files = data.get("files", data.get("children", [])) # Usamos files si existe, si no usamos children, porque a veces OctoPrint devuelve la lista de archivos en la clave "children"

        # Devolvemos la lista de archivos, filtrando solo los que sean archivos gcode y tengan la extension .gcode, .gco o .g
        return [
            {
                "name": f.get("name", ""), # Nombre del archivo
                "size": f.get("size", 0), # Tamaño del archivo
                "date": f.get("date", 0), # Fecha de creacion del archivo
                "origin": f.get("origin", "local"), # Origen del archivo
            }
            for f in files
            if f.get("name", "").lower().endswith((".gcode", ".gco", ".g")) # Filtramos solo los que sean archivos gcode y tengan la extension .gcode, .gco o .g
        ]

    # Metodo que selecciona un archivo para imprimir
    def seleccionar_archivo(self, filename):
        resp = self._request("POST", f"/api/files/local/{filename}", json={"command": "select"})
        return resp is not None and resp.status_code in (200, 204)

# Instanciamos la clase OctoPrintClient
octoprint_client = OctoPrintClient()
