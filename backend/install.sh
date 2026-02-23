#!/bin/bash
echo "=== Instalando Backend ==="
echo

# Verificar que Python 3.10 esta disponible
if ! command -v python3.10 &> /dev/null; then
    echo "ERROR: Python 3.10 no esta instalado o no se encuentra en el PATH."
    echo "Instala Python 3.10 con tu gestor de paquetes, por ejemplo:"
    echo "  sudo apt install python3.10 python3.10-venv"
    exit 1
fi

# Mostrar version encontrada
echo "Python encontrado:"
python3.10 --version

# Crear entorno virtual con Python 3.10
if [ -d ".venv" ]; then
    echo "Entorno virtual ya existe. Eliminando para recrear limpio..."
    rm -rf .venv
fi

echo "Creando entorno virtual con Python 3.10..."
python3.10 -m venv .venv
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo crear el entorno virtual."
    exit 1
fi

# Activar entorno virtual
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo activar el entorno virtual."
    exit 1
fi

# Actualizar pip
echo "Actualizando pip..."
python -m pip install --upgrade pip -q

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "ERROR: Fallo la instalacion de dependencias."
    exit 1
fi

echo
echo "=== Backend instalado correctamente! ==="
echo
echo "Para ejecutar:"
echo "  cd backend"
echo "  source .venv/bin/activate"
# echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo
