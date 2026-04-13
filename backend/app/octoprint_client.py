"""
Cliente HTTP para comunicación con la API de OctoPrint.

Encapsula todas las llamadas a la API REST de OctoPrint:
estado de impresora, gestión de archivos G-code, control de
impresión (pausar, reanudar, cancelar), y timelapses.
"""
import os
import requests
from app.config import WEBCAM_SNAPSHOT_URL


class OctoPrintClient:
    """Cliente que centraliza todas las peticiones HTTP a OctoPrint."""

    # ═══════════════════════════════════════════════════════
    #  Helpers internos
    # ═══════════════════════════════════════════════════════

    def _get_url(self):
        """Devuelve la URL base de OctoPrint."""
        return os.getenv("OCTOPRINT_URL", "http://localhost")

    def _get_headers(self):
        """Devuelve los headers con la API key."""
        return {
            "X-Api-Key": os.getenv("OCTOPRINT_API_KEY", ""),
            "Content-Type": "application/json",
        }

    def _request(self, method, endpoint, **kwargs):
        """
        Helper que ejecuta una petición HTTP a OctoPrint.
        Centraliza la construcción de URL + headers + manejo de errores
        para evitar repetir el mismo try/except en cada método.

        Parámetros:
          method   — "GET", "POST" o "DELETE"
          endpoint — ruta relativa (ej: "/api/printer")
          **kwargs — argumentos extra para requests (json, files, timeout, etc.)

        Devuelve el objeto Response o None si falla.
        """
        url = f"{self._get_url()}{endpoint}"
        headers = self._get_headers()
        timeout = kwargs.pop("timeout", 10)

        try:
            return requests.request(
                method, url, headers=headers, timeout=timeout, **kwargs
            )
        except Exception as e:
            print(f"[OctoPrint] Error en {method} {endpoint}: {e}")
            return None

    # ═══════════════════════════════════════════════════════
    #  Estado de la impresora
    # ═══════════════════════════════════════════════════════

    def get_printer_status(self):
        """
        Obtiene el estado actual de la impresora y del trabajo en curso.
        Devuelve un diccionario con claves: printer, job, connected.
        """
        printer_resp = self._request("GET", "/api/printer")
        job_resp = self._request("GET", "/api/job")

        printer_ok = printer_resp and printer_resp.status_code == 200
        job_ok = job_resp and job_resp.status_code == 200

        return {
            "printer": printer_resp.json() if printer_ok else {},
            "job": job_resp.json() if job_ok else {},
            "connected": printer_ok,
        }

    def get_snapshot(self):
        """Obtiene una captura JPEG de la cámara. Devuelve bytes o None."""
        try:
            response = requests.get(WEBCAM_SNAPSHOT_URL, timeout=10)
            return response.content if response.status_code == 200 else None
        except Exception:
            return None

    # ═══════════════════════════════════════════════════════
    #  Control de impresión
    # ═══════════════════════════════════════════════════════

    def pause_print(self):
        """Pausa la impresión actual."""
        resp = self._request("POST", "/api/job", json={"command": "pause", "action": "pause"})
        return resp is not None and resp.status_code == 204

    def resume_print(self):
        """Reanuda la impresión pausada."""
        resp = self._request("POST", "/api/job", json={"command": "pause", "action": "resume"})
        return resp is not None and resp.status_code == 204

    def start_print(self):
        """Inicia la impresión del archivo seleccionado."""
        resp = self._request("POST", "/api/job", json={"command": "start"})
        return resp is not None and resp.status_code in (200, 204)

    def cancel_print(self):
        """Cancela la impresión actual."""
        resp = self._request("POST", "/api/job", json={"command": "cancel"})
        return resp is not None and resp.status_code == 204

    # ═══════════════════════════════════════════════════════
    #  Gestión de archivos G-code
    # ═══════════════════════════════════════════════════════

    def upload_gcode(self, file_content, filename):
        """Sube un archivo G-code a OctoPrint. Devuelve {success, data/error}."""
        api_key = os.getenv("OCTOPRINT_API_KEY", "")
        try:
            response = requests.post(
                f"{self._get_url()}/api/files/local",
                headers={"X-Api-Key": api_key},
                files={"file": (filename, file_content, "application/octet-stream")},
                data={"select": "true"},
                timeout=30,
            )
            if response.status_code == 201:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_files(self):
        """Lista los archivos G-code disponibles en OctoPrint."""
        resp = self._request("GET", "/api/files")
        if resp is None or resp.status_code != 200:
            return []

        data = resp.json()
        files = data.get("files", data.get("children", []))

        # Filtrar solo archivos G-code
        return [
            {
                "name": f.get("name", ""),
                "size": f.get("size", 0),
                "date": f.get("date", 0),
                "origin": f.get("origin", "local"),
            }
            for f in files
            if f.get("name", "").lower().endswith((".gcode", ".gco", ".g"))
        ]

    def select_file(self, filename):
        """Selecciona un archivo G-code para imprimir."""
        resp = self._request("POST", f"/api/files/local/{filename}", json={"command": "select"})
        return resp is not None and resp.status_code in (200, 204)

    # ═══════════════════════════════════════════════════════
    #  Timelapses
    # ═══════════════════════════════════════════════════════

    def list_timelapses(self):
        """Lista los timelapses disponibles en OctoPrint."""
        resp = self._request("GET", "/api/timelapse")
        if resp is None or resp.status_code != 200:
            return []

        return [
            {
                "name": f.get("name", ""),
                "size": f.get("bytes", f.get("size", 0)),
                "date": f.get("date", ""),
                "url": f.get("url", ""),
                "thumbnail": f.get("thumbnail", ""),
            }
            for f in resp.json().get("files", [])
        ]

    def download_timelapse(self, filename):
        """Descarga un timelapse de OctoPrint. Devuelve bytes o None."""
        resp = self._request("GET", f"/downloads/timelapse/{filename}", timeout=60, stream=True)
        if resp is not None and resp.status_code == 200:
            return resp.content
        return None

    def delete_timelapse(self, filename):
        """Elimina un timelapse de OctoPrint."""
        resp = self._request("DELETE", f"/api/timelapse/{filename}")
        return resp is not None and resp.status_code == 204


# Instancia global del cliente (usada en main.py)
octoprint_client = OctoPrintClient()
