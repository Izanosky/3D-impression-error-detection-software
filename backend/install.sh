#!/bin/bash

# ============================================================
#  Colores y utilidades
# ============================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

step()  { echo -e "\n${CYAN}${BOLD}▶ $1${NC}"; }
ok()    { echo -e "${GREEN}✔ $1${NC}"; }
warn()  { echo -e "${YELLOW}⚠ $1${NC}"; }
err()   { echo -e "${RED}✘ $1${NC}"; exit 1; }

# Muestra tiempo transcurrido desde $1 (epoch)
elapsed() {
    local secs=$(( $(date +%s) - $1 ))
    printf "%dm %ds" $(( secs/60 )) $(( secs%60 ))
}

TOTAL_START=$(date +%s)

echo -e "${BOLD}╔══════════════════════════════════════╗"
echo -e "║       Instalando Backend             ║"
echo -e "╚══════════════════════════════════════╝${NC}"

# ============================================================
#  1. Buscar Python 3
# ============================================================
step "Buscando Python 3..."
PYTHON_CMD=""
for cmd in python3.12 python3.11 python3.10 python3; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON_CMD=$cmd
        break
    fi
done
[ -z "$PYTHON_CMD" ] && err "Python 3 no encontrado. Instálalo con: sudo apt install python3 python3-venv"
ok "Usando: $PYTHON_CMD ($($PYTHON_CMD --version 2>&1))"

# ============================================================
#  2. Entorno virtual
# ============================================================
step "Preparando entorno virtual..."
if [ -d ".venv" ]; then
    warn "Entorno virtual existente detectado — eliminando para reconstruir limpio..."
    rm -rf .venv
fi

echo "  Creando .venv con --system-site-packages..."
$PYTHON_CMD -m venv --system-site-packages .venv \
    || err "No se pudo crear el entorno virtual. Prueba: sudo apt install python3-venv"
ok "Entorno virtual creado"

source .venv/bin/activate \
    || err "No se pudo activar el entorno virtual"
ok "Entorno virtual activado: $(which python)"

# ============================================================
#  3. Configurar piwheels (wheels ARM precompilados — Raspberry Pi Foundation)
# ============================================================
step "Configurando piwheels (binarios ARM, evita compilar C++)..."
PIP_CONF="${HOME}/.config/pip/pip.conf"
mkdir -p "$(dirname "$PIP_CONF")"
if grep -q "piwheels" "$PIP_CONF" 2>/dev/null; then
    ok "piwheels ya estaba configurado en $PIP_CONF"
else
    cat >> "$PIP_CONF" <<EOF

[global]
extra-index-url=https://www.piwheels.org/simple
EOF
    ok "piwheels añadido a $PIP_CONF"
fi

# ============================================================
#  4. Paquetes del sistema (evita compilar numpy y opencv)
# ============================================================
step "Instalando paquetes del sistema precompilados (evita compilar C++)..."
warn "Esto puede pedirte la contraseña sudo..."

SYS_PKGS=(python3-numpy python3-opencv python3-av ffmpeg)
for pkg in "${SYS_PKGS[@]}"; do
    echo -n "  Instalando $pkg... "
    if sudo apt install -y "$pkg" &>/dev/null; then
        echo -e "${GREEN}✔${NC}"
    else
        echo -e "${YELLOW}no disponible (se instalará con pip)${NC}"
    fi
done

# ============================================================
#  5. Actualizar pip
# ============================================================
step "Actualizando pip..."
python -m pip install --upgrade pip \
    || warn "No se pudo actualizar pip, continuando con la versión actual"
ok "pip: $(pip --version)"

# ============================================================
#  6. Instalar dependencias una a una con tiempos
# ============================================================
step "Instalando dependencias desde requirements.txt..."

if [ ! -f requirements.txt ]; then
    err "No se encontró requirements.txt en el directorio actual ($(pwd))"
fi

# Filtra líneas vacías y comentarios
PACKAGES=$(grep -v '^\s*#' requirements.txt | grep -v '^\s*$')
TOTAL_PKGS=$(echo "$PACKAGES" | wc -l)
CURRENT=0
FAILED=()

echo "  Total de paquetes: ${BOLD}$TOTAL_PKGS${NC}"
echo ""

while IFS= read -r pkg; do
    [ -z "$pkg" ] && continue
    CURRENT=$(( CURRENT + 1 ))
    PKG_START=$(date +%s)

    printf "  [%2d/%2d] %-40s " "$CURRENT" "$TOTAL_PKGS" "$pkg"

    # Instalación con output visible si falla
    if pip install "$pkg" --prefer-binary -q 2>/tmp/pip_err; then
        PKG_TIME=$(elapsed $PKG_START)
        echo -e "${GREEN}✔${NC} (${PKG_TIME})"
    else
        PKG_TIME=$(elapsed $PKG_START)
        echo -e "${RED}✘ FALLÓ${NC} (${PKG_TIME})"
        echo -e "    ${RED}$(cat /tmp/pip_err | tail -3)${NC}"
        FAILED+=("$pkg")
    fi
done <<< "$PACKAGES"

# ============================================================
#  7. Resumen final
# ============================================================
echo ""
echo -e "${BOLD}══════════════════════════════════════${NC}"
TOTAL_TIME=$(elapsed $TOTAL_START)
echo -e "  Tiempo total: ${BOLD}${TOTAL_TIME}${NC}"

if [ ${#FAILED[@]} -eq 0 ]; then
    echo -e "${GREEN}${BOLD}  ✔ Backend instalado correctamente${NC}"
else
    warn "  Los siguientes paquetes fallaron:"
    for f in "${FAILED[@]}"; do
        echo -e "    ${RED}• $f${NC}"
    done
    echo ""
    warn "  Puedes intentar instalarlos manualmente con:"
    echo "    source .venv/bin/activate"
    for f in "${FAILED[@]}"; do
        echo "    pip install $f --prefer-binary"
    done
fi

echo ""
echo -e "${BOLD}  Para ejecutar el backend:${NC}"
echo "    cd backend"
echo "    source .venv/bin/activate"
echo "    uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo -e "${BOLD}══════════════════════════════════════${NC}"