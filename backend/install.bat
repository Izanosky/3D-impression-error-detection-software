@echo off
echo === Instalando Backend ===

REM Crear entorno virtual
if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
)

REM Activar e instalar dependencias
call .venv\Scripts\activate.bat
echo Instalando dependencias...
pip install -r requirements.txt -q

echo.
echo === Backend listo! ===
echo.
echo Para ejecutar:
echo   .venv\Scripts\activate
echo   uvicorn app.main:app --host 0.0.0.0 --port 8000
