"""
Cliente para comunicación con OctoPrint API
"""
import os
import requests


class OctoPrintClient:
    def _get_url(self):
        """Obtiene la URL de OctoPrint desde variables de entorno"""
        return os.getenv("OCTOPRINT_URL", "http://localhost")
    
    def _get_headers(self):
        """Obtiene los headers con la API key para las peticiones"""
        return {
            "X-Api-Key": os.getenv("OCTOPRINT_API_KEY", ""),
            "Content-Type": "application/json"
        }
    
    def get_printer_status(self) -> dict:
        """Obtiene el estado actual de la impresora"""
        base_url = self._get_url()
        headers = self._get_headers()
        
        try:
            # Estado de la impresora
            printer_resp = requests.get(
                f"{base_url}/api/printer",
                headers=headers,
                timeout=10
            )
            printer_data = printer_resp.json() if printer_resp.status_code == 200 else {}
            
            # Estado del trabajo actual
            job_resp = requests.get(
                f"{base_url}/api/job",
                headers=headers,
                timeout=10
            )
            job_data = job_resp.json() if job_resp.status_code == 200 else {}
            
            return {
                "printer": printer_data,
                "job": job_data,
                "connected": printer_resp.status_code == 200
            }
        except Exception as e:
            return {
                "printer": {},
                "job": {},
                "connected": False,
                "error": str(e)
            }
    
    def get_snapshot(self) -> bytes | None:
        """Obtiene una captura de la cámara de OctoPrint"""
        base_url = self._get_url()
        headers = self._get_headers()
        
        try:
            # URL típica de webcam en OctoPrint
            response = requests.get(
                f"{base_url}/webcam/?action=snapshot",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.content
            return None
        except Exception:
            return None
    
    def pause_print(self) -> bool:
        """Pausa la impresión actual"""
        base_url = self._get_url()
        headers = self._get_headers()
        
        try:
            response = requests.post(
                f"{base_url}/api/job",
                headers=headers,
                json={"command": "pause", "action": "pause"},
                timeout=10
            )
            return response.status_code == 204
        except Exception:
            return False
    
    def resume_print(self) -> bool:
        """Reanuda la impresión pausada"""
        base_url = self._get_url()
        headers = self._get_headers()
        
        try:
            response = requests.post(
                f"{base_url}/api/job",
                headers=headers,
                json={"command": "pause", "action": "resume"},
                timeout=10
            )
            return response.status_code == 204
        except Exception:
            return False
    
    def start_print(self) -> bool:
        """Inicia la impresión del archivo seleccionado"""
        base_url = self._get_url()
        headers = self._get_headers()
        
        try:
            response = requests.post(
                f"{base_url}/api/job",
                headers=headers,
                json={"command": "start"},
                timeout=10
            )
            print(f"[OctoPrint] start_print -> status={response.status_code}, body={response.text[:200]}")
            return response.status_code in (200, 204)
        except Exception as e:
            print(f"[OctoPrint] start_print error: {e}")
            return False
    
    def cancel_print(self) -> bool:
        """Cancela la impresión actual"""
        base_url = self._get_url()
        headers = self._get_headers()
        
        try:
            response = requests.post(
                f"{base_url}/api/job",
                headers=headers,
                json={"command": "cancel"},
                timeout=10
            )
            return response.status_code == 204
        except Exception:
            return False
    
    def upload_gcode(self, file_content: bytes, filename: str) -> dict:
        """Sube un archivo G-code a OctoPrint"""
        base_url = self._get_url()
        api_key = os.getenv("OCTOPRINT_API_KEY", "")
        
        try:
            response = requests.post(
                f"{base_url}/api/files/local",
                headers={"X-Api-Key": api_key},
                files={"file": (filename, file_content, "application/octet-stream")},
                data={"select": "true"},
                timeout=30
            )
            if response.status_code == 201:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_files(self) -> list:
        """Lista los archivos G-code disponibles en OctoPrint"""
        base_url = self._get_url()
        headers = self._get_headers()
        
        try:
            # Intentar primero /api/files (lista todo)
            response = requests.get(
                f"{base_url}/api/files",
                headers=headers,
                timeout=10
            )
            print(f"[OctoPrint] list_files -> status={response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"[OctoPrint] list_files keys: {list(data.keys())}")
                
                # OctoPrint puede devolver 'files' o 'children'
                files = data.get("files", data.get("children", []))
                print(f"[OctoPrint] list_files raw count: {len(files)}")
                
                result = []
                for f in files:
                    name = f.get("name", "")
                    print(f"[OctoPrint] file: {name} (type: {f.get('type', 'unknown')})")
                    if name.lower().endswith(('.gcode', '.gco', '.g')):
                        result.append({
                            "name": name,
                            "size": f.get("size", 0),
                            "date": f.get("date", 0),
                            "origin": f.get("origin", "local")
                        })
                
                print(f"[OctoPrint] list_files filtered: {len(result)} G-code files")
                return result
            else:
                print(f"[OctoPrint] list_files error body: {response.text[:300]}")
            return []
        except Exception as e:
            print(f"[OctoPrint] list_files exception: {e}")
            return []
    
    def select_file(self, filename: str) -> bool:
        """Selecciona un archivo para imprimir"""
        base_url = self._get_url()
        headers = self._get_headers()
        
        try:
            response = requests.post(
                f"{base_url}/api/files/local/{filename}",
                headers=headers,
                json={"command": "select"},
                timeout=10
            )
            print(f"[OctoPrint] select_file({filename}) -> status={response.status_code}")
            return response.status_code in (200, 204)
        except Exception as e:
            print(f"[OctoPrint] select_file error: {e}")
            return False


# Instancia global del cliente
octoprint_client = OctoPrintClient()
