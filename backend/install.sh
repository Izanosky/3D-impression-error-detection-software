#!/bin/bash
echo "=== Instalando Backend ==="
echo

# Buscar Python 3 disponible (3.10, 3.11, 3.12...)
PYTHON_CMD=""
for cmd in python3.10 python3.11 python3.12 python3; do
    if command -v $cmd &> /dev/null; then
        PYTHON_CMD=$cmd
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: Python 3 no esta instalado o no se encuentra en el PATH."
    echo "Instala Python 3 con tu gestor de paquetes, por ejemplo:"
    echo "  sudo apt install python3 python3-venv"
    exit 1
fi

# Mostrar version encontrada
echo "Python encontrado:"
$PYTHON_CMD --version

# Crear entorno virtual
if [ -d ".venv" ]; then
    echo "Entorno virtual ya existe. Eliminando para recrear limpio..."
    rm -rf .venv
fi

echo "Creando entorno virtual con $PYTHON_CMD (--system-site-packages)..."
$PYTHON_CMD -m venv --system-site-packages .venv
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo crear el entorno virtual."
    echo "Prueba: sudo apt install python3-venv"
    exit 1
fi

# Activar entorno virtual
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo activar el entorno virtual."
    exit 1
fi

# Instalar dependencias del sistema necesarias que causan fallos de memoria si se complian
echo "Instalando paquetes del sistema precompilados de Python para evitar la compilacion y fallo de memoria (Segmentation fault)..."
echo "Esto puede pedirte contraseña para sudo..."
sudo apt install -y python3-scipy python3-numpy 2>/dev/null || echo "AVISO: No se pudieron instalar scipy nativo. Si la instalación falla, ejecuta: sudo apt install python3-scipy"

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
