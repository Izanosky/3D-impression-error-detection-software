import os
import requests


class OctoPrintClient:
    """Cliente HTTP para la API de OctoPrint."""

    def _get_url(self):
        return os.getenv("OCTOPRINT_URL", "http://localhost")

    def _get_headers(self):
        return {
            "X-Api-Key": os.getenv("OCTOPRINT_API_KEY", ""),
            "Content-Type": "application/json",
        }

    def _request(self, method, endpoint, **kwargs):
        """Ejecuta una petición HTTP a OctoPrint. Devuelve Response o None."""
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

    # Estado de la impresora
    def get_printer_status(self):
        printer_resp = self._request("GET", "/api/printer")
        job_resp = self._request("GET", "/api/job")

        printer_ok = printer_resp and printer_resp.status_code == 200
        job_ok = job_resp and job_resp.status_code == 200

        return {
            "printer": printer_resp.json() if printer_ok else {},
            "job": job_resp.json() if job_ok else {},
            "connected": printer_ok,
        }

    # Control de impresión
    def pause_print(self):
        resp = self._request("POST", "/api/job", json={"command": "pause", "action": "pause"})
        return resp is not None and resp.status_code == 204

    def resume_print(self):
        resp = self._request("POST", "/api/job", json={"command": "pause", "action": "resume"})
        return resp is not None and resp.status_code == 204

    def start_print(self):
        resp = self._request("POST", "/api/job", json={"command": "start"})
        return resp is not None and resp.status_code in (200, 204)

    def cancel_print(self):
        resp = self._request("POST", "/api/job", json={"command": "cancel"})
        return resp is not None and resp.status_code == 204

    # Archivos G-code
    def upload_gcode(self, file_content, filename):
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
        resp = self._request("GET", "/api/files")
        if resp is None or resp.status_code != 200:
            return []

        data = resp.json()
        files = data.get("files", data.get("children", []))

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
        resp = self._request("POST", f"/api/files/local/{filename}", json={"command": "select"})
        return resp is not None and resp.status_code in (200, 204)


octoprint_client = OctoPrintClient()
