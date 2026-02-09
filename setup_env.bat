@echo off
echo === Instalando Sistema Completo ===
echo.

echo [1/2] Instalando Backend...
cd backend
call install.bat
cd ..

echo.
echo [2/2] Instalando Frontend...
cd frontend
call install.bat
cd ..

echo.
echo === Instalacion completa! ===
echo.
echo Para ejecutar el sistema:
echo   Terminal 1: cd backend ^&^& .venv\Scripts\activate ^&^& uvicorn app.main:app --host 0.0.0.0 --port 8000
echo   Terminal 2: cd frontend ^&^& npm run dev
