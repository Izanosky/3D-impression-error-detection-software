@echo off
echo === Entorno TFG ===

REM Comprobar si el entorno virtual ya existe
if exist "backend\.venv\Scripts\activate.bat" (
    echo Entorno virtual detectado. Activando...
    call backend\.venv\Scripts\activate.bat
    echo.
    echo === Entorno activado! ===
    echo.
    echo Comandos disponibles:
    echo   Backend:  cd backend ^&^& uvicorn app.main:app --reload
    echo   Frontend: cd frontend ^&^& npm run dev
) else (
    echo Entorno virtual no encontrado. Creando...
    echo.
    
    echo [1/4] Creando entorno virtual del backend...
    "C:\Users\izanj\AppData\Local\Programs\Python\Python310\python.exe" -m venv backend\.venv
    
    echo [2/4] Instalando dependencias del backend...
    backend\.venv\Scripts\python.exe -m pip install --upgrade pip -q
    backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -q
    
    echo [3/4] Instalando dependencias del frontend...
    cd frontend
    call npm install
    cd ..
    
    echo [4/4] Activando entorno...
    call backend\.venv\Scripts\activate.bat
    
    echo.
    echo === Entorno creado y activado! ===
    echo.
    echo Para iniciar el sistema:
    echo   1. Backend:  cd backend ^&^& uvicorn app.main:app --reload
    echo   2. Frontend: cd frontend ^&^& npm run dev
)
