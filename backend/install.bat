@echo off
echo === Instalando Backend ===

REM Verificar que Python 3.10 esta disponible
py -3.10 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.10 no esta instalado o no se encuentra en el PATH.
    echo Instala Python 3.10 desde https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Crear entorno virtual con Python 3.10
if not exist ".venv" (
    echo Creando entorno virtual con Python 3.10...
    py -3.10 -m venv .venv
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
