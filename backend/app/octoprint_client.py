"""
Cliente para comunicación con OctoPrint API
"""
import httpx
from .config import get_setting


class OctoPrintClient:
    def _get_url(self):
        """Obtiene la URL de OctoPrint de la configuración"""
        return get_setting("octoprint_url")
    
    def _get_headers(self):
        """Obtiene los headers con la API key actual"""
        return {
            "X-Api-Key": get_setting("octoprint_api_key"),
            "Content-Type": "application/json"
        }
    
    async def get_printer_status(self) -> dict:
        """Obtiene el estado actual de la impresora"""
        base_url = self._get_url()
        headers = self._get_headers()
        
        async with httpx.AsyncClient() as client:
            try:
                # Estado de la impresora
                printer_resp = await client.get(
                    f"{base_url}/api/printer",
                    headers=headers,
                    timeout=10.0
                )
                printer_data = printer_resp.json() if printer_resp.status_code == 200 else {}
                
                # Estado del trabajo actual
                job_resp = await client.get(
                    f"{base_url}/api/job",
                    headers=headers,
                    timeout=10.0
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
    
    async def get_snapshot(self) -> bytes | None:
        """Obtiene una captura de la cámara de OctoPrint"""
        base_url = self._get_url()
        headers = self._get_headers()
        
        async with httpx.AsyncClient() as client:
            try:
                # URL típica de webcam en OctoPrint
                response = await client.get(
                    f"{base_url}/webcam/?action=snapshot",
                    headers=headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.content
                return None
            except Exception:
                return None
    
    async def pause_print(self) -> bool:
        """Pausa la impresión actual"""
        base_url = self._get_url()
        headers = self._get_headers()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{base_url}/api/job",
                    headers=headers,
                    json={"command": "pause", "action": "pause"},
                    timeout=10.0
                )
                return response.status_code == 204
            except Exception:
                return False
    
    async def resume_print(self) -> bool:
        """Reanuda la impresión pausada"""
        base_url = self._get_url()
        headers = self._get_headers()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{base_url}/api/job",
                    headers=headers,
                    json={"command": "pause", "action": "resume"},
                    timeout=10.0
                )
                return response.status_code == 204
            except Exception:
                return False


# Instancia global del cliente
octoprint_client = OctoPrintClient()
