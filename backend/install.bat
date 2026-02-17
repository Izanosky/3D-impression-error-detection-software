@echo off
echo === Instalando Backend ===
echo.

REM Verificar que Python 3.10 esta disponible
py -3.10 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.10 no esta instalado o no se encuentra en el PATH.
    echo Instala Python 3.10 desde https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)

REM Mostrar version encontrada
echo Python encontrado:
py -3.10 --version

REM Crear entorno virtual con Python 3.10
if exist ".venv" (
    echo Entorno virtual ya existe. Eliminando para recrear limpio...
    rmdir /s /q .venv
)

echo Creando entorno virtual con Python 3.10...
py -3.10 -m venv .venv
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual.
    pause
    exit /b 1
)

REM Activar entorno virtual
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

REM Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip -q

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERROR: Fallo la instalacion de dependencias.
    pause
    exit /b 1
)

echo.
echo === Backend instalado correctamente! ===
echo.
echo Para ejecutar:
echo   cd backend
echo   .venv\Scripts\activate
echo   uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
pause
